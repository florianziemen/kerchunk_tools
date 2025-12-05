from kerchunk_tools.remove_from_ds import remove_from_ds
import xarray as xr
import pathlib
import tempfile
import shutil
from typing import List, Tuple


def test_remove_from_ds(
    kerchunk_files: List[pathlib.Path],
    datasets: Tuple[xr.Dataset, xr.Dataset, xr.Dataset],
):
    with tempfile.TemporaryDirectory() as tmpdir:
        kerchunk_file: pathlib.Path = kerchunk_files[0]
        # remove_from_ds modifies in place, so we need to copy the file first
        tmp_kerchunk_path: pathlib.Path = pathlib.Path(tmpdir) / kerchunk_file.name
        shutil.copytree(kerchunk_file, tmp_kerchunk_path)

        remove_from_ds(str(tmp_kerchunk_path), ["var1"])

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
        assert "var1" not in ds
        assert ds["time"].equals(datasets[1]["time"])
