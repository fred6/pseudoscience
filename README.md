pseudoscience
=======
overview
-----
I wrote this because I couldn't figure out how to get Jekyll to do what I wanted, which is fucking amazing since what I wanted consists entirely of this:

 - I write a bunch of markdown files and put them in a folder.
 - parse all the markdown files in a folder, generating html for them
 - allow me to loop through the files to create a list of the pages on an index page

I doctored up some hack where I used the built-in _posts folder for jekyll, and looped through with site.pages variable, but then I had to name my files using dummy dates like "2012-01-01-semigroup.md" instead of just "semigroup.md". I quickly realized that that is retarded, so I just threw this together. Totally stunning that you either a) can't do this in Jekyll or b) it's not obvious, but I guess Jekyll is content with being a static *blog* generator, not a static *site* generator.

install
-------
After downloading this repo, you need to get pyyaml, jinja2, and misaka:

pip install pyyaml
pip install jinja2
pip install misaka

I guess there's a distutils module or something in the python stdlib (I'm not super familiar with python), and it looks like lots of people use it. But apparently python 3.3 is deprecating it. so i think i'm going to wait on that before implementing. or just switch to python v3.3-only, maybe when the first beta is released.

