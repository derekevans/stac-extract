
import os
from copy import deepcopy
import json

from osgeo import gdal


class Raster:

    def __init__(self, name, aoi, assets, metadata={}):
        self.name = name
        self.aoi = aoi
        self.assets = assets
        self.metadata = metadata
        
        self.pixel_size = None
        self.out_path = None

    def create(self, pixel_size, out_dir):
        try:
            self.pixel_size = pixel_size
            self._create_assets()
            self._merge_assets(out_dir)
            self._write_metadata(out_dir)
        finally:
            self._cleanup()

    def _create_assets(self):
        for asset in self.assets:
            asset.create(self.pixel_size)        

    def _merge_assets(self, out_dir):
        self.out_path = f'{out_dir}/{self._get_file_name()}'
        asset_paths = [asset.out_path for asset in self.assets]
        cmd = f'gdal_merge.py -n {self.assets[0].nd_value} -a_nodata {self.assets[0].nd_value} -o \"{self.out_path}\" -separate {" ".join(asset_paths)}'
        os.system(cmd)

    def _get_file_name(self):
        return f'{self.name}.tif'
    
    def _write_metadata(self, out_dir):
        out_path = f'{out_dir}/{self.name}.json'
        text = json.dumps(self.get_metadata(), indent=4)
        with open(out_path, 'w') as file:
            file.write(text)

    def get_metadata(self):
        metadata = deepcopy(self.metadata)
        metadata['file_name'] = self._get_file_name()
        metadata['assets'] = [asset.metadata for asset in self.assets]
        return metadata

    def _cleanup(self):
        for asset in self.assets:
            asset.cleanup()
