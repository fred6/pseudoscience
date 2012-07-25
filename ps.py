import os, yaml, shutil, errno, subprocess
from sys import exit, argv
from jinja2 import Environment, FileSystemLoader

# get config
f = open('config.yaml', 'r')
cfg = yaml.load(f.read())
f.close()

    
#http://nixtu.blogspot.com/2011/11/pandoc-markup-converter.html
def convert(source, from_format, to_format):
    # raises OSError if pandoc is not found!
    # supported formats at http://johnmacfarlane.net/pandoc/
    p = subprocess.Popen(['pandoc', '--from=' + from_format, '--to=' + to_format],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    return p.communicate(bytes(source, 'UTF-8'))[0]


# http://stackoverflow.com/a/1994840
def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def rmanything(thing):
    try:
        shutil.rmtree(thing)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            os.remove(thing)
        else: raise


class SiteCompiler():
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(cfg['templates_dir'], encoding='utf-8'))
        self.tpl = {}
        self.tpl['layout'] = self.env.get_template('layout.tpl')
        self.tpl['page_content'] = self.env.get_template('page_content.tpl')
        self.tpl['index_content'] = self.env.get_template('index_content.tpl')
        self.layout_vars = {}

    def _clean_up(self):
        # make output directory if it doesnt exist
        if not os.path.exists(cfg['out_dir']):
            os.makedirs(cfg['out_dir'])

        # clean out old files
        for f in os.listdir(cfg['out_dir']):
            rmanything(cfg['out_dir']+f)


    def _set_layout_vars(self, page_tpl, page_vars, **kwargs):
        if kwargs.get('page_name') != None:
            titlestr = ' - ' + kwargs['page_name']
        else:
            titlestr = ''

        self.layout_vars = {
          'title': cfg['site_title']+titlestr,
          'content': self.tpl[page_tpl].render(page_vars)
        }

    def _write_file(self, file_name):
        fname = cfg['out_dir'] + file_name + '.html'
        f = open(fname, 'w')
        f.write(self.tpl['layout'].render(self.layout_vars))
        f.close()

    def _compile_page(self, fname):
        file = open(cfg['site_dir']+fname, 'r')
        content = file.read()
        file.close()

        pg = {'name': fname[:fname.find(cfg['pages_ext'])],
              'content': bytes.decode(convert(content, 'markdown', 'html'))}

        self._set_layout_vars('page_content', {'page': pg}, page_name=pg['name'])
        self._write_file(pg['name'])

        return pg['name']


    def compile(self):
        self._clean_up()
        pages = []

        # read input directory
        for ef in os.listdir(cfg['site_dir']):
            if ef.endswith(cfg['pages_ext']):
                page_info = self._compile_page(ef)
                pages.append({'name': page_info})
            else:
                copyanything(cfg['site_dir']+ef, cfg['out_dir']+ef)

        # compile index file
        self._set_layout_vars('index_content', {'pages': pages})
        self._write_file('index')


if __name__ == '__main__':
    if len(argv) == 1:
        sc = SiteCompiler()
        sc.compile()
    else:
        print("there's no arguments right now.")
