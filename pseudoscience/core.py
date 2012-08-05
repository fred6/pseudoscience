from sys import exit, argv
from glob import glob
import os
from functools import reduce

from jinja2 import Environment, FileSystemLoader

from pseudoscience.util import *

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


def render_page(page_vars):
    # if folder matches a select in the render_rules
    # then use whatever templates are specified there
    tplname = cfg.templates['default_page']

    folder = page_vars['path']
    page_name = page_vars['name']

    match_folder = folder+'*'
    match_page = folder+page_name
    for match in [match_folder, match_page]:
        if cfg.render_rules.get(match) is not None:
            if cfg.render_rules[match].get('page_template') is not None:
                tplname = cfg.render_rules[match]['page_template']

    page_content = transform[tplname].render(page_vars)
    render_layout_and_write(page_name, folder, page_content)


def render_layout_and_write(page_name, folder, content):
    fname = cfg.out_dir + folder + page_name + '.html'

    layout_vars = {'content': content, 'title': ' > '.join(folder[1:].split('/'))+page_name}

    f = open(fname, 'w')
    f.write(str(transform[cfg.templates['default_layout']].render(layout_vars)))
    f.close()


def compile_page(fname, folder):
    file = open(cfg.site_dir+folder+fname, 'r')
    content = file.read()
    file.close()

    pg = {'name': pgname_from_fname(fname),
          'path': folder,
          'content': bytes.decode(convert(content, cfg.page_format, 'html'))}

    render_page(pg)


def compile_index(smap):
    index_vars = {
            'name': 'index',
            'path': '/',
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


def compile_site():
    create_transforms()
    smap = SiteMap()

    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '') + '/'

        prep_folder(cfg.out_dir+rel_folder)
        for ef in o[2]:
            if ef.endswith(cfg.pages_ext):
                compile_page(ef, rel_folder)
            else:
                copy_to_out(rel_folder+ef)


    compile_index(smap.smap)
