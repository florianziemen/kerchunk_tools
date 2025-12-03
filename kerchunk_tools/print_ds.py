#!/usr/bin/env python3

import xarray as xr
from argparse import ArgumentParser
import pandas as pd
import sys

import logging


def print_ds(infile, print_heads = False):
    ds = xr.open_zarr(f"reference::{infile}", consolidated=False)
    print(ds)
    print_inlined_dimensions(infile, ds)
    if print_heads:
        print_head(infile, ds)

def print_inlined_dimensions(infile, ds):
    print ("Inlined dimensions and their sizes:")
    for x in ds.dims:
        try:
            dt = pd.read_parquet(f"{infile}/{x}/refs.0.parq", engine="fastparquet")
            print(x, sys.getsizeof(dt.head(1)["raw"]))
        except FileNotFoundError:
            print(f"{x} has no data.")

def print_head(infile, ds):
    print("Head of each variable:")
    for x in ds.variables:
        try:
            dt = pd.read_parquet(f"{infile}/{x}/refs.0.parq", engine="fastparquet")
            print(x, dt.head(1))
        except FileNotFoundError:
            print(f"{x} has no data.")

def parse_args():
    parser = ArgumentParser(description="Print Zarr dataset")
    parser.add_argument("infile", help="Input Zarr file")
    parser.add_argument("--heads", help="print heads of parquet tables", action="store_true")
    parser.add_argument("-v","--verbose", help="Enable verbose logging", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    return args

def main():
    args = parse_args()
    print_ds(args.infile, args.heads)

if __name__ == "__main__":
    main()
