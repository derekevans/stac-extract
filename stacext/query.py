
from itertools import groupby
from copy import deepcopy
import re

import pystac_client

from .models import Raster, Asset


class Query:

    HTTPS_REGEX = '^https:\/\/'
    S3_REGEX = '^s3:\/\/'

    def __init__(self, aoi, source_config, **kwargs):
        self.aoi = aoi
        self.source_config = source_config
        self.start_date = kwargs.get('start_date')
        self.end_date = kwargs.get('end_date')
        self.assets = kwargs.get('assets')

        self._results = None
    
    def query(self):
        self._set_results()
        return self._build_rasters()

    def _set_results(self):
        self._results = self._get_catalog().search(
            collections=[self._get_collection()],
            intersects=self._format_aoi(),
            datetime=self._format_date()
        )

    def _get_collection(self):
        return self.source_config['name']

    def _get_catalog(self):
        return pystac_client.Client.open(self._get_url())
    
    def _get_url(self):
        return self.source_config['url']
    
    def _format_aoi(self):
        return self.aoi.to_crs(4326).unary_union
    
    def _format_date(self):
        return f"{self.start_date.isoformat()}/{self.end_date.isoformat()}"
    
    #
    # Build Rasters
    #
    
    def _build_rasters(self):
        return [self._build_raster(group, items) for group, items in self._group_results_by_date()]
            
    def _group_results_by_date(self):
        return groupby(self._results.items(), lambda x: x.datetime.date())
    
    def _build_raster(self, date, items):
        assets = self._build_assets(items)
        name = f"{self.source_config['name']}_{date.isoformat()}"
        return Raster(name, self.aoi, assets, self._get_raster_metadata(date))

    def _get_raster_metadata(self, date):
        config = deepcopy(self.source_config)
        config['date'] = date.isoformat()
        del config['assets']
        return config
    
    #
    # Build Assets
    #

    def _build_assets(self, items):
        configs = self._init_asset_configs()
        self._update_asset_configs(configs, items)
        return [Asset(asset['name'], self.aoi, asset['paths'], asset) for asset in configs]
        
    def _init_asset_configs(self):
        configs = deepcopy(self.source_config['assets'])
        configs = self._filter_and_order_asset_configs(configs)            
        self._init_asset_paths(configs)
        return configs
    
    def _filter_and_order_asset_configs(self, configs):
        '''
            Filter and order assets configs as defined in self.assets.
        '''
        if self.assets is not None:
            f_assets = []
            for asset in self.assets:
                config = list(filter(lambda config: config['name'] == asset, configs))[0]
                f_assets.append(config)
            return f_assets
        else:
            return configs
    
    def _init_asset_paths(self, configs):
        for asset in configs:
            asset['paths'] = []
    
    def _update_asset_configs(self, configs, items):
        for item in items:
            for config in configs:
                self._assign_asset_config_path(config, item)
                # self._update_asset_config_bands(config, item)
                # add additional metadata here

    def _assign_asset_config_path(self, config, item):
        url = item.assets[config['name']].href
        if re.match(self.HTTPS_REGEX, url):
            path = f'/vsicurl/{url}'
        elif re.match(self.S3_REGEX, url):
            path = f"/vsis3/{url.replace('s3://', '')}"
        config['paths'].append(path)
