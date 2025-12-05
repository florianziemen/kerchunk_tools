#!/usr/bin/env python3

# %%
from argparse import ArgumentParser
import logging
import shutil
import xarray as xr
import json
from typing import List

# %%

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# %%
def remove_from_ds(kerchunk_file, to_drop: List[str]):
    logger.debug(f"Processing kerchunk file: {kerchunk_file}")
    with open(kerchunk_file + "/.zmetadata", "r") as f:
        kerchunk_data = json.load(f)

    # Print the keys in the kerchunk data
    logger.debug(f"Keys in {kerchunk_file}: {list(kerchunk_data['metadata'].keys())}")

    # Load the kerchunk data into an xarray dataset
    ds = xr.open_dataset(
        f"reference::{kerchunk_file}", engine="zarr", consolidated=False, chunks={}
    )

    # Print the dataset information
    logger.debug(f"Available variables: {[x for x in ds]}")
    for x in to_drop:
        del kerchunk_data["metadata"][f"{x}/.zattrs"]
        del kerchunk_data["metadata"][f"{x}/.zarray"]
        shutil.rmtree(f"{kerchunk_file}/{x}")
    with open(kerchunk_file + "/.zmetadata", "w") as f:
        json.dump(kerchunk_data, f, indent=2)


# %%
def parse_args():
    parser = ArgumentParser(description="Process Kerchunk files")
    parser.add_argument("files", nargs="+", help="List of Kerchunk files to process")
    parser.add_argument("--to_drop", nargs="+", help="List of variables to drop")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    for kerchunk_file in args.files:
        remove_from_ds(kerchunk_file, args.to_drop)


if __name__ == "__main__":
    main()
