pseudoscience
=======
overview
-----
I wrote this because I couldn't figure out how to get Jekyll to do what I wanted, which is fucking amazing since what I wanted consists entirely of this:

 - I write a bunch of markdown files and put them in a folder.
 - parse all the markdown files in a folder, generating html for them
 - allow me to loop through the files to create a list of the pages on an index page

I doctored up some hack where I used the built-in _posts folder for jekyll, and looped through with site.pages variable, but then I had to name my files using dummy dates like "2012-01-01-semigroup.md" instead of just "semigroup.md". I quickly realized that that is retarded, so I just threw this together. Totally stunning that you either a) can't do this in Jekyll or b) it's not obvious how to do this in Jekyll, but I guess Jekyll is content with being a static *blog* generator, not a static *site* generator.

install
-------
First you need to get pandoc. Yap, that Haskell-based Markdown parser/generator. Why am I using Pandoc? Because all the Python-based Markdown parsers are atrocious.

Other dependencies include PyYAML and Jinja2:

 - pip install pyyaml
 - pip install jinja2

 
future stuff
------------
I think I want to switch to mustache templates (pystache), but I tried to do this once and it definitely did not work. It escaped all my HTML after the first template render. Also the pystache documentation is non-existent. Sorry bros, thanks for the free software and all, but I'm not reading your source code to figure out how to use your library. I have *things to do*.
