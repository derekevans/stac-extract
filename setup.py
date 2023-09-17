
from distutils.core import setup

setup(
    name='pysatimg',
    version='0.0.1',
    packages=['pysatimg'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy==1.26.0',
        'geopandas==0.14.0',

        # If you get ImportError: cannot import name '_gdal_array' from 'osgeo', try to reinstall GDAL using the following:
        # pip install --no-build-isolation --no-cache-dir --force-reinstall GDAL==3.7.2 
    
        'GDAL==3.7.2',
        'pystac-client'
    ],
    python_requires='>=3.8.0'
)