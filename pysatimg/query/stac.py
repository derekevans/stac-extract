
import pystac_client

from pysatimg import SOURCE_SETTINGS
from .query import Query


class STACQuery(Query):

    def __init__(self, aoi, source_name, **kwargs):
        super().__init__(aoi, **kwargs)
        self.source_name = source_name

        self._results = None
        
    def query(self):
        self.set_results()
        return self.build_rasters()

    def set_results(self):
        self._results = self.get_catalog().search(
            collections=[self.get_collection()],
            intersects=self.format_aoi(),
            datetime=self.format_date()
        )

    def get_collection(self):
        return self.get_source_settings()['collection']

    def get_source_settings(self):
        return SOURCE_SETTINGS[self.source_name]

    def get_catalog(self):
        return pystac_client.Client.open(self.get_url())
    
    def get_url(self):
        return self.get_source_settings()['url']
    
    def format_aoi(self):
        return self.aoi.to_crs(4326).unary_union
    
    def format_date(self):
        return f"{self.start_date.isoformat()}/{self.end_date.isoformat()}"
    
    def build_rasters(self):
        pass