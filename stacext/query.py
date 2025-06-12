
from itertools import groupby
from copy import deepcopy
import re

import pystac_client
import planetary_computer

from stacext.models import RasterBuilder


class Query:

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
        url = self.source_config['url']
        catalog = pystac_client.Client.open(
            url=url,
            modifier=(planetary_computer.sign_inplace if url == "https://planetarycomputer.microsoft.com/api/stac/v1" else None)
        )
        self._results = catalog.search(
            collections=[self.source_config['name']],
            intersects=self._format_aoi(),
            datetime=self._format_date()
        )
    
    def _format_aoi(self):
        return self.aoi.to_crs(4326).unary_union
    
    def _format_date(self):
        return f"{self.start_date.isoformat()}/{self.end_date.isoformat()}"
    
    #
    # Build Rasters
    #
    
    def _build_rasters(self):
        return [self._build_raster(date, items) for date, items in self._group_results_by_date()]
            
    def _group_results_by_date(self):
        return groupby(self._results.items(), lambda x: x.datetime.date())
    
    def _build_raster(self, date, items):
        builder = RasterBuilder(
            source_config=self.source_config,
            aoi=self.aoi,
            assets=self.assets,
            date=date,
            items=items
        )
        return builder.build()
        