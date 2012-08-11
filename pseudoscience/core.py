from sys import exit, argv
from glob import glob
import os
from functools import reduce

from jinja2 import Environment, FileSystemLoader

from pseudoscience.util import *
################
## philosophy ##
################
# hakyll's notion of  fully general compilation rules where you pass around
# a compiler function that tells you how the document should be compiled
# (and where you have to specify an identity compilation function in order to
# copy, say a css file over) is obviously pretty powerful. but in practice
# there are only two compilation possibilities that I want to handle:
# 
#   - copy the file over verbatim
#   - parse the meta data, run the body through pandoc
#
# it might be wise to set up some infrastructure to be able to extend towards
# fully general compilation rules in the future, but honestly it seems pointless
# to actually implement.
#
# So in reality, the 'rules' we specify in config, we can get by with just specifying
# routing rules and which templates to use

# global vars
transform = {}
import config as cfg


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




def render_page(page_vars):
    # if folder matches a select in the render_rules
    # then use whatever templates are specified there
    tplname = cfg.templates['default_page']

    folder = page_vars['folder']
    page_name = page_vars['name']

    match_folder = folder+'*'
    match_page = folder+page_name
    for match in [match_folder, match_page]:
        if cfg.render_rules.get(match) is not None:
            if cfg.render_rules[match].get('page_template') is not None:
                tplname = cfg.render_rules[match]['page_template']

    page_content = transform[tplname].render(page_vars)
    render_layout_and_write(page_name, folder, page_vars['fullpath'], page_content)


def render_layout_and_write(page_name, folder, fullpath, content):
    fname = cfg.out_dir + fullpath

    layout_vars = {'content': content, 'title': ' > '.join(folder[1:].split('/'))+page_name}

    f = open(fname, 'w')
    f.write(str(transform[cfg.templates['default_layout']].render(layout_vars)))
    f.close()


def compile_page(in_fpath, out_fpath):
    file = open(cfg.site_dir+in_fpath, 'r')
    content = file.read()
    file.close()

    last_slash = out_fpath.rindex('/')

    pg = {'name': out_fpath[last_slash+1:out_fpath.index('.')],
          'folder': out_fpath[:last_slash+1],
          'fullpath': out_fpath,
          'content': bytes.decode(convert(content, cfg.page_format, 'html'))}

    render_page(pg)


def compile_index(out_fpath, smap):
    last_slash = out_fpath.rindex('/')
    index_vars = {
            'name': out_fpath[last_slash+1:out_fpath.index('.')],
            'folder': out_fpath[:last_slash+1],
            'fullpath': out_fpath,
            'map': smap}
    render_page(index_vars)



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



def copy_to_out(rel_file_path):
    copyanything(cfg.site_dir+rel_file_path, cfg.out_dir+rel_file_path)



def compile_file(in_fpath, out_fpath, site_map):
    if in_fpath == '/':
        compile_index(out_fpath, site_map)
    elif in_fpath.endswith(cfg.pages_ext):
        compile_page(in_fpath, out_fpath)
    else:
        copy_to_out(in_fpath)


def compile_site():
    create_transforms()
    smap = SiteMap()

    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '') + '/'

        prep_folder(cfg.out_dir+rel_folder)

        if rel_folder == '/':
            compile_file(rel_folder, index_router(rel_folder), smap.smap)

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
            if fpath.endswith(cfg.pages_ext):
                route_out = page_router(fpath)
            else:
                route_out = id_router(fpath)

            compile_file(fpath, route_out, smap.smap)
