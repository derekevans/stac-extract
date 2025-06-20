import glob
import json
import datetime

import rioxarray
import xarray as xr


def to_xarray(in_dir):
    return XArrayConverter(in_dir).convert()


class XArrayConverter:

    def __init__(self, in_dir):
        self.in_dir = in_dir

    def convert(self):
        datasets = self._load_datasets()
        dataset = xr.concat(datasets, 'time')
        return dataset

    def _load_datasets(self):
        return [self._load_dataset(metadata) for metadata in self._metadatas()]

    def _metadatas(self):
        metadata_paths = sorted(glob.glob(f'{self.in_dir}/*.json'))
        for metadata_path in metadata_paths:
            with open(metadata_path) as f:
                yield json.load(f)

    def _load_dataset(self, metadata):
        ds = xr.open_dataset(
            f"{self.in_dir}/{metadata['file_name']}", 
            engine="rasterio", 
            mask_and_scale=True, 
            cache=False, 
            band_as_variable=True
        )
        f_ds = ds.rename(self._band_name_map(metadata))
        date = datetime.datetime.fromisoformat(metadata['date']).date()
        f_ds = f_ds.expand_dims({'time': [date]})
        f_ds = self._set_band_attrs(f_ds, metadata)
        f_ds = self._set_dataset_attrs(f_ds, metadata)
        return f_ds

    def _band_name_map(self, metadata):
        names = []
        for asset in metadata['assets']:
            for band in asset['bands']:
                names.append(band['name'])
        return {f"band_{idx + 1}": name for idx, name in enumerate(names)}

    def _set_band_attrs(self, xds, metadata):
        for asset in metadata['assets']:
            for band in asset['bands']:
                xds[band['name']].attrs = band
                xds[band['name']].attrs['paths'] = asset['paths']
        return xds

    def _set_dataset_attrs(self, xds, metadata):
        merge_attrs = {k: v for k, v in metadata.items() if k in ['name', 'description', 'url']}
        xds.attrs.update(merge_attrs)
        return xds
        