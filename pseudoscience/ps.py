import sys
import os, shutil, subprocess
from glob import glob

from jinja2 import Environment, FileSystemLoader

config = {
        'site_dir': './',
        'out_dir': 'out/',
        'templates_dir': 'templates',
        'site_title': 'jackanapes'
        }


# simple wrapper class for jinja2 rendering
class Jinja2Renderer:
    def __init__(self, name):
        self.tpl_name = name

        tplext = '.html'
        self.tpl = Jinja2Renderer.env.get_template(name+tplext)

    def render(self, vs):
        self.tpl.render(vs)

    @classmethod
    def setupEnv(cls, d):
        cls.env = Environment(loader=FileSystemLoader(d, encoding='utf-8'))



class PandocConverter:
    def __init__(self):
        pass

    def convert(self, source, from_format, to_format):
        # raises OSError if pandoc is not found!
        # supported formats at http://johnmacfarlane.net/pandoc/
        p = subprocess.Popen(['pandoc', '--from=' + from_format, '--to=' + to_format, '--mathjax'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        return p.communicate(bytes(source, 'UTF-8'))[0]


class SiteChef:
    def __init__(self, config, renderer, converter):
        self.out_dir = config['out_dir']
        self.site_dir = config['site_dir']
        self.templates_dir = config['templates_dir']
        self.tpl_renderer = renderer
        self.pg_converter = converter


    def _create_folder_if_not_exists(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    def _isPage(self, fname):
        pages = ['.md', '.rst']
        return ('.' in fname) and (fname[fname.index('.'):] in pages)


    def copyDirectory(self, folder):
        print("copyDir w/ folder = "+folder+"\n\n")
        self._create_folder_if_not_exists(self.out_dir + folder)
        for fname in os.listdir(self.site_dir + folder):
            print(fname)
            if self._isPage(fname):
                site_file = self.site_dir + fname
                out_file = self.out_dir + fname
                shutil.copy(site_file, out_file)

    def renderPages(self):
        pages = ['.md', '.rst']

        self._create_folder_if_not_exists(self.out_dir)

        for fname in os.listdir(self.site_dir):

            if self._isPage(fname):
                src_fpath = self.site_dir + fname
                name = fname[:fname.index('.')]
                ext = fname[fname.index('.'):]
                pv = {'name': name}

                with open(src_fpath, 'r') as file:
                    content = file.read()
                    src_format = 'markdown' if ext == '.md' else 'rst'
                    converted = self.pg_converter.convert(content, src_format, 'html')
                    pv['content'] = bytes.decode(converted)

                target_fpath = self.out_dir + name + '.html'
                print(target_fpath+"\n\n")
                with open(target_fpath, 'w') as f:
                    f.write(str(self.tpl_renderer.render(pv)))



    def compile(self):
        self.copyDirectory('css/')
        self.copyDirectory('images/')
        self.renderPages()



def compile_site(config):
    Jinja2Renderer.setupEnv(config['templates_dir'])
    chef = SiteChef(config, Jinja2Renderer('layout'), PandocConverter())
    chef.compile()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        compile_site(config)
    else:
        print("there's no arguments right now.")
