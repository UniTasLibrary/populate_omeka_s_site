# vim: set fileencoding=utf-8 :

import pytest
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

def test_rewrite_slug_empty_string():
	input_string = ''
	o = utility_functions.rewrite_slug(input_string)
	assert o == ''

def test_rewrite_slug_all_actions():
	input_string = 'I/amTEâåSTING.files'
	o = utility_functions.rewrite_slug(input_string)
	assert o == 'i_amtesting_files'

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
# def test_load_source_html():

def test_extract_desired_metadata():
	# If someone starts using this they'll need to fix the test.
	input_soup = 'asdfadf'
	input_file = 'asdfadf'
	o = utility_functions.extract_desired_metadata(input_soup, input_file)
	assert o == None


# Mocks, do these tests as round 2
# def test_extract_desired_html():

# Mocks, do these tests as round 2
# def test_cleanup_html_markup():

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
	assert o == ''

def test_extract_image_name_invalid_filename():
	my_name = '/some/unexpected/dir/name.jpg'
	o = utility_functions.extract_image_name(my_name)
	assert o == ''


# Mocks, do these tests as round 2
# def test_generate_alt_text()


# Mocks, do these tests as round 2
# def test_check_for_then_upload_image()


