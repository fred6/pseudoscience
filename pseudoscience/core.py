from lxml import etree
from sys import exit, argv
from glob import glob
import os
from functools import reduce

from pseudoscience.util import *

# global vars
transform = {}
import config as cfg


# set up transforms (pull all xsls from templates_dir)
def create_transforms():
    global transform

    for tpl in glob(cfg.templates_dir+'*.xsl'):
        key = tpl.replace(cfg.templates_dir, '').replace('.xsl', '')
        transform[key] = etree.XSLT(etree.parse(tpl))

    
# chop off the markdown file extension
pgname_from_fname = lambda f: f[:f.find(cfg.pages_ext)]


def build_etree(data):
    ele = build_etree_rec(data)
    return etree.ElementTree(ele)


def build_etree_rec(data):
    listify = list(data.items())

    if listify != []:
        for ele, val in listify:
            ele, val = listify[0]
            ele_root = etree.Element(ele)

            if isinstance(val, dict):
                for e,v in val.items():
                    subele = build_etree_rec({e: v})

                    if subele is not None:
                        ele_root.append(subele)
            elif isinstance(val, str):
                ele_root.text = val
            else:
                # assume list
                for sub in val:
                    subele = build_etree_rec(sub)
                    ele_root.append(subele)

        return ele_root

    else:
        return None


def make_layout_vars(content_tree, page_title, page_path):
    lv = {}
    lv['page_title'] = page_title
    lv['page_path'] = page_path
    lv['site_title'] = cfg.site_title
    lv['content'] = {}

    tree = build_etree({'root': lv})

    root_ele = tree.getroot()
    content_ele = root_ele.find('content')
    content_ele.append(content_tree.getroot())
    
    # return ElementTree
    return etree.ElementTree(root_ele)


def write_file_from_dict(vardict, page_name, folder):
    # if folder matches a select in the render_rules
    # then use whatever templates are specified there
    tplname = cfg.templates['default_page']

    match_folder = folder+'*'
    match_page = folder+page_name
    for match in [match_folder, match_page]:
        if cfg.render_rules.get(match) is not None:
            if cfg.render_rules[match].get('page_template') is not None:
                tplname = cfg.render_rules[match]['page_template']

    vartree = build_etree(vardict)
    result_tree = transform[tplname](vartree)
    LV = make_layout_vars(result_tree, page_name, folder)
    write_file_from_result_tree(page_name, folder, LV)


def write_file_from_result_tree(file_name, folder, LV):
    fname = cfg.out_dir + folder + file_name + '.html'

    f = open(fname, 'w')
    f.write(str(transform[cfg.templates['default_layout']](LV)))
    f.close()


def compile_page(fname, folder):
    file = open(cfg.site_dir+folder+fname, 'r')
    content = file.read()
    file.close()

    pg = {'name': pgname_from_fname(fname),
          'path': folder,
          'content': bytes.decode(convert(content, cfg.page_format, 'html'))}

    write_file_from_dict({'page': pg}, pg['name'], pg['path'])


def compile_index(pages_dict):
    write_file_from_dict(pages_dict, 'index', '')



class SiteMap():
    def __init__(self):
        self.smap = {}

    def add_to_map(self, path, files):
        pginfo = lambda f: {'page': {'name': pgname_from_fname(f), 'path': path+'/'}}
        pages = [pginfo(f) for f in files if self._is_content_file(f)]
        folder_dict = {'pages': pages, 'subs': []}

        if path == '':
            self.smap = folder_dict
        elif pages != []:
            path_list = path.split('/')

            # the last in path_list is not created yet so only traverse up to second-to-last
            # reduce just turns [a, b, c, d] into self.smap[a][b][c].
            # afterwards we create self.smap[a][b][c][d]
            parent_folder = reduce(lambda D, k: D['subs'][k], path_list[:-1], self.smap)
            parent_folder[path_list[-1]] = folder_dict


    def _is_content_file(self, filename):
        return filename.endswith(cfg.pages_ext)


def copy_to_out(rel_file_path):
    copyanything(cfg.site_dir+rel_file_path, cfg.out_dir+rel_file_path)


def compile_site():
    create_transforms()
    smap = SiteMap()

    for o in os.walk(cfg.site_dir):
        rel_folder = o[0].replace(cfg.site_dir, '')
        smap.add_to_map(rel_folder, o[2])

        prep_folder(cfg.out_dir+rel_folder)
        for ef in o[2]:
            if ef.endswith(cfg.pages_ext):
                compile_page(ef, rel_folder+'/')
            else:
                copy_to_out(rel_folder+'/'+ef)


    compile_index({'root': smap.smap})
