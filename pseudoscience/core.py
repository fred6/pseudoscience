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
        #pginfo = lambda f: {'page': {'name': pgname_from_fname(f), 'path': path+'/'}}
        #fldinfo = lambda f: {'folder': {'name': f, 'path': path+'/', 'content': {}}}

        #pages = [pginfo(f) for f in files if self._is_content_file(f)]
        #folders = [fldinfo(f) for f in folders]
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



def render_page(page_vars, compile_data):
    tplname = cfg.templates['default_page']

    folder = page_vars['folder']
    page_name = page_vars['name']

    tmp = compile_data.get('page_template') 
    if tmp is not None:
        tplname = tmp

    page_content = transform[tplname].render(page_vars)
    render_layout_and_write(page_name, folder, page_vars['fullpath'], page_content)


def render_layout_and_write(page_name, folder, fullpath, content):
    fname = cfg.out_dir + fullpath

    layout_vars = {'content': content, 'title': ' > '.join(folder[1:].split('/'))+page_name}

    f = open(fname, 'w')
    f.write(str(transform[cfg.templates['default_layout']].render(layout_vars)))
    f.close()


def make_html_vars(in_fpath, out_fpath, smap):
    content = None
    if not in_fpath.endswith('/'):
        file = open(cfg.site_dir+in_fpath, 'r')
        content = file.read()
        file.close()

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


def compile_file(in_fpath, out_fpath, site_map, compile_data):
    if out_fpath.endswith('.html'):
        render_page(make_html_vars(in_fpath, out_fpath, site_map), compile_data)
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
            if len(mr) == 1:
                compile_file(path, mr[0](path), smap.smap, mr[1])
        except psException as e:
            pass

    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '') + '/'

        prep_folder(cfg.out_dir+rel_folder)

        match_and_compile(rel_folder)


        # the logic here should be as follows:
        # for each file in this directory:
        #    call the appropriate router
        #    "compile" the file
        #
        # compilation takes the output of the router (the file path to write),
        # and the file path of the input file and uses some logic to yield output
        # content. we currently have two cases:
        #   - verbatim copy
        #   - parse metadata, run content through pandoc, call a chain of template files
        # i can see use for a third:
        #   - compress file (like minifying CSS and java)
        #   - compile css (using some language like SASS)
        #
        # i was thinking about bringing templates under the fold of of 'compilation', but
        # theres some difficulty. a jinja2 template gets 'compiled' into a compiler.
        # a reST file gets compiled into raw text

        for ef in o[2]:
            fpath = rel_folder+ef
            match_and_compile(fpath)
