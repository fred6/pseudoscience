import os, shutil, subprocess
from glob import glob

from jinja2 import Environment, FileSystemLoader

from pseudoscience.util import *


def config_renderers(cfg, smap):
    renderers = jinja2_renderers(cfg, smap.smap)
    renderers['_id'] = make_id_renderer(cfg)
    return renderers


def jinja2_renderers(cfg, site_map):
    env = Environment(loader=FileSystemLoader(cfg.templates_dir, encoding='utf-8'))
    tplext = '.html'

    layout_tpl = env.get_template(cfg.templates['default_layout']+tplext)

    def make_renderer(page_template):
        def renderer(in_fpath, out_fpath):
            pg_vars = parse_file(cfg, in_fpath, out_fpath)
            pg_vars['map'] = site_map

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


def parse_file(cfg, in_fpath, out_fpath):
    last_slash = out_fpath.rindex('/')
    pv = {
            'name': out_fpath[last_slash+1:out_fpath.index('.')],
            'folder': out_fpath[:last_slash+1],
            'fullpath': out_fpath}

    if file_is_page(in_fpath):
        with open(cfg.site_dir+in_fpath, 'r') as file:
            content = file.read()
            in_format = 'markdown' if in_fpath[in_fpath.index('.'):] == '.md' else 'rst'
            pv['content'] = bytes.decode(convert(content, in_format, 'html'))

    return pv



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
