from lxml import etree
from sys import exit, argv
import os
from util import *

# global vars
cfg = {}
transform = {}


def get_config():
    global cfg
    f = open('config.xml', 'r')
    cfg_ele = etree.XML(f.read())
    for var in list(cfg_ele):
        if var.tag != 'templates':
            cfg[var.tag] = var.text
        else:
            cfg['templates'] = {}

            for v in list(var):
                cfg['templates'][v.tag] = v.text

    f.close()


# set up transforms
def create_transforms():
    global transform
    build_xslt = lambda name: etree.XSLT(etree.parse(cfg['templates_dir']+name+'.xsl'))
    for trk, trv in list(cfg['templates'].items()):
        transform[trk] = build_xslt(trv)

    transform['index_content'] = build_xslt('index_content')

    
# chop off the markdown file extension
pgname_from_fname = lambda f: f[:f.find(cfg['pages_ext'])]


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
    lv['site_title'] = cfg['site_title']
    lv['content'] = {}

    tree = build_etree({'root': lv})

    root_ele = tree.getroot()
    content_ele = root_ele.find('content')
    content_ele.append(content_tree.getroot())
    
    # return ElementTree
    return etree.ElementTree(root_ele)


def write_file_from_dict(vardict, tplname, page_name, folder):
    vartree = build_etree(vardict)
    result_tree = transform[tplname](vartree)
    LV = make_layout_vars(result_tree, page_name, folder)
    write_file_from_result_tree(page_name, folder, LV)


def write_file_from_result_tree(file_name, folder, LV):
    fname = cfg['out_dir'] + folder + file_name + '.html'

    f = open(fname, 'w')
    f.write(str(transform['default_layout'](LV)))
    f.close()


def compile_page(fname, folder):
    file = open(cfg['site_dir']+folder+fname, 'r')
    content = file.read()
    file.close()

    pg = {'name': pgname_from_fname(fname),
          'path': folder,
          'content': bytes.decode(convert(content, 'markdown', 'html'))}

    write_file_from_dict({'page': pg}, 'default_page', pg['name'], pg['path'])


def compile_index(pages_dict):
    write_file_from_dict(pages_dict, 'index_content', 'index', '')


def compile_site():
    # trailingslashify
    tsify = lambda x: x+'/' if x[len(x)-1] != '/' else x

    index_vars = {}
    for o in os.walk(cfg['site_dir']):
        this_in_folder = tsify(o[0])
        this_out_folder = this_in_folder.replace(cfg['site_dir'], cfg['out_dir'])
        this_folder = this_in_folder.replace(cfg['site_dir'], '')

        prep_folder(this_out_folder)

        print(this_in_folder)

        pages = [{'page': 
                    {'name': pgname_from_fname(f),
                     'path': this_folder}
                 } for f in o[2] if f.endswith(cfg['pages_ext'])]

        if this_in_folder == cfg['site_dir']:
            index_vars['pages'] = pages
        else:
            this_folder_no_ts = this_folder[:this_folder.find('/')]
            path_list = this_folder_no_ts.split('/')

            #assign pages to the sub-dict in index_vars corresponding to the subfolder of the page
            dict_acc = index_vars
            for p in path_list[:len(path_list)-1]:
                dict_acc = dict_acc[p]

            dict_acc[path_list[len(path_list)-1]] = {'pages': pages}


        for ef in o[2]:
            print('    '+ef)
            if ef.endswith(cfg['pages_ext']):
                compile_page(ef, this_folder)
            else:
                copyanything(this_in_folder+ef, this_out_folder+ef)


    compile_index({'root': index_vars})


if __name__ == '__main__':
    if len(argv) == 1:
        get_config()
        create_transforms()
        compile_site()
    else:
        print("there's no arguments right now.")
