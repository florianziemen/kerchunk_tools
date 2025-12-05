#!/usr/bin/env python3

from kerchunk.combine import MultiZarrToZarr, merge_vars
from fsspec.implementations.reference import LazyReferenceMapper
import kerchunk.df
from argparse import ArgumentParser
from typing import Iterable, List, Union
import xarray as xr
from pathlib import Path
import logging
import kerchunk_tools.print_ds as print_ds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def merge_datasets_with_time(
    files: List[str],
    outfile: str,
):
    logger.debug(f"Merging datasets with time dimension: {files}")
    logger.debug(f"Output file: {outfile}")
    out_json = MultiZarrToZarr(
        files,
        concat_dims=["time"],
        identical_dims=get_identical_dims(files),
        inline_threshold=0,
    ).translate()

    kerchunk.df.refs_to_dataframe(
        out_json,
        outfile,
        record_size=10000000,
    )
    return out_json

def merge_time_independent_datasets(parquet_stores, outfile):
    stores = [
        dict(
            refs=LazyReferenceMapper(
                root=path,
            )
        )
        for path in parquet_stores
    ]

    merged_refs = merge_vars(stores)
    kerchunk.df.refs_to_dataframe(merged_refs, outfile, record_size=100000)

def sort_time_dependent(files):
    no_time = list()
    with_time = list()
    for f in files:
        ds = xr.open_zarr(f"reference::{f}", consolidated=False)
        if "time" in ds.dims:
            with_time.append(f)
        else:
            no_time.append(f)
            logger.debug(f"File {f} has no time dimension.")
            logger.debug(f"Dimensions: {ds.dims}")
    logger.debug(f"Datasets without time dimension: {no_time}")
    logger.debug(f"Datasets with time dimension: {with_time}")
    return no_time, with_time


def get_identical_dims(files):
    identical_dims = set()
    for f in files:
        ds = xr.open_zarr(f"reference::{f}", consolidated=False)
        identical_dims |= set(ds.dims)
        identical_dims.discard("time")
    return identical_dims


def parse_args():
    parser = ArgumentParser(description="Merge Zarr datasets")
    parser.add_argument("files", nargs="+", help="List of Zarr files to merge")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument("-o", "--output", required=True, help="Output Zarr file")

    args = parser.parse_args()
    if Path(args.output).exists():
        raise FileExistsError(f"Output file {args.output} already exists.")
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
    return args



def merge_datasets(files: Union[Iterable[str],Iterable[Path]], output: Union[str,Path]):
    files = [str(Path(f).resolve()) for f in files]
    no_time, with_time = sort_time_dependent(files)
    merge_datasets_with_time(with_time, str(output)+".time.parquet")
    if no_time:
        merge_time_independent_datasets(no_time + [ str(output)+".time.parquet"], output)
    else:
        (Path(str(output) + ".time.parquet")).rename(output)
    print_ds.print_ds(output)

def main():
    args = parse_args()
    merge_datasets(args.files, args.output)

if __name__ == "__main__":
    main()