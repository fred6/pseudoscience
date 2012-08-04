site_title = 'my site' 
site_dir = 'site/'
out_dir = 'out/'
templates_dir = 'templates/'
pages_ext = '.md'

templates = {}
templates['default_layout'] = 'layout'
templates['default_page'] = 'page_default'

render_rules = {}
render_rules['blather/*'] = {'page_template': 'page_blather'}
render_rules['index'] = {'page_template': 'index_content'}

