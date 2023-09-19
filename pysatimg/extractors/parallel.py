
from .extractor import Extractor
from concurrent.futures import ThreadPoolExecutor


class ParallelExtractor(Extractor):

    def __init__(self, source_name, aoi, pixel_size, n_threads, out_dir, **kwargs):
        super().__init__(source_name, aoi, pixel_size, out_dir, **kwargs)
        self.n_threads = n_threads
        
    def _create_rasters(self):
        self._in_parallel(self._get_create_raster_tasks())

    def _get_create_raster_tasks(self):
        tasks = []
        for raster in self.rasters:
            task = (raster.create, self.pixel_size, self.out_dir)
            tasks.append(task)
        return tasks

    #
    # Utilities
    #

    def _in_parallel(self, tasks):
        with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
            for task in tasks:
                if hasattr(task, '__iter__'):
                    executor.submit(*task)
                else:
                    executor.submit(task)
