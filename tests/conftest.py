import numpy as np
import pytest
import xarray as xr
import pathlib
import tempfile
import virtualizarr
import obstore
from virtualizarr.parsers import HDFParser
from virtualizarr.registry import ObjectStoreRegistry
from typing import Tuple, List

@pytest.fixture(scope="session")
def datasets() -> Tuple[xr.Dataset, xr.Dataset, xr.Dataset]:
    ds1 = xr.Dataset(
        {
            "var1": (
                ("time", "cell"),
                np.random.rand(10, 100),
                {"foo": "bar", "baz": "qux"},
            )
        },
        coords={"time": np.arange(10), "cell": np.arange(100)},
        attrs={"foo": "bar"},
    )
    ds2 = xr.Dataset(
        {
            "var2": (
                ("time", "cell"),
                np.random.rand(10, 100),
                {"foo": "bar", "baz": "qux"},
            )
        },
        coords={"time": np.arange(10), "cell": np.arange(100)},
        attrs={"foo": "bar"},
    )
    ds3 = xr.Dataset(
        {"var3": (("cell"), np.random.rand(100), {"foo": "bar", "baz": "qux"})},
        coords={"cell": np.arange(100)},
        attrs={"foo": "bar"},
    )
    return ds1, ds2, ds3


@pytest.fixture(scope="session")
def netcdf_files(datasets: Tuple[xr.Dataset, xr.Dataset, xr.Dataset]) -> List[pathlib.Path]:
    with tempfile.TemporaryDirectory() as tmpdir:
        paths: List[pathlib.Path] = []
        for i, ds in enumerate(datasets):
            path = pathlib.Path(tmpdir) / f"ds{i}.nc"
            ds.to_netcdf(path, engine="h5netcdf")
            paths.append(path)
        yield paths


@pytest.fixture(scope="session")
def kerchunk_files(netcdf_files: List[pathlib.Path]) -> List[pathlib.Path]:
    kerchunk_paths: List[pathlib.Path] = []
    
    stores = {f"file://{path.parent}": obstore.store.from_url(f"file://{path.parent}") for path in netcdf_files}
    registry = ObjectStoreRegistry(stores)
    parser = HDFParser()

    for path in netcdf_files:
        outpath: pathlib.Path = path.with_suffix(".parquet")

        vds = virtualizarr.open_virtual_dataset(
            url=f"file://{path}", registry=registry, parser=parser
        )

        vds.vz.to_kerchunk(outpath, format="parquet")
        kerchunk_paths.append(outpath)
    return kerchunk_paths
