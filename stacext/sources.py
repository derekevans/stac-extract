
import re

import pystac_client


class Sources:

    CATALOG_URLS = (
        'https://earth-search.aws.element84.com/v1',
        'https://planetarycomputer.microsoft.com/api/stac/v1'
    ) 

    TYPE_REGEX = 'image\/tiff|image\/jp2|application\/vnd+zarr'

    def __init__(self):
        self.configs = None

    def fetch(self):
        self.configs = {}
        for url in self.CATALOG_URLS:
            config = self._catalog_config(url)
            self.configs[url] = config
        return self.configs

    def _catalog_config(self, url):
        catalog = pystac_client.Client.open(url)
        configs = {}
        for collection in catalog.get_collections():
            collection_config =  self._collection_config(collection, url)
            if len(collection_config['assets']) > 0:
                configs[collection.id] = collection_config
        return configs

    def _collection_config(self, collection, url):
        return {
            'name': collection.id,
            'description': collection.description,
            'url': url,
            'assets': self._assets_config(collection)
        }

    def _assets_config(self, collection):
        assets = []
        assets_key = 'item_assets' if 'item_assets' in collection.to_dict().keys() else 'assets'
        for asset_name, asset_config in collection.to_dict()[assets_key].items():
            try:
                if re.search(self.TYPE_REGEX, asset_config['type']):
                    f_asset = self._format_asset(asset_name, asset_config)
                    assets.append(f_asset)
            except:
                pass
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

        for catalog, collections in self.configs.items():
            print(f"CATALOG: {catalog}")
            print()
            for _, collection in collections.items():
                assets = ', '.join([asset['name'] for asset in collection['assets']])
                print(f"  COLLECTION: {collection['name']}")
                # print(f"    DESCRIPTION: {collection['description']}")
                print(f"    ASSETS: {assets}")
                print()