
import os
import tempfile

from osgeo import gdal 


class Band:

    CUTLINE_LAYER_NAME = 'aoi'

    def __init__(self, name, aoi, paths, metadata):
        self.name = name
        self.aoi = aoi
        self.paths = paths
        self.metadata = metadata

        self.out_path = None
        self.nd_value = None
        self.pixel_size = None

        self._clip_paths = None
        self._cutline_path = None

    def create(self, pixel_size):
        self._init_create(pixel_size)
        self._clip_paths_by_aoi()
        self._merge_clipped_paths()

    def _init_create(self, pixel_size):
        self._set_pixel_size(pixel_size)
        self._set_nd_value()
        self._write_cutline()

    def _set_pixel_size(self, pixel_size):
        self.pixel_size = pixel_size

    def _set_nd_value(self):
        rast = gdal.Open(self.paths[0])
        self.nd_value = rast.GetRasterBand(1).GetNoDataValue()
        rast = None 

    def _write_cutline(self):
        self._cutline_path = tempfile.mkstemp(suffix='.gpkg')[1]

        # I was getting "DriverError: A file system object called {} already exists." caused by the tempfile existing when 
        # trying to write the aoi to a gpkg file.  This error persisted when setting mode='w'.  Deleting the file allows 
        # the .gpkg file to be written.
        self._delete_file(self._cutline_path)
        self.aoi.to_file(self._cutline_path, layer=self.CUTLINE_LAYER_NAME, driver='GPKG')

    def _clip_paths_by_aoi(self):
        self._clip_paths = [self._clip_path_by_aoi(path) for path in self.paths]

    def _clip_path_by_aoi(self, path):
        out_path = tempfile.mkstemp(suffix='.tif')[1]
        gdal.Warp(
            out_path,
            path,
            dstSRS=self.aoi.crs.to_wkt(),
            cutlineDSName=self._cutline_path,
            cutlineLayer=self.CUTLINE_LAYER_NAME,
            xRes=self.pixel_size[0],
            yRes=self.pixel_size[1],
            outputBounds=self.aoi.total_bounds,
            srcNodata=self.nd_value,
            dstNodata=self.nd_value
        )
        return out_path

    def _merge_clipped_paths(self):
        if (len(self.paths) > 0):
            self.out_path = tempfile.mkstemp(suffix='.tif')[1]
            cmd = f'gdal_merge.py -n {self.nd_value} -a_nodata {self.nd_value} -o {self.out_path} {" ".join(self._clip_paths)}'
            os.system(cmd)
        else:
            self.out_path = self._clip_paths[0]

    def cleanup(self):
        for path in self._clip_paths:
            self._delete_file(path)
        self._delete_file(self._cutline_path)
        self._delete_file(self.out_path)

    def _delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)
        