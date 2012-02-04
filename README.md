ginchy.py
=======
intro
-----
A microbloggingish framework. Entries are collected in YAML files, which can contain multiple entries. My idea was to have one YAML file per month, with each YAML file being a multi-document YAML stream. An entry is represented by 2 consecutive YAML documents; the first document is the metadata, and the second is the content (just like jekyll format):

e.g.

    ---
    date: 2012 Jan 21
    tags: [python, yaml, jinja2]
    body: |
      Text goes *here*.
    ---
    date: 2012 Jan 23
    tags: [blah]
    body: |
      Another entry, in the same file. How novel.

Having to indent the entry content is annoying, I agree. Trying to find a work around. May require abandoning a full-YAML file.

You can use markdown in entry content. We use Misaka to parse markdown.


install
-------
After downloading this repo, you need to get pyyaml, jinja2, and misaka:

pip install pyyaml
pip install jinja2
pip install misaka

I guess there's a distutils module or something in the python stdlib (I'm not super familiar with python), and it looks like lots of people use it. But apparently python 3.3 is deprecating it. so i think i'm going to wait on that before implementing. or just switch to python v3.3-only, maybe when the first beta is released.


todo
------
Make more stuff configurable without editing source code.
