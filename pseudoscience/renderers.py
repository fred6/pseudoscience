import os
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
            if not os.path.exists(folder):
                os.makedirs(folder)

            with open(fname, 'w') as f:
                f.write(str(layout_tpl.render(layout_vars)))

        return renderer

    renderers = {}
    for tpl in glob(cfg.templates_dir+'/*'+tplext):
        key = tpl.replace(cfg.templates_dir+'/', '').replace(tplext, '')
        if key != cfg.templates['default_layout']:
            renderers[key] = make_renderer(env.get_template(key+tplext))

    return renderers

