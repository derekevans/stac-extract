
from concurrent.futures import ThreadPoolExecutor
import datetime

import geopandas as gpd
from alive_progress import alive_bar

from ..query.sentinel2 import Sentinel2L2AQuery


class Extractor:

    """
    Base class to extract imagery for an area of interest.

    The coordinate reference system and extent will be the same as the input area of interest. 
    """

    def __init__(
            self, 
            source_name: str, 
            aoi: gpd.GeoDataFrame | gpd.GeoSeries, 
            start_date: datetime.date, 
            end_date: datetime.date, 
            out_dir: str,
            pixel_size: tuple[int | float, int | float] = (10, -10), 
            n_threads: int = 1, 
            assets:  list[str] | None = None
        ):
        self.source_name = source_name
        self.aoi = aoi
        self.start_date = start_date
        self.end_date = end_date
        self.out_dir = out_dir
        self.pixel_size = pixel_size
        self.n_threads = n_threads
        self.assets = assets
        
        self.rasters = None

        self._f_aoi = None
        self._query = None
        

    def extract(self) -> None:

        """Extract, transform, and write imagery for area of interest to output directory."""

        self._format_aoi()
        self._query_source()
        self._create_rasters()

    #
    # AOI formatting
    #

    def _format_aoi(self):
        geom = self.aoi.unary_union
        self._f_aoi = gpd.GeoSeries([geom], crs=self.aoi.crs)

    #
    # Source query
    # 

    def _query_source(self):
        self._query = self._get_source_query_instance()
        self.rasters = self._query.query()

    def _get_source_query_instance(self):
        query_class = self._get_source_query_class()
        return query_class(
            aoi=self.aoi,
            start_date=self.start_date,
            end_date=self.end_date,
            assets=self.assets
        )
        
    def _get_source_query_class(self):
        if self.source_name == 'sentinel-2-l2a':
            return Sentinel2L2AQuery
        
    #
    # Raster creation
    #
        
    def _create_rasters(self):
        if self.n_threads > 1:
            self._create_rasters_in_parallel()
        else:
            with alive_bar(len(self.rasters), force_tty=True) as bar:
                for raster in self.rasters:
                        raster.create(self.pixel_size, self.out_dir)
                        bar()

    def _create_rasters_in_parallel(self):
        tasks = self._get_create_raster_tasks()
        self._in_parallel(tasks)

    def _get_create_raster_tasks(self):
        tasks = []
        for raster in self.rasters:
            task = (raster.create, self.pixel_size, self.out_dir)
            tasks.append(task)
        return tasks

    def _in_parallel(self, tasks):
        with alive_bar(len(tasks), force_tty=True) as bar:
            with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
                futures = [executor.submit(*task) for task in tasks]
                for future in futures:
                    future.add_done_callback(lambda x: bar())
    