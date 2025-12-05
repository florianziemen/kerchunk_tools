# Simple tools that manipulate kerchunk datasets based on the raw parquet fieles

## Scripts in `kerchunk_tools/`

- **merge_datasets**  Merges multiple kerchunk reference files along the time dimension into a single output. Uses `MultiZarrToZarr` for concatenation and supports logging/debugging.
- **print_ds** Prints the contents and structure of a kerchunk reference dataset. Shows inlined dimensions, their sizes, and optionally the head of each variable.
- **remove_from_ds.py** Removes specified variables or dimensions from a kerchunk reference dataset. Updates metadata and logs the process.
- **rename_dimensions.py** Renames dimensions in a kerchunk reference dataset according to a user-provided mapping. Useful for standardizing dimension names.
- **update_paths.py** Rewrites path prefixes in kerchunk parquet stores, either in-place or to a new file. Useful for updating storage locations or migrating datasets.
