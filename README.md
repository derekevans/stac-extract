
# stac-extract

A python package for extracting raster data for an area of interest from the SpatioTemporal Asset Catalogs (STAC).

## Usage

```python
import stacext
import geopandas as gpd
from datetime import date
from shapely.geometry import box

# Create the area of interest (AOI) which can be a gpd.GeoSeries or gpd.GeoDataFrame
# This can also be loaded from a file (.shp, .gpkg, etc.) using gpd.read_file
polygon = box(306040, 4431910, 306830, 4432720)
aoi = gpd.GeoSeries(polygon, crs="EPSG:32616")

# Generate multiband rasters in the AOI with red, green, and blue bands (in that order) from Sentinel-2 L2A for each available date in the date range
extractor = stacext.Extractor(
    source_name='sentinel-2-l2a', 
    aoi=aoi, 
    pixel_size=(10, -10), 
    resample_method='bilinear',
    out_dir='/path/to/output/rasters', 
    start_date=date(2023,7,4), 
    end_date=date(2023, 7,7), 
    assets=['red', 'green', 'blue'],
    n_threads=4
)
extractor.extract()
```

From the command line:
```sh
stac_extract.py --aoi /path/to/input/aoi.shp --source sentinel-2-l2a --pixel_x 10 --pixel_y -10 --resample_method bilinear --start_date 2023-07-04 --end_date 2023-07-07 -a red -a green -a blue --n_threads 4 --out_dir /path/to/output/rasters
```

### Sources

List all available sources:

```python
import stacext

sources = stacext.Sources()
sources.pprint()
```

From the command line:

```sh
stac_sources.py
```

## Development

To install the development environment for this package, you first need to have Docker Desktop installed.  Once installed:

```sh
git clone https://github.com/derekevans/stac-extract
cd stac-extract
make docker/build
make docker/start
make docker/attach
cd stac-extract
make install
```

### Jupyter Lab
To install Jupyter Lab and start the Jupyter server:

```sh
cd stac-extract
make docker/attach
cd stac-extract
make jupyter/install
make jupyter/start/dev
```

Once started, you can access Jupyter Lab on http://localhost:8889/lab

## TODO:
1. Add docstrings and function annotations
2. Write tests
3. Suppress GDAL output b/c it effects progress bar
4. Add additional sources