
# We can query from multiple sources.  Here we need to configure query sources and have each query source return the same query result object


class Query:

    def __init__(self, aoi, **kwargs):
        self.aoi = aoi
        self.start_date = kwargs['start_date']
        self.end_date = kwargs['end_date']
    
    def query(self):
        pass

    def build_rasters(self):
        pass 

    