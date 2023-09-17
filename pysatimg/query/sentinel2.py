
from itertools import groupby
from copy import deepcopy

from .stac import STACQuery
from pysatimg.raster import Raster
from pysatimg.band import Band


class Sentinel2L2AQuery(STACQuery):

    SOURCE_NAME = 'sentinel-2-l2a'

    def __init__(self, aoi, **kwargs):
        super().__init__(
                aoi, 
                self.SOURCE_NAME,
                **kwargs
            )
        
    def build_rasters(self):
        return [self.build_raster(group, items) for group, items in self.group_results_by_date()]
            
    def group_results_by_date(self):
        return groupby(self._results.items(), lambda x: x.datetime.date())
    
    def build_raster(self, date, items):
        bands = self.build_bands(items)
        name = f'{self.SOURCE_NAME}_{date.isoformat()}'
        return Raster(name, bands, self.get_raster_metadata(date))

    def build_bands(self, items):
        settings = self.init_band_settings()
        self.assign_band_paths(settings, items)
        return [Band(band['name'], band['paths'], band) for band in settings]
        
    def init_band_settings(self):
        settings = deepcopy(self.get_source_settings()['bands'])
        for band in settings:
            band['paths'] = []
        return settings
    
    def assign_band_paths(self, settings, items):
        for item in items:
            for band in settings:
                url = item.assets[band['name']].href
                path = f'/vsicurl/{url}'
                band['paths'].append(path)

    def get_raster_metadata(self, date):
        settings = deepcopy(self.get_source_settings())
        settings['date'] = date.isoformat()
        del settings['bands']
        return settings
