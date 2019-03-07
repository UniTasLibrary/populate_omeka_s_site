"""Utility functions to do...s tuff"""
# vim: set fileencoding=utf-8 :

import re
from bs4 import BeautifulSoup, Comment
import codecs
from config import *

from omeka_interactions import download_specific_media_id, upload_items_with_media, download_site_metadata
from omeka_interactions import download_specific_page_metadata

# Functions
def print_debug(debug_message):
	debug_setting = run_verbose
	if debug_setting:
		print debug_message
	return True

# https://stackoverflow.com/questions/1276764/stripping-everything-but-alphanumeric-chars-from-a-string-in-python
def rewrite_slug(old_url):
	"""Clean old URLs.

	Rewrite old URLs (and references to them). First we do the subtitutions we
	need then strip out any other characters that might have snuck in (somehow).
	This will need to be run on every reference but should return consistent
	results so is suitable for dynamic rewrites.
	"""
	# Cut of leading ../ and trailing .html
	if old_url.endswith('.html'):
		trimmed_url = old_url.strip('../').split('.html')[0]
	elif old_url.endswith('.htm'):
		trimmed_url = old_url.strip('../').split('.htm')[0]
	else:
		trimmed_url = old_url

	# Lowercase and replace '/', ' ', and '.' as required
	lowered_url = trimmed_url.lower().replace('/', '_').replace('.', '_').replace(' ', '_').replace('%20', '_')
	# Only keep ASCII characters
	stripped_url = re.sub(r'\W+', '', lowered_url)
	return stripped_url


def check_if_processing_required(source_location):
	"""Determine if we need to process this HTML input.

	Good sources to compare with are the json temporary file or
	Omeka S API for the site we're updating.
	
	Accepts: input html location
	Returns: True (required) or False (skip this record)
	"""
	# We only need to process HTML - pictures, binaries, etc will not be embeded like this.

	if source_location.endswith('.jpg') or source_location.endswith('jpeg') or source_location.endswith('gif'):
		print_debug('No further processing required for {}'.format(source_location))
		return False

	if not (source_location.endswith('.htm') or source_location.endswith('html')):
		# Notify when skipping 'novelty' extensions
		print_debug('Skipping current file: {} does not have an html or htm extension'.format(source_location))
		return False

	# TODO: if version exists in API pass here?

	return True

def load_source_html(source_location):
	"""Gather HTML required for processing.

	Input can be anything, if desired, but here its files.
	This must return a BS object or None.
	"""
	try:
		# FIXME: This does not handle unicode in the files. Fix so I
		# have UTF-8 output after reading the file. and that files
		# read.
		opened_containing_file = codecs.open(source_location)
		html_doc = opened_containing_file.read()
		soup = BeautifulSoup(html_doc, 'html.parser')        
		# Clean up after ourselves
		opened_containing_file.close()
	except UnicodeDecodeError as udee:
		print "Error while converting {} to soup due to decoding error - {}.".format(source_location, udee)
		return None
	return soup


def extract_desired_metadata(soup_object, file_pointer):
	"""If desired, extract metadata from page.

	Runs before body processing but can be augmented
	with extra data later.

	Accepts: BS soup object
	Accepts: reference to file on disk (from os.open)
	Returns: TODO
	"""
	return None

def extract_desired_html(soup_object):
	"""Extract part of HTML we want to keep.

	# Content pages all appear to use the same layout (phew). subject guide, index, search, other supporting pages do not.
	# TitlePageHeadings; import and fix by hand (they include a heading and content in same block)

	Accepts BS object
	Returns BS object
	"""

	# "Darwin style"
	# desired_page_contents = soup_object.find('td', class_=re.compile('style5'))


	# "Companion style"
	# Index and some other pages won't work on this system, require looking for InstanceBeginEditable
	# NOTE: future revision could look for <!-- InstanceBeginEditable name="content" --> and return its parent, unsure if thats an improvement or not

	# Find first content block on page
	desired_page_contents = soup_object.find('p', class_=re.compile('BodyHeading|BodyText|Furtherreading|TitlePageHeadings|BodyHeadings|ImageCaption'))

	if not desired_page_contents:
		# support pages (index, others???) may use this but the content returned is likely to be incomplete
		desired_page_contents = soup_object.find('td', class_=re.compile('BodyHeading|BodyText|Furtherreading|TitlePageHeadings|BodyHeadings|ImageCaption'))

	if not desired_page_contents:
		print "No matching classes found in {}".format(soup_object)
		return None

	return desired_page_contents.parent



def cleanup_html_markup(dirty_html):
	"""Perform any html fixes and issues caused by the transformation.

	This could include broken quoting, unnecesary
	"smart" quotes or any other unwanted problems.
	"""
	# Cleaning HTML before further processing
	from bs4 import Comment
	comments=dirty_html.find_all(string=lambda text:isinstance(text,Comment))
	for c in comments:
		print_debug( 'Deleting {}'.format(c))
		c.extract()

	# print dirty_html
	for e in dirty_html.find_all(href=re.compile('html')):
		if not e.get('href').startswith('http'):
			e['href'] = rewrite_slug(e.get('href'))
			# print 'keeping {}'.format(e)
	for e in dirty_html.find_all(href=re.compile('htm')):
		if not e.get('href').startswith('http'):
			e['href'] = rewrite_slug(e.get('href'))
			# print 'keeping {}'.format(e)


def build_page_block_data(page_section):
	block_data = {
		"o:attachment" : [],
		"o:layout" : "html",
		"o:data" : {
		    "html" : "{}".format(page_section),
		 },
	}
	return block_data


def extract_image_name(image_path):
	if not image_path:
		return ''
	try:
		image_name = image_path.split('/')[-1]
		return image_name
	except IndexError as iee:
		print 'Unable to split {} to create a suitable image name'.format(image_path)
		if image_path.find('files/') >= 0:
			print 'File has probably been imported to omeka already, skipping'
		return ''

def generate_alt_text(image_html, image_name):
	# image_html is actually a BS object
	try:
		alt_text = image_html.get('alt')
	except AttributeError as aee:
		print '{} has no alt text, Attempting to create a suitable string using file name'.format(image_name)
		alt_text = image_name.replace('/', ' ').replace('.', ' ').replace('_', ' ').replace('%20', ' ')
	return alt_text

def check_for_then_upload_image(image_urls, image_name, image_path, alt_text, version):
	if not image_name:
		return None
	if image_name not in image_urls:
		uploaded_image = upload_items_with_media(image_name, { 'alt_text': alt_text, 'version': version, 'image_with_path': image_path})
		full_media_entry = download_specific_media_id(uploaded_image.json()['o:media'][0]['o:id'])

		if 'o:original_url' in full_media_entry:
			image_urls.update({image_name: '/{}'.format(full_media_entry['o:original_url'].strip(omekas_base_url))})
		else:
			print "Something went wrong with the API returned json for {}; it is lacking o:original_url".format(image_name)
			print full_media_entry
		return True
	else:
		print '{} has been seen before in this item set and will not be uploaded again.'.format(image_name)
		return None


def replace_known_page_slugs_list(page_ids_and_slugs):
	if not page_ids_and_slugs:
		print_debug('Updating empty starting page data from API')
	# Need to download metadata each time as page list changes
	our_sites_metadata = download_site_metadata()
	if 'o:page' in our_sites_metadata.keys():
		for site_page in our_sites_metadata['o:page']:
			# print_debug(site_page)
			# Do not query API for pages we already have. This will cut API call volume
			# Linearly to the number of pages.
			if site_page['o:id'] in page_ids_and_slugs.keys():
				continue
			# First run has no data so we probably don't need to know it can't find all these things
			our_pages_metadata = download_specific_page_metadata(site_page['o:id'])
			if our_pages_metadata:
				page_ids_and_slugs.update({site_page['o:id']: our_pages_metadata['o:slug']})

	else:
		print "our_sites_metadata did not include o:page"

	return page_ids_and_slugs

