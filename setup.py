
from distutils.core import setup

setup(
    name='stac-extract',
    version='0.0.1',
    packages=[
        'stacext', 
        'stacext.models',
        'stacext.converters'
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy>=1.24.0',
        'geopandas>=1.0.1',
        'pyyaml',
        'pystac-client',
        'GDAL==3.11.0',
        'alive_progress',
        'netCDF4>=1.6.5',
        'xarray>=2024.1.1',
        'rioxarray>=0.15.1'
    ],
    python_requires='>=3.10.0',
    scripts=[
        './scripts/stac_extract.py',
        './scripts/stac_sources.py'
    ]
)