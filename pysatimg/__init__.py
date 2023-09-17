
import os
import json
from osgeo import gdal

def _read_source_settings():
    sources_path = f'{os.path.dirname(__file__)}/settings/sources.json'
    with open(sources_path, 'r') as f:
        return json.loads(f.read())

SOURCE_SETTINGS = _read_source_settings()

gdal.UseExceptions()
