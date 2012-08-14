import os, shutil, errno, subprocess

#http://nixtu.blogspot.com/2011/11/pandoc-markup-converter.html
def convert(source, from_format, to_format):
    # raises OSError if pandoc is not found!
    # supported formats at http://johnmacfarlane.net/pandoc/
    p = subprocess.Popen(['pandoc', '--from=' + from_format, '--to=' + to_format, '--mathjax'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    return p.communicate(bytes(source, 'UTF-8'))[0]


# http://stackoverflow.com/a/1994840
def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            folder = dst[:dst.rindex('/')+1]
            if not os.path.exists(folder):
                os.makedirs(folder)

            shutil.copy(src, dst)
        else: raise

def rmanything(thing):
    try:
        shutil.rmtree(thing)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            os.remove(thing)
        else: raise
