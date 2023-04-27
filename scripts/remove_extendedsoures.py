#!/usr/bin/env python3
import argparse
import logging
import os

import remove_extended_sources as res

def initialize_logs():
    """
    Initialize the log settings
    """
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    
def create_parser():
    parser = argparse.ArgumentParser("Input a MeerKAT SDP pipeline continuum image and produce "
                                     "an image with masked extended sources.")
    parser.add_argument('input',
                        help='MeerKAT continuum image fits file')
    parser.add_argument('cut', nargs='?', const=250, type=float,
                       help="Number that determines if source are extended based on flux ratio "
                            "of the peak and integrated of the regions. Default: 250.")
    parser.add_argument('output', nargs='?',
                        help="The output full path plus file name with ''prod.fits'  extension. "
                        "e.g. /home/name/removed_extended_source.fits. Default: same directory as "
                        "the input image.")
    return parser

def main():
    # Initializing the log settings
    initialize_logs()
    logging.info('Masking out extended sources in MeerKAT images.')
    parser = create_parser()
    args = parser.parse_args()
    path = os.path.abspath(args.input)
    outpath = args.output
    cut = args.cut
    if cut is None:
        cut = 250
    logging.info('----------------------------------------')
    logging.info('Read fits file')
    raw_image = res.read_fits(path)
    logging.info('----------------------------------------')
    logging.info('Create a mask with island numbers using breizzoro')
    mask_image = res.create_mask(path)
    logging.info('----------------------------------------')
    logging.info('Mask out extended sources in the fits image')
    path2mask = os.path.splitext(path)[0]+'.mask.fits'
    # List of islands with extended sources
    pos = res.find_extended_sources(raw_image.data[0, 0, :, :], path2mask, cut)
    # Mask out extended sources in the mask
    res.mask_extended_sources(path2mask, pos)
    # Multiplying the original fits image with the mask
    mask_fits = os.path.splitext(path)[0]+'.binary.fits'
    logging.info('Saving the image without extended sources')
    res.get_image_products(raw_image, mask_fits)
    logging.info('------------------DONE-------------------')


if __name__ == "__main__":
    main()