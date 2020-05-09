import os
from contextlib import contextmanager

@contextmanager
def save_in_dir(path):
    oldpath = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(oldpath)
