import os, shutil, errno

def rmanything(thing):
    try:
        shutil.rmtree(thing)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            os.remove(thing)
        else: raise


def file_is_page(filename):
    page_extensions = ['.md', '.rst']
    if '.' in filename:
        ext = filename[filename.index('.'):]
        return ext in page_extensions
    else:
        return False


