
import os
import tempfile

from osgeo import gdal 


class Band:

    CUTLINE_LAYER_NAME = 'aoi'

    def __init__(self, name, paths, metadata):
        self.name = name
        self.paths = paths
        self.metadata = metadata

        self.out_path = None
        self.nd_value = None

        self._clip_paths = []
        self._aoi = None
        self._pixel_size = None
        self._cutline_path = None

    def create(self, aoi, pixel_size):
        self._aoi = aoi
        self._pixel_size = pixel_size

        self.set_nd_value()
        self.clip_paths()
        self.merge_clipped_paths()

    def set_nd_value(self):
        rast = gdal.Open(self.paths[0])
        self.nd_value = rast.GetRasterBand(1).GetNoDataValue()
        rast = None 

    def clip_paths(self):
        self.write_cutline()
        self._clip_paths = [self.clip_path(path) for path in self.paths]


    def clip_path(self, path):
        clip_path = tempfile.mkstemp(suffix='.tif')[1]
        gdal.Warp(
            clip_path,
            path,
            dstSRS=self._aoi.crs.to_wkt(),
            cutlineDSName=self._cutline_path,
            cutlineLayer=self.CUTLINE_LAYER_NAME,
            xRes=self._pixel_size[0],
            yRes=self._pixel_size[1],
            outputBounds=self._aoi.total_bounds,
            srcNodata=self.nd_value,
            dstNodata=self.nd_value
        )
        return clip_path

    def write_cutline(self):
        handle, self._cutline_path = tempfile.mkstemp(suffix='.gpkg')

        # I was getting an error due to the tempfile existing when trying to write the aoi to a gpkg file.  
        # The specifice error was "DriverError: A file system object called already exists."
        # This error persisted when setting mode='w'.  Deleting the file allowed the .gpkg file to be written.
        self.delete_file(self._cutline_path)
        self._aoi.to_file(self._cutline_path, layer=self.CUTLINE_LAYER_NAME, driver='GPKG')

    def merge_clipped_paths(self):
        if (len(self.paths) > 0):
            self.out_path = tempfile.mkstemp(suffix='.tif')[1]
            cmd = f'gdal_merge.py -n {self.nd_value} -a_nodata {self.nd_value} -o {self.out_path} {" ".join(self._clip_paths)}'
            print(cmd)
            os.system(cmd)
        else:
            self.out_path = self._clip_paths[0]

    def cleanup(self):
        for path in self._clip_paths:
            self.delete_file(path)
        self.delete_file(self._cutline_path)
        self.delete_file(self.out_path)

    def delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        