# vim: set fileencoding=utf-8 :

import pytest
import mock
import utility_functions

def test_print_debug_empty_message_verbose():
	run_verbose = True
	o = utility_functions.print_debug('')
	assert o == True

def test_print_debug_with_message_verbose():
	run_verbose = True
	o = utility_functions.print_debug('something')
	assert o == True

def test_print_debug_with_message_not_verbose():
	run_verbose = False
	o = utility_functions.print_debug('something')
	assert o == True

def test_print_debug_enabled():
	run_verbose = True
	o = utility_functions.print_debug('something')
	assert o == True


def test_rewrite_slug_empty_string():
	input_string = ''
	o = utility_functions.rewrite_slug(input_string)
	assert o == ''

def test_rewrite_slug_htm_file():
	input_string = 'I/am.htm'
	o = utility_functions.rewrite_slug(input_string)
	assert o == 'i_am'

def test_rewrite_slug_html_file():
	input_string = 'I/amT.html'
	o = utility_functions.rewrite_slug(input_string)
	assert o == 'i_amt'

def test_rewrite_slug_html_file_strip_level_up():
	input_string = '../I/amT.html'
	o = utility_functions.rewrite_slug(input_string)
	assert o == 'i_amt'

def test_rewrite_slug_all_actions():
	input_string = '../I/amTEâåSTING.files'
	o = utility_functions.rewrite_slug(input_string)
	assert o == '___i_amtesting_files'


def test_check_if_processing_required_image():
	location_source = 'iam.jpg'
	o = utility_functions.check_if_processing_required(location_source)
	assert o == False

def test_check_if_processing_required_madeup():
	location_source = 'iam.fofof'
	o = utility_functions.check_if_processing_required(location_source)
	assert o == False

def test_check_if_processing_required_html():
	location_source = 'iam.html'
	o = utility_functions.check_if_processing_required(location_source)
	assert o == True


# TODO: This requires several mocks and file IO; do as round 2
def test_load_source_html(mocker):
	mocker.patch('codecs.open')
	mocker.patch('utility_functions.BeautifulSoup')
	o = utility_functions.load_source_html('/nonexistant')
	# FIXME: complete and do others


def test_extract_desired_metadata():
	# If someone starts using this they'll need to fix the test.
	input_soup = 'asdfadf'
	input_file = 'asdfadf'
	o = utility_functions.extract_desired_metadata(input_soup, input_file)
	assert o == None


# FIXME: more
def test_extract_desired_html_no_matches(mocker):
	fake_soup = mock.MagicMock()
	o = utility_functions.extract_desired_html(fake_soup)
	assert fake_soup.find.is_called()


# FIXME: more
def test_cleanup_html_markup(mocker):
	fake_soup = mock.MagicMock()
	o = utility_functions.cleanup_html_markup(fake_soup)
	assert o == None


def test_build_page_block_data():
	page_section = 'I am fred'
	valid_output = {
		"o:attachment" : [],
		"o:layout" : "html",
		"o:data" : {
		    "html" : "I am fred",
		 },
	}
	o = utility_functions.build_page_block_data(page_section)
	assert o == valid_output
	

def test_extract_image_name_empty_name():
	my_name = ''
	o = utility_functions.extract_image_name(my_name)
	assert o == ''

def test_extract_image_name_dir_plus_file():
	my_name = 'images/handy.jpg'
	o = utility_functions.extract_image_name(my_name)
	assert o == 'handy.jpg'

def test_extract_image_name_dir_with_files_in_it():
	my_name = 'files/blahblah/something.jpg'
	o = utility_functions.extract_image_name(my_name)
	assert o == 'something.jpg'


# TODO: More
def test_generate_alt_text_simple_filename(mocker):
	fake_soup = mock.MagicMock()
	fake_image_name = 'i_make_works.jpg'
	o = utility_functions.generate_alt_text(fake_soup, fake_image_name)
	o == 'i make works'

def test_generate_alt_text_with_path(mocker):
	fake_soup = mock.MagicMock()
	fake_image_name = 'something/i_make_works.jpg'
	o = utility_functions.generate_alt_text(fake_soup, fake_image_name)
	o == 'something i make works'


# TODO: More
def test_check_for_then_upload_image_no_image_name(mocker):
	image_urls = ''
	image_name = ''
	image_path = ''
	alt_text = ''
	version = ''
	o = utility_functions.check_for_then_upload_image(image_urls, image_name, image_path, alt_text, version)
	assert o == None

def test_check_for_then_upload_image_image_in_list(mocker):
	image_urls = ['i_am_image.gif']
	image_name = 'i_am_image.gif'
	image_path = ''
	alt_text = ''
	version = ''
	o = utility_functions.check_for_then_upload_image(image_urls, image_name, image_path, alt_text, version)
	assert o == None

def test_check_for_then_upload_image(mocker):
	# This fails the API json component so hits the inner 'else' clause.
	image_urls = ['image', 'not', 'in', 'here']
	image_name = 'i_am_image.gif'
	image_path = ''
	alt_text = ''
	version = ''
	mocker.patch('utility_functions.upload_items_with_media')
	mocker.patch('utility_functions.download_specific_media_id')
	o = utility_functions.check_for_then_upload_image(image_urls, image_name, image_path, alt_text, version)
	assert o == True


def test_replace_known_page_slugs_list(mocker):
	mocker.patch('utility_functions.download_site_metadata')
	mocker.patch('utility_functions.download_specific_page_metadata')
	input_dict = {}
	o = utility_functions.replace_known_page_slugs_list(input_dict)
	assert o == {}
