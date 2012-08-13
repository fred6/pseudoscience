import os, re
from functools import reduce
from collections import namedtuple

from pseudoscience.util import *
from pseudoscience.renderers import jinja2_renderers

import config as cfg

# parse rules
def parse_rules():
    SiteRule = namedtuple('SiteRule', 'pattern, router, renderer')
    cfg.rules = []
    for r in cfg.r:
        cfg.rules.append(SiteRule(r[0], r[1], r[2] if len(r) == 3 else cfg.templates['default_page']))


# chop off the (first) file extension
pgname_from_fname = lambda f: f[:f.find('.')]


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
                for f in files if file_is_page(f)]
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


# helper
def file_is_page(filename):
    page_extensions = ['.md', '.rst']
    if '.' in filename:
        ext = filename[filename.index('.'):]
        return ext in page_extensions
    else:
        return False


def parse_file(in_fpath, out_fpath):
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


def copy_to_out(rel_file_path):
    copyanything(cfg.site_dir+rel_file_path, cfg.out_dir+rel_file_path)


def compile_file(in_fpath, out_fpath, site_map, renderer):
    print('compile_file: '+in_fpath+';'+out_fpath)
    if out_fpath.endswith('.html'):
        parse_res = parse_file(in_fpath, out_fpath)
        parse_res['map'] = site_map
        renderer(parse_res)
    else:
        copy_to_out(in_fpath)


def compile_site():
    # establish renderers
    renderers = jinja2_renderers(cfg)

    def match_rule(fpath):
        for r in cfg.rules:
            restr = '\A' + r[0].replace('.', '\.').replace('*', '[^/]+') + '\Z'
            if re.match(restr, fpath):
                return (globals()[r.router], renderers[r.renderer])

        raise psException('no route found')

    def match_and_compile(path):
        try:
            mr = match_rule(path)
            compile_file(path, mr[0](path), smap.smap, mr[1])
        except psException as e:
            pass

    parse_rules()
    smap = SiteMap()

    # compile input folder
    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '') + '/'
        prep_folder(cfg.out_dir+rel_folder)

        match_and_compile(rel_folder)

        for ef in o[2]:
            fpath = rel_folder+ef
            match_and_compile(fpath)
