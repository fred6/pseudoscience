import os, shutil, errno

def rmanything(thing):
    try:
        shutil.rmtree(thing)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            os.remove(thing)
        else: raise
