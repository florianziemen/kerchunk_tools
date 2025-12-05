from kerchunk_tools import merge_datasets
import xarray as xr
import pathlib
import tempfile
from typing import List


def test_merge_datasets(kerchunk_files: List[pathlib.Path]):
    with tempfile.TemporaryDirectory() as tmpdir:
        outpath: pathlib.Path = pathlib.Path(tmpdir) / "merged.parquet"
        merge_datasets([str(x) for x in kerchunk_files], str(outpath))

        ds = xr.open_dataset(
            "reference://",
            engine="zarr",
            backend_kwargs={
                "storage_options": {
                    "fo": str(outpath),
                    "remote_protocol": "file",
                },
                "consolidated": False,
            },
        )
        assert "var1" in ds
        assert "var2" in ds
        assert "var3" in ds
