
from copy import deepcopy

import pystac_client

from .query import Query
from pysatimg.models import Band


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