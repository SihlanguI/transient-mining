from setuptools import setup

setup(
    name='transientmining',
    version='0.1.0',    
    description='A package that mines MeerKAT data and search for transient',
    url='https://github.com/SihlanguI/transientmining.git',
    author='Isaac Sihlangu',
    author_email='isihlangu@sarao.ac.za',
    packages=['transientmining'],
    install_requires=['astropy',
                      'numpy',
                      'scipy',
                      'breizorro',
                      ],
    scripts=[
              'scripts/remove_extendedsoures.py'
            ]
)








