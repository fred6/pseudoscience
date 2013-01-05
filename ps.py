import sys
import os, shutil, subprocess
from glob import glob

from jinja2 import Environment, FileSystemLoader

config = {
        'site_dir': './',
        'out_dir': 'out/',
        'templates_dir': 'templates',
        'site_title': 'Jackanapes'
        }


# simple wrapper class for jinja2 rendering
class Jinja2Renderer:
    def __init__(self, name):
        self.tpl_name = name

        tplext = '.html'
        self.tpl = Jinja2Renderer.env.get_template(name+tplext)

    def render(self, vs):
        return self.tpl.render(vs)

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
        for c in config:
            setattr(self, c, config[c])

        self.tpl_renderer = renderer
        self.pg_converter = converter


    def _create_folder_if_not_exists(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)

    def _isPage(self, fname):
        pages = ['.md', '.rst']
        return ('.' in fname) and (fname[fname.index('.'):] in pages)


    # assumes you feed in the trailing slash
    def copyDirectory(self, folder):
        src_folder = self.site_dir + folder
        tgt_folder = self.out_dir + folder
        print("copyDir w/ folder = "+folder)
        self._create_folder_if_not_exists(tgt_folder)
        for fname in os.listdir(src_folder):
            site_file = src_folder + fname
            out_file =  tgt_folder + fname
            print(" -- copying "+site_file+" to "+out_file)
            shutil.copy(site_file, out_file)

        print("\n")


    def renderPages(self):
        print('renderPages')
        pages = ['.md', '.rst']
        self._create_folder_if_not_exists(self.out_dir)

        for fname in os.listdir(self.site_dir):

            if self._isPage(fname):
                src_fpath = self.site_dir + fname
                name = fname[:fname.index('.')]
                ext = fname[fname.index('.'):]
                pv = {'title': self.site_title + ' - ' + name}

                with open(src_fpath, 'r') as file:
                    content = file.read()
                    src_format = 'markdown' if ext == '.md' else 'rst'
                    converted = self.pg_converter.convert(content, src_format, 'html')
                    pv['content'] = bytes.decode(converted)

                target_fpath = self.out_dir + name + '.html'
                print(' -- '+target_fpath)
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
