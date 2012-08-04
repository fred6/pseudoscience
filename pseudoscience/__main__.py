import sys

from pseudoscience.core import compile_site

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # get config
        import config as cfg

        compile_site()
    else:
        print("there's no arguments right now.")
