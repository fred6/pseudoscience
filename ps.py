from lxml import etree
from sys import exit, argv
import os
from util import *

# get config
cfg = {}
f = open('config.xml', 'r')
cfg_ele = etree.XML(f.read())
for var in list(cfg_ele):
    cfg[var.tag] = var.text
f.close()


# set up transforms
transform = {}
for tr_name in ['layout', 'index_content', 'page_content']:
    tpl = etree.parse(cfg['templates_dir'] + tr_name + '.xsl')
    transform[tr_name] = etree.XSLT(tpl)


def build_etree(data):
    ele = build_etree_rec(data)
    return etree.ElementTree(ele)


def build_etree_rec(data):
    # make a 'root' element out of the top-level dict key
    listify = list(data.items())

    print('@@@@@@@@@@@@@@@@@@@@@@@@@@ IN BUILD_ETREE_REC: LISTIFY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    print(listify)
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@ IN BUILD_ETREE_REC: END LISTIFY @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    if listify != []:
        for ele, val in listify:
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@ IN BUILD_ETREE_REC: inside for ELE/val @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            print(ele)
            print(val)
            print('@@@@@@@@@@@@@@@@@@@@@@@@@@ IN BUILD_ETREE_REC: inside for ELE/val AFTER! @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

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

        print('@@@@@@@@@@@@@@@@@@@@@@@@@@ IN BUILD_ETREE_REC: ELE_ROOT @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(etree.tostring(ele_root))

        return ele_root

    else:
        return None


def build_layout_tree(content_tree, page_title):
    lv = {}

    if page_title != 'index':
        lv['page_title'] = page_title

    lv['site_title'] = cfg['site_title']
    lv['content'] = {}

    tree = build_etree({'root': lv})

    if page_title == 'TODO':
        print('$$$$$$$$$$$$$$$$$$$$$$$$$')
        print(etree.tostring(tree))
        print(str(content_tree))
        print('$$$$$$$$$$$$$$$$$$$$$$$$$')

    root_ele = tree.getroot()
    content_ele = root_ele.find('content')
    content_ele.append(content_tree.getroot())
    
    # return ElementTree
    return etree.ElementTree(root_ele)


def write_file_from_dict(tplname, vdict, page_title):
    if page_title == 'TODO':
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@ VDICT @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(vdict)

    bev = build_etree(vdict)

    if page_title == 'TODO':
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@ BUILD ETREE VDICT @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(etree.tostring(bev))

    result_tree = transform[tplname](bev)

    if page_title == 'TODO':
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@ RESULT_TREE @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(str(result_tree))

    final_result_tree = transform['layout'](build_layout_tree(result_tree, page_title))

    if page_title == 'TODO':
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@ FINAL_RESULT_TREE @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print(str(final_result_tree))

    write_file_from_result_tree(page_title, final_result_tree)


def write_file_from_result_tree(file_name, result_tree):
    fname = cfg['out_dir'] + file_name + '.html'

    f = open(fname, 'w')
    f.write(str(result_tree))
    f.close()


def compile_page(fname):
    file = open(cfg['site_dir']+fname, 'r')
    content = file.read()
    file.close()

    pgvars = {'name': fname[:fname.find(cfg['pages_ext'])],
              'content': bytes.decode(convert(content, 'markdown', 'html'))}

    write_file_from_dict('page_content', pgvars, pgvars['name'])

    return pgvars['name']


def compile_index(pages_dict):
    write_file_from_dict('index_content', pages_dict, 'index')


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
