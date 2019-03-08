"""Transform an HTML website to Omeka S."""
# vim: set fileencoding=utf-8 :

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import os
import re
import urllib

from datetime import datetime

from config import *
from utility_functions import *
from omeka_interactions import *

start_time = datetime.now()

# TODO: A __main__ function would look really good here.

# FIXME: need to add error handling; currently walk errors are ignored
all_website_files = os.walk(website_root_on_disk)

# Download any existing pages before running script; start with empty dict
# print_debug('If resuming an existing upload there will probably be messages about pages not found in our empty starting data')
all_current_page_slugs = replace_known_page_slugs_list({})
all_current_page_slugs_length = len(all_current_page_slugs)

# Download any existing image URLS before running
new_map_for_image_urls = gather_previous_image_uploads()
print_debug('new_map_for_image_urls {}'.format(new_map_for_image_urls))

for walk_root, walk_dir, walk_file in all_website_files:
	print '\n------------ Next folder -------------\n'
	if '_notes' in walk_dir:
		walk_dir.remove('_notes')  # don't visit DreamWeaver directories
	print_debug( walk_root )
	print_debug( walk_dir )
	print_debug( walk_file )
	# Look at files in current directory
	for current_file in walk_file:
		# Buid path to our current file
		markup_file = os.path.join(walk_root, current_file)

	# FIXME: I still don't think this will work. I suspect if its a 3rd level page
	# (eg /history/something/foo.htm) the auto slug will be something_foo not
	# history_something_foo

		# Links are relative to website root, this assembles what will
		# be the path for the slug so it matches internal links
		full_file_slug = rewrite_slug('{}/{}'.format(walk_root.split(website_root_on_disk)[1], current_file))
		short_file_slug = rewrite_slug(current_file)

		# This skip is silent, check_if_processing_required outputs notices
		if not check_if_processing_required(markup_file):
			continue
		# Needs to be below the html skip-check in check_if_processing_required
		print '\n===========\n'

		# Remove later when listing every file not needed
		print "Current file is {}, slug is {}".format(current_file, full_file_slug)

		# Take the reference to the file on disk and actually open it up
		html_soup = load_source_html(markup_file)
		if not html_soup:
			print "Skipping {}, no soup returned".format(markup_file)
			continue

		# extract_desired_metadata currently returns None, this project doesn't need it.
		usable_metadata = extract_desired_metadata(markup_file, html_soup)

		# Extract main section of HTML we want to work with - page body.
		# This is a bs4.element.Tag
		page_body = extract_desired_html(html_soup)
 		if not page_body:
 			print 'Skipping {}, no HTML extracted from page body'.format(current_file)
 			continue


		# print_debug(page_body)

		print_debug('\nProcessing images\n')

		# Darwin
		# all_page_images_html = page_body.find_all(href=re.compile("images", re.IGNORECASE))
		# Companion
		all_page_images_html = page_body.find_all(src=re.compile("images", re.IGNORECASE))
		# print type(all_page_images_html)
		print_debug('All page images {}'.format(all_page_images_html))

		# Build a list of all images used on the page to try and reduce duplicate uploads
		# If an image is used multiple times with different alt text only the first will
		# be used.

		for current_link_html in all_page_images_html:
			full_size_image_path = current_link_html.get('src')

			# TTBOMK no page in the current site has sub images so setting to nothing
			# Extract any sub image - those used for display
			sub_image_html = None
			# There isn't always an image, so check before finding image path
			if sub_image_html:
				small_size_image_path = sub_image_html.get('src')
			else:
				print('No sub image tag to render in {}'.format(current_link_html))
				small_size_image_path = ''	# Kill previous iteration if set above

			# Build full_size_image_name
			full_size_image_name = extract_image_name(full_size_image_path)
			# Only process full size image if it isn't already uploaded
			if full_size_image_name != '':
				if full_size_image_name not in new_map_for_image_urls.keys():
					# Now extract alt text, if possible. If not create some from full_size_image_name
					alt_text = generate_alt_text(sub_image_html, full_size_image_name)

					# Upload full size image. If it fails (None returned) print out the list of image urls
					check_for_then_upload_image(new_map_for_image_urls, full_size_image_name, '{}/{}'.format(walk_root, urllib.unquote(full_size_image_path)), alt_text, 'full')

					new_map_for_image_urls = gather_previous_image_uploads()
					print_debug('new_map_for_image_urls has been updated: {}'.format(new_map_for_image_urls))

				# Update urls pointing to our current full image with the omeka s version
				current_link_html['src'] = new_map_for_image_urls[full_size_image_name]
			else:
				print 'Image name ({}) was an empty string; upload and HTML updates skipped'.format(full_size_image_name)


			# Build small_size_image_name
			small_size_image_name = extract_image_name(small_size_image_path)

			# Only process small size image if it isn't already uploaded
			if small_size_image_name != '':
				if small_size_image_name not in new_map_for_image_urls.keys():
					# Now extract alt text, if possible. If not create some from small_size_image_name
					if not alt_text:
						alt_text = generate_alt_text(sub_image_html, small_size_image_name)

					# Upload small size image. If it fails (None returned) print out the list of image urls
					check_for_then_upload_image(new_map_for_image_urls, small_size_image_name, small_size_image_path, alt_text, 'small')

					new_map_for_image_urls = gather_previous_image_uploads()
					print_debug('new_map_for_image_urls has been updated: {}'.format(new_map_for_image_urls))

				# Update urls pointing to our current small image with the omeka s version
				sub_image_html['src'] = new_map_for_image_urls[small_size_image_name]
			else:
				print 'Image name ({}) was an empty string; upload skipped'.format(small_size_image_name)

		print_debug('\nChecking for existing {} page\n'.format(short_file_slug.capitalize()))

		# print_debug(rewrite_slug(current_file))
		if full_file_slug in all_current_page_slugs.values():
			print "{} already exists remotely; skipping page processing and creation".format(full_file_slug)
			continue
		else:
			# Arguably this is happening too early, but thats how it is atm. (A failure lower down will result in a missing page)
			print_debug("Updating all_current_page_slugs from API.")
			all_current_page_slugs = replace_known_page_slugs_list(all_current_page_slugs)
			if all_current_page_slugs_length != len(all_current_page_slugs):
				all_current_page_slugs_length = len(all_current_page_slugs)
				print_debug(all_current_page_slugs)

		# If we didn't continue (skip) above, perform processing of page.
		print '\nPreocessing HTML\n'

		cleanup_html_markup(page_body)

# useful for finding incompletely processed links
# 		for e in page_body.find_all('a'):
# 			print e


		print '\nPreparing json\n'

		# for each section create a block with the section content
		page_content_blocks = []
		for block_content in page_body:
			processed_block = build_page_block_data(block_content)
			page_content_blocks.append(processed_block)
		upload_new_page(page_content_blocks, full_file_slug, short_file_slug)


	print ''

print 'Run started at {}'.format(start_time)
print 'Run finished at {}'.format(datetime.now())


