site_title = 'my site' 
site_dir = 'site/'
out_dir = 'out/'
templates_dir = 'templates/'
pages_ext = '.md'

templates = {}
templates['default_layout'] = 'layout'
templates['default_page'] = 'page_default'

render_rules = {
    'blather/*': {'page_template': 'page_blather'},
    'index': {'page_template': 'index_content'}
}

