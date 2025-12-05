from kerchunk_tools.rename_dimensions import rename_dimensions
import xarray as xr
import pathlib
import tempfile
import shutil
from typing import List


def test_rename_dimensions(kerchunk_files: List[pathlib.Path]):
    with tempfile.TemporaryDirectory() as tmpdir:
        kerchunk_file: pathlib.Path = kerchunk_files[0]
        # rename_dimensions modifies in place, so we need to copy the file first
        tmp_kerchunk_path: pathlib.Path = pathlib.Path(tmpdir) / kerchunk_file.name
        shutil.copytree(kerchunk_file, tmp_kerchunk_path)

        rename_dimensions(str(tmp_kerchunk_path), {"cell": "new_cell"})

        ds = xr.open_dataset(
            "reference://",
            engine="zarr",
            backend_kwargs={
                "storage_options": {
                    "fo": str(tmp_kerchunk_path),
                    "remote_protocol": "file",
                },
                "consolidated": False,
            },
        )
        assert "new_cell" in ds.dims
        assert "cell" not in ds.dims
        assert "new_cell" in ds["var1"].dims
        assert "cell" not in ds["var1"].dims
