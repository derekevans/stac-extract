
import argparse
import datetime
import json

import geopandas as gpd

import stacext

parser = argparse.ArgumentParser(
    prog='stac_extract.py',
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

parser.add_argument('--resample_method', type=str, required=False, default='bilinear', 
    help='''
        Method used to resample source data.  To define how each asset is resampled, pass JSON where the key 
        is the asset name and the value if the resample method. For example: "{'red': 'bilinear', 'scl': 'near'}"
        Options include: near, bilinear, cubic, cubicspline, lanczos, average, rms, mode, max, min, med, q1, q3, sum
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

def parse_resample_method(args):
    method_str = args.resample_method
    if "{" in method_str:
        return json.loads(method_str.replace("'", '"'))
    else:
        return method_str


if __name__ == "__main__":
    args = parser.parse_args()
    extractor = stacext.Extractor(
        aoi=gpd.read_file(args.aoi),
        source_name=args.source, 
        pixel_size=(args.pixel_x, args.pixel_y),
        resample_method=parse_resample_method(args),  
        start_date=datetime.date.fromisoformat(args.start_date), 
        end_date=datetime.date.fromisoformat(args.end_date), 
        assets=args.assets,
        n_threads=args.n_threads,
        out_dir=args.out_dir
    )
    extractor.extract()
