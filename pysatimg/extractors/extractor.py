
import geopandas as gpd

from ..query.sentinel2 import Sentinel2L2AQuery


class Extractor:

    def __init__(self, source_name, aoi, pixel_size, out_dir, **kwargs):
        self.source_name = source_name
        self.aoi = aoi
        self.pixel_size = pixel_size
        self.out_dir = out_dir
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.bands = kwargs.get('bands')

        self.rasters = None

        self._f_aoi = None
        self._query = None
        

    def extract(self):
        self._format_aoi()
        self._query_source()
        self._create_rasters()

    #
    # AOI formatting
    #

    def _format_aoi(self):
        geom = self.aoi.unary_union
        self._f_aoi = gpd.GeoSeries([geom], crs=self.aoi.crs)

    #
    # Source query
    # 

    def _query_source(self):
        self._query = self._get_source_query_instance()
        self.rasters = self._query.query()

    def _get_source_query_instance(self):
        query_class = self._get_source_query_class()
        return query_class(
            aoi=self.aoi,
            start_date=self.start_date,
            end_date=self.end_date,
            bands=self.bands
        )
        
    def _get_source_query_class(self):
        if self.source_name == 'sentinel-2-l2a':
            return Sentinel2L2AQuery
        
    #
    # Raster creation
    #
        
    def _create_rasters(self):
        for raster in self.rasters:
                raster.create(self.pixel_size, self.out_dir)