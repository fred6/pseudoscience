from lxml import etree
import os
from sys import exit, argv

from util import *

# get config
cfg = {}
f = open('config.xml', 'r')
cfg_ele = etree.XML(f.read())
for var in list(cfg_ele):
    cfg[var.tag] = var.text
f.close()

# create transforms
# each tpl is an lxml.etree.ElementTree
transform = {}
for tplname in ['layout', 'page_content', 'index_content']:
    tpl = etree.parse(cfg['templates_dir'] + tplname + '.xsl')
    transform[tplname] = etree.XSLT(tpl)


def build_etree(data):
    ele = build_etree_rec(data)
    return etree.ElementTree(ele)


def build_etree_rec(data):
    # make a 'root' element out of the top-level dict key
    ele, val = list(data.items())[0]
    ele_etree = etree.Element(ele)

    if isinstance(val, dict):
        subele = build_etree_rec(val)
        ele_etree.append(subele)
    elif isinstance(val, str):
        ele_etree.text = val
    else:
        # assume list
        for sub in val:
            subele = build_etree_rec(sub)
            ele_etree.append(subele)

    return ele_etree


def runXSLT(transform_name, var_tree):
    return transform[transform_name](var_tree)


def write_file(file_name, LV):
    fname = cfg['out_dir'] + file_name + '.html'
    f = open(fname, 'w')
    f.write(str(runXSLT('layout', LV)))
    f.close()


def make_layout_vars(page_tpl, page_vars, page_name):
    root = etree.Element('root')
    site_title = etree.SubElement(root, 'site_title')
    site_title.text = cfg['site_title']

    if page_name != 'index':
        page_title = etree.SubElement(root, 'page_title')
        page_title.text = page_name

    content = etree.SubElement(root, 'content')

    content_tpl_run = runXSLT(page_tpl, page_vars)
    contentroot = content_tpl_run.getroot()
    contentsub = content.append(content_tpl_run.getroot())

    return etree.ElementTree(root)


def write_file_from_dict(vardict, tplname, page_name):
    vartree = build_etree(vardict)
    LV = make_layout_vars(tplname, vartree, page_name)
    write_file(page_name, LV)


def compile_page(fname):
    file = open(cfg['site_dir']+fname, 'r')
    content = file.read()
    file.close()

    pg = {'name': fname[:fname.find(cfg['pages_ext'])],
          'content': bytes.decode(convert(content, 'markdown', 'html'))}

    write_file_from_dict({'page': pg}, 'page_content', pg['name'])
    return pg['name']


def compile_index(pages_dict):
    write_file_from_dict(pages_dict, 'index_content', 'index')


def compile_site():
    clean_up(cfg['out_dir'])
    pages = []

    # read input directory
    for ef in os.listdir(cfg['site_dir']):
        if ef.endswith(cfg['pages_ext']):
            page_info = compile_page(ef)
            pages.append({'page': {'name': page_info}})
        else:
            copyanything(cfg['site_dir']+ef, cfg['out_dir']+ef)

    compile_index({'pages': pages})


if __name__ == '__main__':
    if len(argv) == 1:
        compile_site()
    else:
        print("there's no arguments right now.")
