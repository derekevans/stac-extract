
from distutils.core import setup
from setuptools import find_packages

setup(
    name='stac-extract',
    version='0.0.1',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy>=1.24.0',
        'geopandas==0.14.0',
        'pyyaml',
        'pystac-client',

        # If you get ImportError: cannot import name '_gdal_array' from 'osgeo', try to reinstall GDAL using the following:
        # pip install --no-build-isolation --no-cache-dir --force-reinstall GDAL==3.7.2 
        'GDAL==3.7.2',

        'alive_progress',
        'netCDF4==1.6.5',
        'xarray==2024.1.1',
        'rioxarray==0.15.1'
    ],
    python_requires='>=3.10.0',
    scripts=[
        './scripts/stac_extract.py',
        './scripts/stac_sources.py'
    ]
)