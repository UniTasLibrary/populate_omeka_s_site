"""FUnctions which directly interact with omeka - ie via API."""
# vim: set fileencoding=utf-8 :

# http://docs.python-requests.org/en/master/user/quickstart/

import json
import requests
from config import *


def download_all_omekas_items():
	# API pages start at 1 - page 0 returns page 1's results
	# Download all items in our item set
	remote_items = []
	temp_remote_items = 1
	api_results_page = 1
	all_params=dict(credential_params)
	all_params.update({'item_set_id': omekas_item_set_id, 'per_page': 100})
	while temp_remote_items > 0:
		# print "items loop number %s" % api_results_page
		all_params.update({'page': api_results_page})
		temp_remote_items = requests.get(api_url_items, params=all_params).json()
		remote_items += temp_remote_items
		# print len(temp_remote_items)
		if len(temp_remote_items) < 100:
			# All results downloaded
			break
		api_results_page += 1
	# print len(remote_items)
	return remote_items

def download_all_omekas_media():
	# Download all media from server
	remote_media = []
	temp_remote_media = 1
	api_results_page = 1
	all_params=dict(credential_params)
	all_params.update({'per_page': 100})
	while temp_remote_media > 0:
		# print "media loop number %s" % api_results_page
		all_params.update({'page': api_results_page})
		temp_remote_media = requests.get(api_url_media, params=all_params).json()
		remote_media += temp_remote_media
		# print len(temp_remote_media)
		if len(temp_remote_media) < 100:
			# All results downloaded
			break
		api_results_page += 1
	# print len(remote_media)
	return remote_media


def download_specific_media_id(media_id):
	try:
		request_result = requests.get('{}/{}'.format(api_url_media, media_id), params=credential_params).json()
	except ValueError as vee:
		print '{} when processing media id {}'.format(vee, media_id)
		print request_result
		request_result = {}
	return request_result


def download_site_metadata():
	try:
		request_result = requests.get('{}/{}'.format(api_url_sites, omekas_site_id), params=credential_params).json()
	except ValueError as vee:
		print '{} when processing site id {}'.format(vee, omekas_site_id)
		print request_result
		request_result = {}
	return request_result

def download_specific_page_metadata(page_id):
	try:
		request_result = requests.get('{}/{}'.format(api_url_site_pages, page_id), params=credential_params).json()
	except ValueError as vee:
		print '{} when processing page id {}'.format(vee, page_id)
		print request_result
		request_result = {}
	return request_result


# Call this to upload images as they are found in the html.
def upload_items_with_media(image_name, image_data):
	json_data = { "dcterms:title" : [ {
				"property_id": 1,
				"property_label" : "Title",
				"@value" : "{} ({})".format(image_data['alt_text'], image_data['version']),
				"type" : "literal"
			} ], "@type" : "o:Item", "o:item_set" : [ {
				"o:id": '{}'.format(omekas_item_set_id)
			} ], "o:media" : [ {
				"o:ingester": "upload", "file_index": "0", "o:item": {},
				"dcterms:title" : [ {
						"property_id" : 1, "property_label" : "Title",
						"@value" : "{} ({})".format(image_data['alt_text'], image_data['version']),
						"type" : "literal"
					} ] } ] }

	# Three tuple, filename, file object, extra headers
	files = [
		('data', (None, json.dumps(json_data), 'application/json')),
		('file[0]', (image_name, open(image_data['image_with_path'], 'rb'), 'application/octet-stream'))
	]

	# print files

	r = requests.post(api_url_items, files=files, params=credential_params)
	# print r.json()
	if r.ok:
		print "Uploaded {} to Omeka S item set {}. Alt text is {}".format(image_name, omekas_item_set_id, image_data['alt_text'])
	else:
		print "Error uploading {}, result was {}".format(image_name, r.text)
	# Always return, even when its an error within
	return r

def upload_new_page(data_block_list, new_slug, new_title):
	# Our upload data - inserts the data_block_list directly in to the json
	json.dumps(data_block_list)
	json_data = {
		"o:slug": "{}".format(new_slug),
		"o:site": {
			"@id" : "{}/sites/{}".format(api_url_sites, omekas_site_id),
			"o:id": '{}'.format(omekas_site_id)
			},
		"o:title": "{}".format(new_title.capitalize()),
		"o:block": data_block_list,
	}

	# Wrap this in error handling - if it fails, our json isn't ok
	json.dumps(json_data)

	print '\nUploading json to create page\n'

	print json_data

	page_creation = requests.post(api_url_site_pages, params=credential_params, json=json_data)
	if not page_creation.ok:
		print page_creation.text
	# Always return, even when its an error within
	return page_creation


def gather_previous_image_uploads():
	# Because Omeka S API doesn't have a way to return all media who's items are in
	# an item set or all media who's items are in a site pool we build a list of
	# our media from the items in our item set (next code block) followed by
	# pulling ALL media and checking if they're in our list (following while block)

	remote_items = download_all_omekas_items()
	remote_media = download_all_omekas_media()

	# Build a list of media to query using items in our item set.
	media_ids_to_query = []
	for record in remote_items:
		# print 'Item ID {}'.format(record['o:id'])
		for media_record in record['o:media']:
			# print 'Item Media ID {}'.format(media_record['o:id'])
			media_ids_to_query.append(media_record['@id'])

	# Now update our various maps using the media data
	downloaded_image_urls = {}
	for full_media_entry in remote_media:
		# print full_media_entry['@id']
		if full_media_entry['@id'] in media_ids_to_query:
			# print 'Adding {} to downloaded_image_urls'.format( full_media_entry['o:source'])
			downloaded_image_urls.update({full_media_entry['o:source']: '/{}'.format(full_media_entry['o:original_url'].strip(omekas_base_url))})
	return downloaded_image_urls


# Danger will robinson!
def delete_remote_item(resource_type, resource_id):
	# Accepts:
	# resource_type - as specified on https://omeka.org/s/docs/developer/key_concepts/api/
	# resource_id - the identifer (typically number) of the resource to act on.

	deletion = requests.delete('{}api/{}/{}'.format(omekas_base_url, resource_type, resource_id), params=credential_params)
	if not deletion.ok:
		print deletion.text
		return False
	return True

