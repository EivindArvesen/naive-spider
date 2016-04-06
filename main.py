#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""A minimal web crawler."""
__author__ = "Eivind Arvesen"
__copyright__ = "Copyright (c) 2016, Eivind Arvesen. All rights reserved."
__credits__ = ["Eivind Arvesen"]  # Bugfixers, suggestions etc.
__license__ = "3-clause BSD"  # LGPL/GPL3/BSD/Apache/MIT/CC/C/whatever
__version__ = "0.0.1 Alpha" # "Alpha", "Beta", ""
__maintainer__ = "Eivind Arvesen"
__email__ = "eivind.arvesen@gmail.com"
__status__ = "Prototype"  # Prototype/Development/Production

# Copyright (c) 2016 Eivind Arvesen. All rights Reserved.

# Write a minimal web crawler in your programming language of choice.
# A crawler at its core downloads urls, discovers new urls in the
# downloaded content and schedules download of the discovered urls,
# i.e.,:
# * Fetch a discovered URL
# * Store the content on disk
# * Discover new URLs by extracting URLs from the fetched content and
# crawl these etc
# The crawler should be able to resume operations if shut down.

# FLOW:
# Frontier/Queue -> Scheduler -> DownloaderAndParser(s) -> Frontier(URLs)
#                                                      |-> ContentStorage(TextAndMetadata)

import htmllib, formatter
import urllib, htmllib, formatter

from  __builtin__ import any as b_any
from time import strftime
from HTMLParser import HTMLParser
from urllib import urlopen
import urlparse

import multiprocessing
import multiprocessing.queues
import os
import sqlite3
import Queue


class LinksExtractor(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    self.links.append(urlparse.urljoin(self.baseurl, value))

    def get_links(self, page, baseurl):
        self.links = []
        self.baseurl = baseurl
        self.feed(page)
        return self.links


class FrontierQueue(multiprocessing.queues.Queue):
    # Save, load, delete (URLs) from SQLite upon queue action...
    def __init__(self, database):
        # Create DB if it doesn't exist
        self.database = database
        if not os.path.isfile(self.database):
            open(self.database, 'w+').close()

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        # Create tables
        if not c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='frontier'"):
            c.execute('''CREATE TABLE frontier
                     (URL text)''')
        if not c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='storage'"):
            c.execute('''CREATE TABLE storage
                     (date text, content text, canonizedurl text)''')

        # Save changes and close connection
        conn.commit()
        conn.close()

        super(FrontierQueue, self).__init__()

    def put(self, obj, block=True, timeout=None):
        #print "PUT"
        # Normalize URL (http/www)

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        # Insert data
        url = (obj,)
        c.execute("INSERT INTO frontier VALUES (?)", (unicode(url),))
        # Save changes and close connection
        conn.commit()
        conn.close()

        return super(FrontierQueue, self).put(obj, block, timeout)

    def get(self, block=True, timeout=None):
        #print "GET"

        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        # Select data
        url = super(FrontierQueue, self).get(block, timeout)
        c.execute("DELETE FROM frontier WHERE url IS (?)", (unicode(url),))
        # Save changes and close connection
        conn.commit()
        conn.close()

        return url


def __workerProcess__(queue, database):
    while True:
        url = queue.get(block=False)
        #print url
        # download
        response = urlopen(url)
        if b_any('text/html' in x for x in response.info().headers):
            htmlBytes = response.read().decode('utf-8')

            conn = sqlite3.connect(database)
            c = conn.cursor()
            # Insert data in content storage
            c.execute("INSERT INTO storage VALUES (?, ?, ?)", (strftime("%Y-%m-%d %H:%M:%S"), htmlBytes, unicode(url)))
            # Save changes and close connection
            conn.commit()
            conn.close()

            # parse, replace relative URLs with canonized URL
            # add URLS to queue
            htmlparser = LinksExtractor()
            links = htmlparser.get_links(htmlBytes, url)

            for link in links:
                #print link
                queue.put(link)


class Scheduler(object):
    """Docstring for Scheduler class"""

    def __init__(self):
        super(Scheduler, self).__init__()
        #self.arg = arg
        # arg parsing etc.

        database = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'crawler.db'

        if multiprocessing.cpu_count() < 1:  # Detect number of logical (not physical; i.e. HyperThreading) cores
            nProcesses = multiprocessing.cpu_count() -1
        else:
            nProcesses = 1

        queue = FrontierQueue(database)

        # put stuff in the queue here
        for address in ['http://howdovaccinescauseautism.com']:
            queue.put(address)

        p = multiprocessing.Pool(nProcesses, __workerProcess__, (queue, database, ))
        p.close()
        p.join()  # Wait for all child processes to close.


if __name__ == "__main__":
    """Run only if the script is called explicitly."""
    obj = Scheduler()
