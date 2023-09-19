
from pysatimg.sources import SourceLoader


class Query:

    def __init__(self, aoi, source_name, **kwargs):
        self.aoi = aoi
        self.source_name = source_name
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.bands = kwargs.get('bands')

        self._source_config = None
        self._results = None
    
    def query(self):
        self._set_results()
        return self._build_rasters()
    
    def _set_results(self):
        self._set_source_config()

    def _set_source_config(self):
        self._source_config = SourceLoader(self.source_name).load()
        
    def _build_rasters(self):
        pass 

    