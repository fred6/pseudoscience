from sys import exit, argv
from glob import glob
import os, re
from functools import reduce
from collections import namedtuple

from jinja2 import Environment, FileSystemLoader

from pseudoscience.util import *

# global vars
transform = {}
import config as cfg

# parse rules
def parse_rules():
    SiteRule = namedtuple('SiteRule', 'pattern, router, options')
    cfg.rules = []
    for r in cfg.r:
        cfg.rules.append(SiteRule(r[0], r[1], r[2] if len(r) == 3 else {}))


# set up transforms (pull all xsls from templates_dir)
def create_transforms():
    global transform

    env = Environment(loader=FileSystemLoader(cfg.templates_dir, encoding='utf-8'))
    tplext = '.html'
    for tpl in glob(cfg.templates_dir+'/*'+tplext):
        key = tpl.replace(cfg.templates_dir+'/', '').replace(tplext, '')
        transform[key] = env.get_template(key+tplext)

    
# chop off the markdown file extension
pgname_from_fname = lambda f: f[:f.find(cfg.pages_ext)]


# Routers
def id_router(fpath):
    return fpath

def page_router(fpath):
    return pgname_from_fname(fpath)+'.html'

def index_router(fpath):
    return fpath+'index.html'


# Pseudoscience exception
class psException(Exception):
    def __init__(self, value):
        self.value = value


class SiteMap():
    def __init__(self):
        self.smap = {}
        for o in os.walk(cfg.site_dir):
            rel_folder = o[0].replace(cfg.site_dir, '') + '/'

            self.add_to_map(rel_folder, o[1], o[2])


    def add_to_map(self, path, folders, files):
        pages = [(pgname_from_fname(f), {'title': '', 'path': path}) 
                for f in files if self._is_content_file(f)]
        folders = [(f, {'content': {}, 'path': path}) 
                for f in folders]
        folder_dict = {'pages': dict(pages), 'folders': dict(folders)}

        if path == '/':
            self.smap = folder_dict
        elif pages != []:
            path_list = path[1:-1].split('/')

            # the last in path_list is not created yet so only traverse up to second-to-last
            # reduce just turns [a, b, c, d] into self.smap[a][b][c].
            # afterwards we create self.smap[a][b][c][d]
            parent_folder = reduce(lambda D, k: D['folders'][k], path_list[:-1], self.smap)
            parent_folder['folders'][path_list[-1]]['content'] = folder_dict 

    def _is_content_file(self, filename):
        return filename.endswith(cfg.pages_ext)


def make_renderer(layout_name=cfg.templates['default_layout'], page_name=None):
    default = cfg.templates.get('default_page')

    if page_name is not None:
        page_template = transform[page_name]
    elif default is not None:
        page_template = transform[default]
    else:
        raise psException('cannot make renderer, no page template supplied')

    layout_template = transform[layout_name]

    def renderer(pg_vars):
        page_content = page_template.render(pg_vars)
        nav = ' > '.join(pg_vars['folder'][1:].split('/')) + pg_vars['name']
        layout_vars = {'content': page_content, 'title': nav}

        fname = cfg.out_dir + pg_vars['fullpath']
        with open(fname, 'w') as f:
            f.write(str(layout_template.render(layout_vars)))

    return renderer


def make_html_vars(in_fpath, out_fpath, smap):
    content = None
    if not in_fpath.endswith('/'):
        with open(cfg.site_dir+in_fpath, 'r') as file:
            content = file.read()

    last_slash = out_fpath.rindex('/')
    pv = {
            'name': out_fpath[last_slash+1:out_fpath.index('.')],
            'folder': out_fpath[:last_slash+1],
            'fullpath': out_fpath,
            'map': smap}

    if content is not None:
        pv['content'] = bytes.decode(convert(content, cfg.page_format, 'html'))

    return pv


def copy_to_out(rel_file_path):
    copyanything(cfg.site_dir+rel_file_path, cfg.out_dir+rel_file_path)


def compile_file(in_fpath, out_fpath, site_map, renderer):
    if out_fpath.endswith('.html'):
        renderer(make_html_vars(in_fpath, out_fpath, site_map))
    else:
        copy_to_out(in_fpath)


def match_rule(fpath):
    for r in cfg.rules:
        restr = '\A' + r[0].replace('.', '\.').replace('*', '.+') + '\Z'
        if re.match(restr, fpath):
            return (globals()[r.router], r.options)

    raise psException('no route found')


def compile_site():
    create_transforms()
    parse_rules()
    smap = SiteMap()

    def match_and_compile(path):
        try:
            mr = match_rule(path)
            renderer = make_renderer(page_name = mr[1].get('page_template'))
            compile_file(path, mr[0](path), smap.smap, renderer)
        except psException as e:
            pass

    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '') + '/'

        prep_folder(cfg.out_dir+rel_folder)

        match_and_compile(rel_folder)

        for ef in o[2]:
            fpath = rel_folder+ef
            match_and_compile(fpath)
