pseudoscience
=======
overview
-----
Static site generator. Uses Pandoc to parse reStructuredText/Markdown. Jinja2 for templates. Simply put Markdown/reStructuredText files in your `site` folder. Compilation respects directory structure of the `site` folder and copies over non-markdown files verbatim.

install
-------
Three things needed:

  1. Python 3 (possibly 3.2 required. I've only tested on Python 3.2.3)
  2. Pandoc
  3. Jinja2
 

usage
------
There's only one usage: `python ps.py`. This deletes everything from your output directory, then goes through your site directory, compiling Markdown files and copying non-Markdown files. The directory structure of the site directory is preserved.
