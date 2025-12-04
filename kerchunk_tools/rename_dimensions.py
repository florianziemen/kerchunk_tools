#!/usr/bin/env python3

# %%
from argparse import ArgumentParser
import logging
import xarray as xr
import json
from typing import Dict, Union
from pathlib import Path

# %%

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# %%
def rename_dimensions(kerchunk_file:Union[str, Path], replacements: Dict[str, str]):
    kerchunk_file = Path(kerchunk_file)
    logger.debug(f"Processing kerchunk file: {kerchunk_file}")
    with open(kerchunk_file / ".zmetadata", "r") as f:
        kerchunk_data = json.load(f)

    logger.debug(f"Keys in {kerchunk_file}: {list(kerchunk_data['metadata'].keys())}")

    ds = xr.open_dataset(
        f"reference::{kerchunk_file}", engine="zarr", consolidated=False, chunks={}
    )

    logger.debug([x for x in ds.variables])
    for x in ds.variables:
        update_array_dimensions(replacements, kerchunk_data, x)
    for old, new in replacements.items():
        rename_metadata_keys(kerchunk_data, old, new)
        print(kerchunk_data["metadata"])
    for old, new in replacements.items():
        if (kerchunk_file / old).exists():
            (kerchunk_file / old).rename(kerchunk_file / new)
    with open(kerchunk_file / ".zmetadata", "w") as f:
        json.dump(kerchunk_data, f, indent=2)


def update_array_dimensions(replacements, kerchunk_data, x):
    kerchunk_data["metadata"][f"{x}/.zattrs"]["_ARRAY_DIMENSIONS"] = [
        replacements.get(dim, dim)
        for dim in kerchunk_data["metadata"][f"{x}/.zattrs"]["_ARRAY_DIMENSIONS"]
    ]


def rename_metadata_keys(kerchunk_data, old, new):
    if f"{old}/.zattrs" in kerchunk_data["metadata"]:
        kerchunk_data["metadata"][f"{new}/.zattrs"] = kerchunk_data["metadata"][
            f"{old}/.zattrs"
        ]
        del kerchunk_data["metadata"][f"{old}/.zattrs"]
    else:
        logger.debug(f"No .zattrs found for {old}->{new}")
    if f"{old}/.zarray" in kerchunk_data["metadata"]:
        kerchunk_data["metadata"][f"{new}/.zarray"] = kerchunk_data["metadata"][
            f"{old}/.zarray"
        ]
        del kerchunk_data["metadata"][f"{old}/.zarray"]
    else:
        logger.debug(f"No .zarray found for {old}->{new}")


# %%
def parse_args():
    parser = ArgumentParser(description="Process Kerchunk files")
    parser.add_argument("files", nargs="+", help="List of Kerchunk files to process")
    parser.add_argument(
        "--replacements", nargs="+", help="List of replacements in the form old=new"
    )
    args = parser.parse_args()
    if args.replacements:
        args.replacements = dict(
            (old, new) for old, new in (item.split("=") for item in args.replacements)
        )
    return args

def main ():
    args = parse_args()
    for kerchunk_file in args.files:
        rename_dimensions(kerchunk_file, args.replacements)

if __name__ == "__main__":
    main()