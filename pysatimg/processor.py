
import geopandas as gpd

from query.sentinel2 import Sentinel2L2AQuery


class Processor:

    def __init__(self, source_name, aoi, pixel_size, **kwargs):
        self.source_name = source_name
        self.aoi = aoi
        self.pixel_size = pixel_size
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('stop_date')

        self._f_aoi = None
        self._query = None
        self._rasters = None
        

    def process(self):
        self.format_aoi()
        self.query_source()
        self.create_rasters()

    #
    # AOI formatting
    #

    def format_aoi(self):
        geom = self.aoi.unary_union
        self._f_aoi = gpd.GeoSeries([geom], crs=self.aoi.crs)

    #
    # Source query
    # 

    def query_source(self):
        self._query = self.get_source_query_instance()
        self._rasters = self._query.query()

    def get_source_query_instance(self):
        query_class = self.get_source_query_class()
        return query_class(
            aoi=self.aoi,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
    def get_source_query_class(self):
        if self.source_name == 'sentinel-2-l2a':
            return Sentinel2L2AQuery
        
    #
    # Raster creation
    #
        
    def create_rasters(self):
        for raster in self._rasters:
            raster.create()
