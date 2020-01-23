"""Helpers with regards to actions on the filesystem."""
import os
from contextlib import contextmanager


@contextmanager
def cd(new_dir: str) -> None:
    """Context manager allowing an operation to be performed inside given directory.

    Args:
         new_dir: the directory to move into

    """
    prev_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)
