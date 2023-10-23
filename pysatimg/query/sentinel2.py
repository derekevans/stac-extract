
from itertools import groupby
from copy import deepcopy

from .stac import STACQuery
from pysatimg.models import Raster
from pysatimg.models import Asset


class Sentinel2L2AQuery(STACQuery):

    SOURCE_NAME = 'sentinel-2-l2a'

    def __init__(self, aoi, **kwargs):
        super().__init__(
                aoi, 
                self.SOURCE_NAME,
                **kwargs
            )
        
    def _build_rasters(self):
        return [self._build_raster(group, items) for group, items in self._group_results_by_date()]
            
    def _group_results_by_date(self):
        return groupby(self._results.items(), lambda x: x.datetime.date())
    
    def _build_raster(self, date, items):
        assets = self._build_assets(items)
        name = f'{self.SOURCE_NAME}_{date.isoformat()}'
        return Raster(name, self.aoi, assets, self._get_raster_metadata(date))

    def _get_raster_metadata(self, date):
        config = deepcopy(self._source_config)
        config['date'] = date.isoformat()
        del config['assets']
        return config
