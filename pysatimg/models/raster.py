
import os
from copy import deepcopy
import json

from osgeo import gdal


class Raster:

    def __init__(self, name, aoi, bands, metadata={}):
        self.name = name
        self.aoi = aoi
        self.bands = bands
        self.metadata = metadata
        
        self.pixel_size = None
        self.out_path = None

    def create(self, pixel_size, out_dir):
        try:
            self.pixel_size = pixel_size
            self._create_bands()
            self._merge_bands(out_dir)
            self._write_metadata(out_dir)
        finally:
            self._cleanup()

    def _create_bands(self):
        for band in self.bands:
            band.create(self.pixel_size)        

    def _merge_bands(self, out_dir):
        self.out_path = f'{out_dir}/{self._get_file_name()}'
        band_paths = [band.out_path for band in self.bands]
        cmd = f'gdal_merge.py -n {self.bands[0].nd_value} -a_nodata {self.bands[0].nd_value} -o \"{self.out_path}\" -separate {" ".join(band_paths)}'
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
        metadata['bands'] = [band.metadata for band in self.bands]
        return metadata

    def _cleanup(self):
        for band in self.bands:
            band.cleanup()
