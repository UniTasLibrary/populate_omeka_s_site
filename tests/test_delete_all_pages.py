# vim: set fileencoding=utf-8 :

import pytest
import mock
import delete_all_pages

@mock.patch('delete_all_pages.download_site_metadata')
@mock.patch('delete_all_pages.delete_remote_item')
def test_delete_all_pages_missing_o_page(mock_delete_remote_item, mock_download):
	data_dict = {'o:title': 'My test data', 'o:slug': 'my-test_data'}
	mock_download.return_value = data_dict
	result = delete_all_pages.run_delete()
	assert mock_download.called
	assert not mock_delete_remote_item.call_count

@mock.patch('delete_all_pages.download_site_metadata')
@mock.patch('delete_all_pages.delete_remote_item')
def test_delete_all_pages_with_o_page(mock_delete_remote_item, mock_download):
	data_dict = {'o:title': 'My test data', 'o:slug': 'my-test_data', 'o:page': [{'o:id': 42},{'o:id': 999}]}
	mock_download.return_value = data_dict
	result = delete_all_pages.run_delete()
	assert mock_download.called
	assert mock_delete_remote_item.called
	assert mock_delete_remote_item.call_count == 2

