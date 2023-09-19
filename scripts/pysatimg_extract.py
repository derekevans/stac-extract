
import argparse

parser = argparse.ArgumentParser(
    prog='PySatImg Extractor',
    description='Extracts sateillite imagery for an area or interest from a specific source.'
)

parser.add_argument('--aoi', type=str, required=True,
    description='''
                    Path to file with polygon data representing area of interest. 
                    See https://geopandas.org/en/stable/docs/user_guide/io.html for supported files.
                '''
)

parser.add_argument('--source', type=str, required=True,
    description='''
                    The name of the source where imagery will be extracted.
                '''
)

parser.add_argument('--pixel_x', type=float, required=False,
    description='''
                    Pixel length along the x-axis in units of the input area of interest coordinate reference system.
                '''
)

parser.add_argument('--pixel_y', type=float, required=False,
    description='''
                    Pixel length along the y-axis in units of the input area of interest coordinate reference system.
                '''
)

parser.add_argument('--start_date', type=str, required=True,
    description='''
                    The start date used to search for imagery in ISO 8601 format (i.e., 2023-09-18).
                '''
)

parser.add_argument('--end_date', type=str, required=True,
    description='''
                    The end date used to search for imagery in ISO 8601 format (i.e., 2023-09-18).
                '''
)

parser.add_argument('--n_threads', type=int, required=False,
    description='''
                    The number of threads used to extract imagery.
                '''
)

parser.add_argument('--band', action='append', required=False,
    description='''
                    The bands to extract from source.
                '''
)

def parse_args():
    argparser.parse()

if __name__ == "__main__":
