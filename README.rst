Background
==========

According to its website ".. `Omeka S`_ is a next-generation web publishing
platform for institutions interested in connecting digital cultural heritage
collections with other resources online."

.. _`Omeka S`: https://omeka.org/s/


Which sounds a lot nicer thean the old static Dreamweaver sites we had hanging
around! Since I couldn't `find something`_ which would allow me to import those
sites I write this set of scripts to fill that need. They are domain specific
but I've made an attempt to keep them fairly flexible for someone who wants to
customise them.

.. _`find something`: https://forum.omeka.org/t/how-to-import-html-pages-for-a-site/7950

Other options - like displaying the current sites via iframe, a PHP backed
plugin to read the files on disk, and others - didn't seem to offer a
meaningful benefit over showing the sites statically but didn't give as much of
the benefits of Omeka S as we wanted.

The scripts (as written) require all pages share specific attributes as thats
what our pages have; the relevant functions could be augmented to capture
multiple values or behave differently per page if desired.


Configuration
=============

Site
----

A Site must be created, along with an Item Set for storing media within.


Project
-------

Configuration is done in config.py, at a minimum the following values need to
be set:

::

	website_root_on_disk = '/path/to/files'


	omekas_base_url = 'https://export.example.org/'
	omekas_site_id = 16
	omekas_item_set_id = 929
	# Psudorandom strings, generate via admin > user > Api keys
	credential_params = {
	    "key_identity": "identity",
	    "key_credential": "credential"
	}

See config.py.example for other options.


Usage
=====

Adapt (as required) utility_functions.py and a \*_to_omeka_s.py script then run
it to proesss an existing site in to json then upload to Omeka S via its API.

The current implementation uploads chunks of HTML in Omeka S blocks but can
(and maybe one day will) be expanded to process some HTML to Omeka S blocks.

Once customised, install requirements

::
	pip install -r requirements.txt

then run your script

::
	python27 foo_to_omeka_s.py


After importing be sure to check for data validity, including:
- did you import a contents or navigation page? consider replacing it with an Omeka S generated equivalent
- images are displaying correctly
- pages link through to each other correctly


Don't like your pages?
----------------------

If your pages have a systemic issue delete them with `delete_all_pages.py` and
rerun. Items, Media and the top level Site will be unaffected.


Running tests
-------------

::
	pytest --cov


Known issues
============

* Error handling is sparse, and real world usage minimal.
* If no small version of an image exists (there is no sub <img> tag) the outer image (in <a>) is not reprocessed.
* Some details are hard coded (in scripts or config) rather than gathered from API
* No tests for main script
* f/foo.html linking to f/bar.html will generate a link to the slug bar, not the slug f_bar which it needs.


Future enhancements
===================

I've made `quite a few discoveries`_ already but there are lots of known
enhancements for this script, but none were necesary enough to be done up
front.

.. _`quite a few discoveries`: https://forum.omeka.org/t/example-api-usage-using-curl/8083

Most significant are:

* Python 3 support
* Replacing HTML data blocks containing images with an Image data block
* Actually, fix all instances of HTML shoved in an HTMLblock rather than using a proper Omeka S block
* Improved processing necessity checks
* json is currently text substituted in to templates, should be python objects

Other possible enhancements include:

* Creating the required Item Set and Website within Omeka S automatically
* Nice API search for media instead of pulling all media every page processed


Contributing and issues
=======================

Please get in touch `via GitHub`_ for any issues or feedback. Contributions are
also very welcome ; feel free to open a PR directly or open an issue to discuss
first.

.. _`via GitHub`: https://github.com/UniTasLibrary

Contributing guidelines
-----------------------

Please try and maintain (or improve) test coverage in pull requests.

