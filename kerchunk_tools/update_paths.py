#! /usr/bin/env python

import pandas as pd
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def rewrite_kerchunk_parquet(input_parquet_path, output_parquet_path, old_prefix, new_prefix):
    df = pd.read_parquet(input_parquet_path, engine="fastparquet")
    if "path" in df.columns:
        df['path'] = df['path'].str.replace(f'^{old_prefix}', new_prefix, regex=True)
    else:
        raise ValueError('Path column not found. No replacements made.')
    df.to_parquet(output_parquet_path, engine="fastparquet")
    logger.info(f"Rewritten kerchunk parquet store saved to {output_parquet_path}")

def rewrite_kerchunk_parquets_inplace(parquet_dir, old_prefix, new_prefix):
    parquet_dir = Path(parquet_dir)
    for store in parquet_dir.glob("*"):
        if store.is_dir():
            for parquet_file in store.glob("*.parq"):
                rewrite_kerchunk_parquet(parquet_file, parquet_file, old_prefix, new_prefix)

def parse_args():
    parser = argparse.ArgumentParser(description="Rewrite path prefixes in all kerchunk parquet stores in a directory.")
    parser.add_argument("input_dir", help="Directory containing kerchunk parquet stores")
    parser.add_argument("old_prefix", help="Old prefix to replace")
    parser.add_argument("new_prefix", help="New prefix to use")
    parser.add_argument("--verbose" , "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    return args

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    rewrite_kerchunk_parquets_inplace(args.input_dir, args.old_prefix, args.new_prefix)
    
if __name__ == "__main__":
    main()