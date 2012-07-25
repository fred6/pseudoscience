from lxml import etree
import os, yaml, shutil, errno, subprocess
from sys import exit, argv

# get config
f = open('config.yaml', 'r')
cfg = yaml.load(f.read())
f.close()

########
# TODO #
########
# get rid of yaml. just use XML config
# function for converting dictionaries and lists into xml files
# dictionary key/value => element
# list of dictionaries => repeated  element?
# or should it be 'key': [list, list, list]
# because otherwise how do you enforce that theyre the same
# if you just do [{key: val}, {key: val}, {key, val}]

    
#http://nixtu.blogspot.com/2011/11/pandoc-markup-converter.html
def convert(source, from_format, to_format):
    # raises OSError if pandoc is not found!
    # supported formats at http://johnmacfarlane.net/pandoc/
    p = subprocess.Popen(['pandoc', '--from=' + from_format, '--to=' + to_format],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    return p.communicate(bytes(source, 'UTF-8'))[0]


# http://stackoverflow.com/a/1994840
def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def rmanything(thing):
    try:
        shutil.rmtree(thing)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            os.remove(thing)
        else: raise


class SiteCompiler():
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(cfg['templates_dir'], encoding='utf-8'))

        # each tpl entry is an lxml.etree.ElementTree
        tpl = {}
        tpl['layout'] = etree.parse(cfg['templates_dir'] + 'layout.tpl')
        tpl['page_content'] = etree.parse(cfg['templates_dir'] + 'page_content.tpl')
        tpl['index_content'] = etree.parse(cfg['templates_dir'] + 'index_content.tpl')

        self.transform['layout'] = etree.XSLT(tpl['layout'])
        self.transform['index'] = etree.XSLT(tpl['index_content'])
        self.transform['page'] = etree.XSLT(tpl['page_content'])


    def _clean_up(self):
        # make output directory if it doesnt exist
        if not os.path.exists(cfg['out_dir']):
            os.makedirs(cfg['out_dir'])

        # clean out old files
        for f in os.listdir(cfg['out_dir']):
            rmanything(cfg['out_dir']+f)


    def runXSLT(self, transform_name, var_tree):
        return self.transform[transform_name](var_tree)

    def _set_layout_vars(self, page_tpl, page_vars, **kwargs):
        if kwargs.get('page_name') != None:
            titlestr = ' - ' + kwargs['page_name']
        else:
            titlestr = ''

        root = etree.Element('root')
        title = etree.SubElement(root, 'title')
        content = etree.SubElement(root, 'content')
        title.text(cfg['site_title']+titlestr)
        # page_vars needs to be etree.ElementTree first.
        content.text(str(self.runXSLT(page_tpl, page_vars)))
        self.LV = etree.ElementTree(root)


    # do one level for now.
    def _build_etree(self, data):
        e = {}
        root = data.keys()[0]
        e[root] = etree.Element(root)

        if isinstance(data[root], dict):
            for k in data[root].keys():
                e['sub_'+k] = etree.SubElement(e[root], k)
                e['sub_'+k].text(data[root][k])

        else:
            # assume its a list
            for i in data[root]:
                curr_ele = i.keys()[0]
                curr_val = i.values()[0]
                e['sub_'+curr_ele] = etree.SubElement(e[root], curr_ele)
                e['sub_'+curr_ele].text(curr_val)



    def _write_file(self, file_name):
        fname = cfg['out_dir'] + file_name + '.html'
        f = open(fname, 'w')
        f.write(str(self.runXSLT('layout', self.LV)))
        f.close()

    def _compile_page(self, fname):
        file = open(cfg['site_dir']+fname, 'r')
        content = file.read()
        file.close()

        pg = {'name': fname[:fname.find(cfg['pages_ext'])],
              'content': bytes.decode(convert(content, 'markdown', 'html'))}

        self._set_layout_vars('page_content', {'page': pg}, page_name=pg['name'])
        self._write_file(pg['name'])

        return pg['name']


    def compile(self):
        self._clean_up()
        pages = []

        # read input directory
        for ef in os.listdir(cfg['site_dir']):
            if ef.endswith(cfg['pages_ext']):
                page_info = self._compile_page(ef)
                pages.append({'name': page_info})
            else:
                copyanything(cfg['site_dir']+ef, cfg['out_dir']+ef)

        # compile index file
        self._set_layout_vars('index_content', {'pages': pages})
        self._write_file('index')


if __name__ == '__main__':
    if len(argv) == 1:
        sc = SiteCompiler()
        sc.compile()
    else:
        print("there's no arguments right now.")
