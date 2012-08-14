import os, shutil, subprocess
from glob import glob

from jinja2 import Environment, FileSystemLoader

def jinja2_renderers(cfg):
    env = Environment(loader=FileSystemLoader(cfg.templates_dir, encoding='utf-8'))
    tplext = '.html'

    layout_tpl = env.get_template(cfg.templates['default_layout']+tplext)

    def make_renderer(page_template):
        def renderer(pg_vars):
            page_content = page_template.render(pg_vars)
            nav = ' > '.join(pg_vars['folder'][1:].split('/')) + pg_vars['name']
            layout_vars = {'content': page_content, 'title': nav}

            fname = cfg.out_dir + pg_vars['fullpath']

            folder = cfg.out_dir + pg_vars['folder']
            create_folder_if_not_exists(folder)

            with open(fname, 'w') as f:
                f.write(str(layout_tpl.render(layout_vars)))

        return renderer

    renderers = {}
    for tpl in glob(cfg.templates_dir+'/*'+tplext):
        key = tpl.replace(cfg.templates_dir+'/', '').replace(tplext, '')
        if key != cfg.templates['default_layout']:
            renderers[key] = make_renderer(env.get_template(key+tplext))

    return renderers


def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


# copy a file's content verbatim to the new place.
# this is fucking ugly. need a better config method
def make_id_renderer(cfg):
    def id_renderer(in_fpath, out_fpath):
        in_file = cfg.site_dir + in_fpath
        out_file = cfg.out_dir + out_fpath

        create_folder_if_not_exists(out_file[:out_file.rindex('/')+1])
        shutil.copy(in_file, out_file)
    return id_renderer



#http://nixtu.blogspot.com/2011/11/pandoc-markup-converter.html
def convert(source, from_format, to_format):
    # raises OSError if pandoc is not found!
    # supported formats at http://johnmacfarlane.net/pandoc/
    p = subprocess.Popen(['pandoc', '--from=' + from_format, '--to=' + to_format, '--mathjax'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    return p.communicate(bytes(source, 'UTF-8'))[0]
