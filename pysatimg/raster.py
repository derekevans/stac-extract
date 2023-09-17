
import os

from osgeo import gdal


class Raster:

    def __init__(self, name, bands, metadata):
        self.name = name
        self.bands = bands
        self.metadata = metadata
        
        self._aoi = None
        self._pixel_size = None
        self._out_dir = None

    def create(self, aoi, pixel_size, out_dir):
        self._aoi_path = aoi
        self._pixel_size = pixel_size
        self._out_dir = out_dir

        self.create_bands()
        self.merge_bands()
        self.cleanup()

    def create_bands(self):
        for band in self.bands:
            band.create(self._aoi_path, self._pixel_size)

    def merge_bands(self):
        out_path = f'{self._out_dir}/{self.name}.tif'
        band_paths = [band.out_path for band in self.bands]
        cmd = f'gdal_merge.py -n {self.bands[0].nd_value} -a_nodata {self.bands[0].nd_value} -o \"{out_path}\" -separate {" ".join(band_paths)}'
        print(cmd)
        os.system(cmd)

    def cleanup(self):
        for band in self.bands:
            band.cleanup()
