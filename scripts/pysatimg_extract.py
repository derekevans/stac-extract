
import argparse
import datetime

import geopandas as gpd

import pysatimg

parser = argparse.ArgumentParser(
    prog='pysatimg_extract.py',
    description='Extracts sateillite imagery for an area or interest from a specific source.'
)

parser.add_argument('--aoi', type=str, required=True,
    help='''
        Path to file with polygon data representing area of interest. 
        See https://geopandas.org/en/stable/docs/user_guide/io.html for supported files.
    '''
)

parser.add_argument('--source', type=str, required=True,
    help='''
        The name of the source where imagery will be extracted.
    '''
)

parser.add_argument('--pixel_x', type=float, required=False,
    help='''
        Pixel length along the x-axis in units of the input area of interest coordinate reference system.
    '''
)

parser.add_argument('--pixel_y', type=float, required=False,
    help='''
        Pixel length along the y-axis in units of the input area of interest coordinate reference system.
    '''
)

parser.add_argument('--start_date', type=str, required=True,
    help='''
        The start date used to search for imagery in ISO 8601 format (i.e., 2023-09-18).
    '''
)

parser.add_argument('--end_date', type=str, required=True,
    help='''
        The end date used to search for imagery in ISO 8601 format (i.e., 2023-09-18).
    '''
)

parser.add_argument('--n_threads', type=int, required=False, default=1,
    help='''
        The number of threads used to extract imagery.
    '''
)

parser.add_argument('-a', '--assets', action='append', required=False,
    help='''
        The assets to extract from source.
    '''
)

parser.add_argument('--out_dir', type=str, required=True,
    help='''
        Path to output directory where data will be written.
    '''
)


if __name__ == "__main__":
    args = parser.parse_args()
    extractor = pysatimg.Extractor(
        aoi=gpd.read_file(args.aoi),
        source_name=args.source, 
        pixel_size=(args.pixel_x, args.pixel_y),  
        start_date=datetime.date.fromisoformat(args.start_date), 
        end_date=datetime.date.fromisoformat(args.end_date), 
        assets=args.assets,
        n_threads=args.n_threads,
        out_dir=args.out_dir
    )
    extractor.extract()