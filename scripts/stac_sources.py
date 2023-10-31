
import argparse


from stacext import Sources

parser = argparse.ArgumentParser(
    prog='stac_sources.py',
    description='List all available sources and source assets.'
)


if __name__ == "__main__":
    args = parser.parse_args()
    sources = Sources()
    sources.fetch()
    sources.pprint()