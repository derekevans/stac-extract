
import re

import pystac_client


class Sources:

    CATALOG_URLS = (
        'https://earth-search.aws.element84.com/v1',
        'https://planetarycomputer.microsoft.com/api/stac/v1'
    ) 

    TYPE_REGEX = 'image\/tiff|image\/jp2'

    def __init__(self):
        self.configs = None

    def fetch(self):
        self.configs = {}
        for url in self.CATALOG_URLS:
            catalog = pystac_client.Client.open(url)
            configs = self._collection_configs(catalog, url)
            self.configs.update(configs)
        return self.configs

    def _collection_configs(self, catalog, url):
        return {collection.id: self._collection_config(collection, url) for collection in catalog.get_collections() }

    def _collection_config(self, collection, url):
        return {
            'name': collection.id,
            'description': collection.description,
            'url': url,
            'assets': self._assets_config(collection)
        }

    def _assets_config(self, collection):
        assets = []
        for asset_name, asset_config in collection.to_dict()['item_assets'].items():
            if re.search(self.TYPE_REGEX, asset_config['type']):
                f_asset = self._format_asset(asset_name, asset_config)
                assets.append(f_asset)
        return assets
        
    def _format_asset(self, name, info):
        bands = info.get('eo:bands') or [{'name': name}]
        return {
            'name': name,
            'bands': bands
        }

    def pprint(self):

        '''Format and print sources'''

        if self.configs is None:
            self.fetch()

        for _, source in self.configs.items():
            assets = ', '.join([asset['name'] for asset in source['assets']])
            print()
            print(f"NAME: {source['name']}")
            print(f"    DESCRIPTION: {source['description']}")
            print(f"    ASSETS: {assets}")