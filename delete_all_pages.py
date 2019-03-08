
from datetime import datetime

from omeka_interactions import delete_remote_item, download_site_metadata

start_time = datetime.now()
deleted = 0
our_sites_metadata = download_site_metadata()
print "Deleting pages from {}, slug {}\n".format(our_sites_metadata['o:title'], our_sites_metadata['o:slug'])
if 'o:page' in our_sites_metadata.keys():
	for site_page in our_sites_metadata['o:page']:
		deleted += 1
		print "Deleting {}".format(site_page)
		delete_remote_item('site_pages', site_page['o:id'])
else:
	print "our_sites_metadata did not include o:page"

print 'Run started at {}'.format(start_time)
print 'Run finished at {}'.format(datetime.now())
print '{} items deleted'.format(deleted)

