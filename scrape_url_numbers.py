from getSiteNumber import *
import gevent.monkey
gevent.monkey.patch_socket()

import gevent
import urllib2
import simplejson as json

f = open("startup_urls.tsv","r")
links = f.readlines()
f.close()

print(len(links))
filename = 'startups_list_numbers.tsv'
f = open(filename,'w')
f.close()
site_crawlers = []
for link in links:
	site_crawlers.append(getSiteNumber(link, filename))

# print(len(site_crawlers))
threads = []
for i in range(len(site_crawlers)):
    threads.append(gevent.spawn(site_crawlers[i].get_number))
gevent.joinall(threads)