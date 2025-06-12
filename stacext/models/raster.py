
import subprocess as sp
from copy import deepcopy
import json
import re

from stacext.models import Asset


class Raster:

    def __init__(self, name, aoi, assets, metadata={}):
        self.name = name
        self.aoi = aoi
        self.assets = assets
        self.metadata = metadata
        
        self.pixel_size = None
        self.resample_method = None
        self.out_path = None

    def create(self, pixel_size, resample_method, out_dir):
        try:
            self.pixel_size = pixel_size
            self.resample_method = resample_method
            self._create_assets()
            self._merge_assets(out_dir)
            self._write_metadata(out_dir)
        finally:
            self._cleanup()

    def _create_assets(self):
        for asset in self.assets:
            resample_method = self._get_resample_method(asset)
            asset.create(self.pixel_size, resample_method)     

    def _get_resample_method(self, asset):
        if isinstance(self.resample_method, dict):
            return self.resample_method[asset.name]
        else:
            return self.resample_method

    def _merge_assets(self, out_dir):
        self.out_path = f'{out_dir}/{self._get_file_name()}'
        asset_paths = [asset.out_path for asset in self.assets]
        cmd = f'gdal_merge.py -n {self.assets[0].nd_value} -a_nodata {self.assets[0].nd_value} -o \"{self.out_path}\" -separate {" ".join(asset_paths)}'
        sp.run(cmd, stdout=sp.DEVNULL, shell=True)

    def _get_file_name(self):
        return f'{self.name}.tif'
    
    def _write_metadata(self, out_dir):
        out_path = f'{out_dir}/{self.name}.json'
        text = json.dumps(self.get_metadata(), indent=4)
        with open(out_path, 'w') as file:
            file.write(text)

    def get_metadata(self):
        metadata = deepcopy(self.metadata)
        metadata['file_name'] = self._get_file_name()
        metadata['assets'] = [asset.metadata for asset in self.assets]
        return metadata

    def _cleanup(self):
        for asset in self.assets:
            asset.cleanup()


class RasterBuilder:

    HTTPS_REGEX = '^https:\/\/'
    S3_REGEX = '^s3:\/\/'

    def __init__(self, source_config, aoi, assets, date, items):
        self.source_config = source_config
        self.aoi = aoi
        self.date = date
        self.assets = assets
        self.items = items

    def build(self):
        assets = self._build_assets()
        name = f"{self.source_config['name']}_{self.date.isoformat()}"
        return Raster(name, self.aoi, assets, self._get_raster_metadata())

    def _get_raster_metadata(self):
        config = deepcopy(self.source_config)
        config['date'] = self.date.isoformat()
        del config['assets']
        return config
    
    #
    # Build Assets
    #

    def _build_assets(self):
        configs = self._init_asset_configs()
        self._update_asset_configs(configs)
        return [Asset(config['name'], self.aoi, config['paths'], config) for config in configs]
        
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
    
    def _update_asset_configs(self, configs):
        for item in self.items:
            for config in configs:
                self._assign_asset_config_path(config, item)

    def _assign_asset_config_path(self, config, item):
        url = item.assets[config['name']].href
        if re.match(self.HTTPS_REGEX, url):
            path = f'/vsicurl/{url}'
        elif re.match(self.S3_REGEX, url):
            path = f"/vsis3/{url.replace('s3://', '')}"
        config['paths'].append(path)