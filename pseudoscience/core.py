import os, re
from functools import reduce
from collections import namedtuple

from pseudoscience.util import *
from pseudoscience.renderers import jinja2_renderers, make_id_renderer, convert

import config as cfg

# Pseudoscience exception
class psException(Exception):
    def __init__(self, value):
        self.value = value


# parse rules
def parse_rules(renderers):
    SiteRule = namedtuple('SiteRule', 'pattern, router, renderer')
    cfg.rules = []
    for r in cfg.r:
        if r[2][0] == 'id':
            renderer = renderers['_id']
        elif r[2][0] == 'page':
            if len(r[2]) == 2:
                renderer = renderers[r[2][1]]
            else:
                renderer = renderers[cfg.templates['default_page']]

        cfg.rules.append(SiteRule(r[0], globals()[r[1]], renderer))


# chop off the (first) file extension
chop_file_ext = lambda f: f[:f.find('.')]


# Routers
def id_router(fpath):
    return fpath

def page_router(fpath):
    return chop_file_ext(fpath)+'.html'

def index_router(fpath):
    return fpath+'index.html'


class SiteMap():
    def __init__(self):
        self.smap = {}
        for o in os.walk(cfg.site_dir):
            rel_folder = o[0].replace(cfg.site_dir, '') + '/'
            self.add_to_map(rel_folder, o[1], o[2])


    def add_to_map(self, path, folders, files):
        pages = [(chop_file_ext(f), {'title': '', 'path': path}) 
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


def match_rule(fpath):
    for r in cfg.rules:
        restr = '\A' + r[0].replace('.', '\.').replace('*', '[^/]+') + '\Z'
        if re.match(restr, fpath):
            return (r.router, r.renderer)

    raise psException('no route found')


def match_and_compile(path):
    try:
        mr = match_rule(path)
        out_path = mr[0](path)

        def should_compile_file(in_path, out_path):
            in_file = cfg.site_dir + in_path
            out_file = cfg.out_dir + out_path

            return (not os.path.exists(out_file) or 
                os.path.getmtime(in_file) > os.path.getmtime(out_file))

        if should_compile_file(path, out_path):
            print('compiling: '+path+'; '+out_path)
            mr[1](path, out_path)

    except psException as e:
        pass


def compile_site():
    smap = SiteMap()

    # establish renderers
    renderers = jinja2_renderers(cfg, smap.smap)
    renderers['_id'] = make_id_renderer(cfg)

    parse_rules(renderers)

    # compile input folder
    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '') + '/'
        match_and_compile(rel_folder)

        for ef in o[2]:
            fpath = rel_folder+ef
            match_and_compile(fpath)
