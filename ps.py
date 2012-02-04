import os, yaml, misaka
from sys import exit, argv
from jinja2 import Environment, FileSystemLoader

# get config
f = open('config.yaml', 'r')
cfg = yaml.load(f.read())
f.close()


def read_entries():
    for ef in os.listdir(cfg['entries_dir']):
        if ef.endswith(cfg['entries_ext']):
            file = open(cfg['entries_dir']+ef, 'r')
            content = file.read()
            file.close()

            ents = []

            for y in yaml.load_all(content):
              y['body'] = misaka.html(y['body'])
              ents.append(y)

            ents.reverse()

            yield {'name': ef[:ef.find(cfg['entries_ext'])],
                   'entries': ents}


class TemplateRenderer():
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(cfg['templates_dir'], encoding='utf-8'))
        self.tpl = {}
        self.tpl['layout'] = self.env.get_template('layout.tpl')
        self.tpl['entries_content'] = self.env.get_template('entries_content.tpl')
        self.tpl['index_content'] = self.env.get_template('index_content.tpl')

    def render_all(self):
        # make output directory if it doesnt exist
        if not os.path.exists(cfg['out_dir']):
            os.makedirs(cfg['out_dir'])

        # remove old html files
        for f in os.listdir(cfg['out_dir']):
            if f.endswith(".html"):
                os.remove(cfg['out_dir']+f)

        chunks = []

        # render chunk pages
        for ch in read_entries():
            ent_vars = {'entries': ch['entries']}
            layout_vars = {
              'content': self.tpl['entries_content'].render(ent_vars)
            }
            
            f = open(cfg['out_dir']+ch['name']+'.html', 'w')
            f.write(self.tpl['layout'].render(layout_vars))
            f.close()

            chunks.append({'name': ch['name']})


        # render index
        index_vars = {'chunks': chunks}
        layout_vars = {
          'content': self.tpl['index_content'].render(index_vars)
        }
            
        f = open(cfg['out_dir']+'index.html', 'w')
        f.write(self.tpl['layout'].render(layout_vars))
        f.close()


if __name__ == '__main__':
    if len(argv) == 1:
        tr = TemplateRenderer()
        tr.render_all()
    else:
        print("there's no arguments right now.")
