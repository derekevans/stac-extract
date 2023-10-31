
from concurrent.futures import ThreadPoolExecutor
import datetime

import geopandas as gpd
from alive_progress import alive_bar

from .query import Query
from .sources import Sources


class Extractor:

    """
    Extract data for an area of interest from a specified source.

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
            resample_method: str = 'bilinear',
            n_threads: int = 1, 
            assets:  list[str] | None = None
        ):
        self.source_name = source_name
        self.aoi = aoi
        self.start_date = start_date
        self.end_date = end_date
        self.out_dir = out_dir
        self.pixel_size = pixel_size
        self.resample_method = resample_method
        self.n_threads = n_threads
        self.assets = assets
        
        self.rasters = None

        self._f_aoi = None
        self._sources = None
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
        self._query = Query(
            aoi=self.aoi,
            source_config=self._get_source_config(),
            start_date=self.start_date,
            end_date=self.end_date,
            assets=self.assets
        )
        self.rasters = self._query.query()

    def _get_source_config(self):
        if self._sources is None:
            self._set_sources()
        return self._sources.configs[self.source_name]
    
    def _set_sources(self):
        self._sources = Sources()
        self._sources.fetch()
        
    #
    # Raster creation
    #
        
    def _create_rasters(self):
        if self.n_threads > 1:
            self._create_rasters_in_parallel()
        else:
            with alive_bar(len(self.rasters), force_tty=True) as bar:
                for raster in self.rasters:
                    raster.create(self.pixel_size, self.resample_method, self.out_dir)
                    bar()

    def _create_rasters_in_parallel(self):
        tasks = self._get_create_raster_tasks()
        self._in_parallel(tasks)

    def _get_create_raster_tasks(self):
        tasks = []
        for raster in self.rasters:
            task = (raster.create, self.pixel_size, self.resample_method, self.out_dir)
            tasks.append(task)
        return tasks

    def _in_parallel(self, tasks):

        # TODO: Add error handling.  This is important when requesting from S3 with /vsis3/ and 
        # user does not have AWS_SECRET_ACCESS_KEY and AWS_NO_SIGN_REQUEST defined or ~/.aws/credentials
        
        with alive_bar(len(tasks), force_tty=True) as bar:
            with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
                futures = [executor.submit(*task) for task in tasks]
                for future in futures:
                    future.add_done_callback(lambda x: bar())
    