from kerchunk_tools.print_ds import print_ds
import pathlib
from typing import List


def test_print_ds(kerchunk_files: List[pathlib.Path]):
    print_ds(kerchunk_files[0])
