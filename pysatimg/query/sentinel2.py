
from itertools import groupby
from copy import deepcopy

from .stac import STACQuery
from pysatimg.models import Raster
from pysatimg.models import Band


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
        bands = self._build_bands(items)
        name = f'{self.SOURCE_NAME}_{date.isoformat()}'
        return Raster(name, self.aoi, bands, self._get_raster_metadata(date))
    
    def _build_bands(self, items):
        settings = self._init_band_settings()
        self._assign_band_paths(settings, items)
        return [Band(band['name'], self.aoi, band['paths'], band) for band in settings]
        
    def _init_band_settings(self):
        settings = deepcopy(self._source_config['bands'])
        for band in settings:
            band['paths'] = []
        
        if self.bands is not None:
            settings = list(filter(lambda band: band['name'] in self.bands, settings))
            
        return settings
    
    def _assign_band_paths(self, settings, items):
        for item in items:
            for band in settings:
                url = item.assets[band['name']].href
                path = f'/vsicurl/{url}'
                band['paths'].append(path)

    def _get_raster_metadata(self, date):
        config = deepcopy(self._source_config)
        config['date'] = date.isoformat()
        del config['bands']
        return config
