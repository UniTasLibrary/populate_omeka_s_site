# vim: set fileencoding=utf-8 :

import pytest
import mock
import html_site_to_omeka_s

# Utils
@mock.patch('html_site_to_omeka_s.rewrite_slug')
# @mock.patch('html_site_to_omeka_s.check_if_processing_required')
@mock.patch('html_site_to_omeka_s.load_source_html')
@mock.patch('html_site_to_omeka_s.extract_desired_metadata')
@mock.patch('html_site_to_omeka_s.extract_desired_html')
@mock.patch('html_site_to_omeka_s.cleanup_html_markup')
@mock.patch('html_site_to_omeka_s.build_page_block_data')
@mock.patch('html_site_to_omeka_s.extract_image_name')
@mock.patch('html_site_to_omeka_s.generate_alt_text')
@mock.patch('html_site_to_omeka_s.check_for_then_upload_image')
@mock.patch('html_site_to_omeka_s.replace_known_page_slugs_list')
# api/interactions
@mock.patch('html_site_to_omeka_s.omeka_interactions.gather_previous_image_uploads')
@mock.patch('html_site_to_omeka_s.omeka_interactions.upload_new_page')
# config
@mock.patch('html_site_to_omeka_s.config.website_root_on_disk')
# System
@mock.patch('os.walk')
@mock.patch('os.path.join')
def test_main_site_migration(mock_os_path_join, mock_os_walk, mock_website_root_on_disk, mock_upload_new_page, mock_gather_previous_image_uploads, mock_replace_known_page_slugs_list, mock_check_for_then_upload_image, mock_generate_alt_text, mock_extract_image_name, mock_build_page_block_data, mock_cleanup_html_markup, mock_extract_desired_html, mock_extract_desired_metadata, mock_load_source_html, mock_rewrite_slug):
	# FIXME: Why is this returning a  mock not the string?
	mock_website_root_on_disk.return_value = '/doesnotexist/'
	mock_os_walk.return_value = [('/doesnotexist/nothere', ['fakesubfolder', '_notes'], ['skipper.asdfadf']),('/fakepath', [], ['process.html'])]
	mock_replace_known_page_slugs_list.side_effect = [{}, {'something': 'value'}]
	mock_gather_previous_image_uploads.side_effect = [{}, {'details': 'returned'}]
	mock_os_path_join.side_effect = ['/nothere/skipper.asdfadf', '/fakepath/process.html']
	mock_rewrite_slug.return_value = 'fakepath_process'
# Consider not mocking this one
	# mock_check_if_processing_required.side_effect = [False, True]
	mock_load_source_html.return_value = 'Raw HTML'
	mock_extract_desired_metadata.return_value = None
	mock_extract_desired_html.return_value = mock.MagicMock()	# Lots of sub methods are called on the bs4 objects that this should be returning
	mock_extract_image_name.return_value = 'name_of_image_from_file.jpg'
	mock_generate_alt_text.return_value = 'name of image from file'
	mock_check_for_then_upload_image.return_value = None	# Ignored in code
	mock_cleanup_html_markup.return_value = None		# ignored in code
	mock_build_page_block_data.return_value = {}		# FIXME: returns a dict?
	mock_upload_new_page.return_value = None		# ignored in code
	output = html_site_to_omeka_s.main_site_migration()
