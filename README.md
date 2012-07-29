pseudoscience
=======
overview
-----
Static site generator. Uses Pandoc for Markdown parsing/HTML generation and an XSLT templating system based on lxml. Simply put Markdown files in your `site` folder. Compilation respects directory structure of the `site` folder and copies over non-markdown files verbatim.

install
-------
Three things needed:

  1. Python 3 (possibly 3.2 required. I've only tested on Python 3.2.3)
  2. Pandoc
  3. lxml
 

usage
------
There's only one usage: `python ps.py`. This deletes everything from your output directory, then goes through your site directory, compiling Markdown files and copying non-Markdown files. The directory structure of the site directory is preserved.

In order to have everything work you need to edit the XSLs in the templates folder.
 
