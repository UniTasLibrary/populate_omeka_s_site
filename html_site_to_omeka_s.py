"""Transform an HTML website to Omeka S."""
# vim: set fileencoding=utf-8 :

# https://www.crummy.com/software/BeautifulSoup/bs4/doc/

import os
import re

from config import *
from utility_functions import *
from omeka_interactions import *


# TODO: A __main__ function would look really good here.

# FIXME: need to add error handling; currently walk errors are ignored
all_website_files = os.walk(website_root_on_disk)

for walk_root, walk_dir, walk_file in all_website_files:
	if '_notes' in walk_dir:
		walk_dir.remove('_notes')  # don't visit DreamWeaver directories
	# print walk_root
	# print walk_dir
	# print walk_file
	# Look at files in current directory
	for current_file in walk_file:
		# Buid path to our current file
		markup_file = os.path.join(walk_root, current_file)

		# This skip is silent, check_if_processing_required outputs notices
		if not check_if_processing_required(markup_file):
			print_debug('No further processing required')
			continue
		# Needs to be below the html skip-check in check_if_processing_required
		print '\n===========\n'

		# Remove later when listing every file not needed
		print "Current file is {}".format(current_file)

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

		print '\nProcessing images\n'

		new_map_for_image_urls = gather_previous_image_uploads()
		# print 'new_map_for_image_urls {}'.format(new_map_for_image_urls)

		all_page_images_html = page_body.find_all(href=re.compile("images"))

		# Build a list of all images used on the page to try and reduce duplicate uploads
		# If an image is used multiple times with different alt text only the first will
		# be used.

		for current_link_html in all_page_images_html:
			full_size_image_path = current_link_html.get('href')

			# Extract any sub image - those used for display
			sub_image_html = current_link_html.find('img')
			# There isn't always an image, so check before finding image path
			if sub_image_html:
				small_size_image_path = sub_image_html.get('src')
			else:
				print('{} has no sub image tag to render'.format(current_link_html))
				small_size_image_path = ''	# Kill previous iteration if set above

			# print '0 big image {}, small image {}'.format(full_size_image_path, small_size_image_path)

			full_size_image_name = extract_image_name(full_size_image_path)
			small_size_image_name = extract_image_name(small_size_image_path)

			# Now extract alt text, if possible. If not create some from full_size_image_name
			alt_text = generate_alt_text(sub_image_html, full_size_image_path)

			# Upload full size image
			check_for_then_upload_image(new_map_for_image_urls, full_size_image_name, full_size_image_path, alt_text, 'full')

			# Update urls pointing to our current full image with the omeka s version
			current_link_html['href'] = new_map_for_image_urls[full_size_image_name]

			# Upload small size image
			check_for_then_upload_image(new_map_for_image_urls, small_size_image_name, small_size_image_path, alt_text, 'small')

			# sub_image_html may not exist, but must do if small_size_image_name is defined.
			if small_size_image_name:
				# Update urls pointing to our current small image with the omeka s version
				sub_image_html['src'] = new_map_for_image_urls[small_size_image_name]
				if small_size_image_name not in new_map_for_image_urls.keys():
					# Now extract alt text, if possible. If not create some from small_size_image_name
					if not alt_text:
						alt_text = generate_alt_text(sub_image_html, small_size_image_name)

		print '\nChecking for existing {} page\n'.format(rewrite_slug(current_file).capitalize())

		our_sites_metadata = download_site_metadata()

		all_current_page_slugs = []
		for site_page in our_sites_metadata['o:page']:
			# print site_page
			our_pages_metadata = download_specific_page_metadata(site_page['o:id'])
			all_current_page_slugs.append(our_pages_metadata['o:slug'])

		print all_current_page_slugs

		# print all_current_page_slugs
		# print rewrite_slug(current_file)
		if rewrite_slug(current_file) in all_current_page_slugs:
			print "{} already exists remotely; skipping page processing and creation".format(rewrite_slug(current_file).capitalize())
			continue

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
		upload_new_page(page_content_blocks, rewrite_slug(current_file))


	print ''


