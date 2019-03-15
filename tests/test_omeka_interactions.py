# vim: set fileencoding=utf-8 :

import pytest
import mock

import omeka_interactions

@mock.patch('omeka_interactions.requests')
def test_download_all_omekas_items(mock_requests):
	mock_requests.return_value.get.return_value = {}
	output = omeka_interactions.download_all_omekas_items()
	


@mock.patch('omeka_interactions.requests')
def test_download_all_omekas_media(mock_requests):
	mock_requests.return_value.get.return_value = {}
	output = omeka_interactions.download_all_omekas_media()


@mock.patch('omeka_interactions.requests')
def test_download_specific_media_id_empty_return(mock_requests):
	mock_requests.return_value.get.return_value = {}
	output = omeka_interactions.download_specific_media_id(123)


@mock.patch('omeka_interactions.requests')
def test_download_site_metadata_empty_return(mock_requests):
	mock_requests.return_value.get.return_value = {}
	output = omeka_interactions.download_site_metadata()


@mock.patch('omeka_interactions.requests')
def test_download_specific_page_metadata_empty_return(mock_requests):
	mock_requests.return_value.get.return_value = {}
	output = omeka_interactions.download_specific_page_metadata(123)


@mock.patch('omeka_interactions.open')
@mock.patch('omeka_interactions.requests')
def test_upload_items_with_media(mock_requests, mock_open):
	mock_requests.return_value.ok.return_value = True
	image_data = {'alt_text': 'some text', 'version': 'small', 'image_with_path': '/foo/image_name'}
	output = omeka_interactions.upload_items_with_media('image_name', image_data)


@mock.patch('omeka_interactions.requests')
def test_upload_new_page(mock_requests):
	mock_requests.return_value.ok.return_value = True
	omeka_interactions.upload_new_page({}, 'new-slug-text', 'New Page Title')


@mock.patch('omeka_interactions.download_all_omekas_items')
@mock.patch('omeka_interactions.download_all_omekas_media')
def test_gather_previous_image_uploads(mock_items, mock_media):
	mock_items.return_value = [{'o:media': { '@id': 132 }}]
	mock_media.return_value = [{'@id': 132, 'o:source': 'path-to-file', 'o:original_url': 'uri-file-path'}]
	# omeka_interactions.gather_previous_image_uploads()


@mock.patch('omeka_interactions.requests')
def test_delete_remote_item(mock_requests):
	mock_requests.return_value.ok.return_value = True
	omeka_interactions.delete_remote_item('foobar', 123)

