pseudoscience
=======
overview
-----
Barebones static site generator. You can really only copy directories verbatim and parse markdown/reStructuredText files in the root.

It uses pandoc for markup -> HTML conversion and jinja2 for HTML templates.

I am strongly considering replacing this script with a Makefile.

install
-------
Just download it. You need Python 3, not sure which version in particular (I've run it on 3.3.0 only)


todo
------
It needs to clear out files that no longer exist in the source. Right now I'm not checking that. I'll get to it later.
