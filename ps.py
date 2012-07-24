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


def read_entries():
    for ef in os.listdir(cfg['site_dir']):
        if ef.endswith(cfg['pages_ext']):
            file = open(cfg['site_dir']+ef, 'r')
            content = file.read()
            file.close()

            yield {'name': ef[:ef.find(cfg['pages_ext'])],
                   'content': bytes.decode(convert(content, 'markdown', 'html'))}
        else:
            rmanything(cfg['out_dir']+ef)
            copyanything(cfg['site_dir']+ef, cfg['out_dir']+ef)


class TemplateRenderer():
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(cfg['templates_dir'], encoding='utf-8'))
        self.tpl = {}
        self.tpl['layout'] = self.env.get_template('layout.tpl')
        self.tpl['page_content'] = self.env.get_template('page_content.tpl')
        self.tpl['index_content'] = self.env.get_template('index_content.tpl')

    def clean_before_render(self):
        # make output directory if it doesnt exist
        if not os.path.exists(cfg['out_dir']):
            os.makedirs(cfg['out_dir'])

        # remove old html files
        for f in os.listdir(cfg['out_dir']):
            if f.endswith(".html"):
                os.remove(cfg['out_dir']+f)

    def create_layout_vars(self, page_tpl, page_vars, **kwargs):
        if kwargs.get('page_name') != None:
            titlestr = ' - ' + kwargs['page_name']
        else
            titlestr = ''

        return {
          'title': self.render_title(ch['name'])+titlestr,
          'content': self.tpl[page_tpl].render(page_vars)
        }


    def render_all(self):
        self.clean_before_render()
        pages = []

        # render chunk pages
        for ch in read_entries():
            ent_vars = {'page': ch}
            lv = self.create_layout_vars('page_content', ent_vars, page_name=ch['name'])

            fname = cfg['out_dir'] + ch['name'] + '.html'
            f = open(fname, 'w')
            f.write(self.tpl['layout'].render(lv))
            f.close()

            pages.append({'name': ch['name']})


        # render index
        index_vars = {'pages': pages}
        lv = self.create_layout_vars('index_content', index_vars)

        f = open(cfg['out_dir']+'index.html', 'w')
        f.write(self.tpl['layout'].render(lv))
        f.close()


if __name__ == '__main__':
    if len(argv) == 1:
        tr = TemplateRenderer()
        tr.render_all()
    else:
        print("there's no arguments right now.")
