import os

import numpy as np

from astropy.io import fits
from scipy.ndimage.measurements import find_objects


def read_fits(path):
    """Read in the FITS file.

    Parameters
    ----------
    path : str
        FITS file

    Returns
    -------
    output_file : astropy.io.fits.hdu.image.PrimaryHDU
        First element of the HDU list
    """
    fl = fits.open(path)
    images = fl[0]
    return images


def create_mask(path):
    """
    Create  a mask with island numbers using breizorro
    Parameters
    -----------
    path: str
        Path to fits image file
    Returns
    --------
    mask: astropy.io.fits.hdu.hdulist.HDUList
       Mask fits file with island numbers
    """
    os.system("breizorro -r {} --number-islands".format(path))


def find_extended_sources(img_data, path2mask, cut=250):
    """
    Find positions of extended sources in the mask
    Paremeters
    ----------
    img_data: numpy.ndarray
       Image data
    path2mask: str
          Path to the mask fits file
    cut: float
      Number that determines if source are extended based on
      flux ratio of the peak and integrated of the regions.
      Default: 250.
    Returns
    --------
    indices: list
         python list with index positions of extended source
    """
    msk_data = read_fits(path2mask).data[0, 0, :, :]
    # Find object in a mask
    objs = find_objects(msk_data.astype(int))
    # Estimate peak and integrated fluxes in the image using objects found in a mask
    peak_flux = []
    int_flux = []
    for i in range(len(objs)):
        peak_flux.append(np.max(img_data[objs[i]]))
        int_flux.append(np.sum(img_data[objs[i]]))
    peak_flux = np.array(peak_flux)
    int_flux = np.array(int_flux)
    ratio = int_flux/peak_flux
    # Find an optimal way to get the ratio
    indx = np.where(ratio > cut)[0]
    # Breizorro start to count from 1
    indx = indx+1
    return indx.tolist()


def mask_extended_sources(path2mask, list_islands):
    """
    Extract islands from mask. Make the mask binary and invert it.
    Parameters
    ---------
    path2mask: str
          Path to the mask fits file
    indices: list
         python list with index positions of extended source
    Returns
    --------
    Inverted binary mask: astropy.io.fits.hdu.hdulist.HDUList
          Fits file image
    """
    outname = path2mask.replace('.mask.fits', '.binary.fits')
    # convert list of islands to string for breizorro to read it
    idn = " ".join(str(idx) for idx in list_islands)
    os.system("breizorro -m {} --extract-islands {} --make-binary --invert -o {}".format(path2mask,
                                                                                         idn,
                                                                                         outname))
    # Remove intermediate mask fits file
    os.remove(path2mask)


def get_image_products(raw_image, path2mask):
    """Get a product of original fits image with the mask
    Parameters
    ----------
    raw_image: astropy.io.fits.hdu.image.PrimaryHDU
        First element of the HDU list
    mask: str
        Path to the inverted binary mask
    Returns
    -------
    prod_images: astropy.io.fits.hdu.hdulist.HDUList
           fits image without extended sources
    """
    msk_data = read_fits(path2mask).data
    img_data = raw_image.data
    outname = path2mask.replace('.binary.fits', '.RES.fits')
    # Product image. Removing extended sources
    p_img_data = raw_image.data * msk_data
    raw_image.data = p_img_data
    raw_image.writeto(outname)
    # Remove intermediate mask fits file
    os.remove(path2mask)
