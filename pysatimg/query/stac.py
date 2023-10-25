
from copy import deepcopy

import pystac_client

from .query import Query
from pysatimg.models import Asset


class STACQuery(Query):

    def _set_results(self):
        super()._set_results()
        self._results = self._get_catalog().search(
            collections=[self._get_collection()],
            intersects=self._format_aoi(),
            datetime=self._format_date()
        )

    def _get_collection(self):
        return self._source_config['collection']

    def _get_catalog(self):
        return pystac_client.Client.open(self._get_url())
    
    def _get_url(self):
        return self._source_config['url']
    
    def _format_aoi(self):
        return self.aoi.to_crs(4326).unary_union
    
    def _format_date(self):
        return f"{self.start_date.isoformat()}/{self.end_date.isoformat()}"
    
    def _build_assets(self, items):
        configs = self._init_asset_configs()
        self._update_asset_configs(configs, items)
        return [Asset(asset['name'], self.aoi, asset['paths'], asset) for asset in configs]
        
    def _init_asset_configs(self):
        configs = deepcopy(self._source_config['assets'])
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
                self._update_asset_config_bands(config, item)
                # add additional metadata here

    def _assign_asset_config_path(self, config, item):
        url = item.assets[config['name']].href
        path = f'/vsicurl/{url}'
        config['paths'].append(path)

    def _update_asset_config_bands(self, config, item):
        item_band_infos = item.assets[config['name']].to_dict().get('eo:bands')
        config_band_infos = config.get('bands')

        if item_band_infos is not None and config_band_infos is None:
            config['bands'] = item_band_infos
        elif item_band_infos is not None and config_band_infos is not None:
            updated_config_band_infos = []
            for item_band_info in item_band_infos:
                f_config_band_infos = list(filter(lambda config_band_info: config_band_info['name'] == item_band_info['name'], config_band_infos))
                if len(f_config_band_infos) == 0:
                    updated_config_band_infos.append(item_band_infos)
                else:
                    config_band_info = f_config_band_infos[0]
                    merged_infos = {**item_band_info, **config_band_info}
                    updated_config_band_infos.append(merged_infos)       
            config['bands']  = updated_config_band_infos