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

from  __builtin__ import any as b_any
from time import strftime
import HTMLParser
from urllib import urlopen
import urlparse

import multiprocessing
import multiprocessing.queues
import os
import sqlite3
import Queue

global database
database = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'crawler.db'


class FrontierQueue(multiprocessing.queues.Queue):
    # Save, load, delete (URLs) from SQLite upon queue action...
    def __init__(self):
        # Create DB if it doesn't exist
        global database
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


class CrawlerProcess(multiprocessing.Process):
    def __init__(self, queue):
        super(CrawlerProcess, self).__init__()
        self.queue = queue
        global database
        self.database = database

    def run(self):
        #print'hello'
        while True:
            try:
                url = self.queue.get(block=False)
                #print url
                # download
                response = urlopen(url)
                if b_any('text/html' in x for x in response.info().headers):
                    htmlBytes = response.read().decode('utf-8')

                    conn = sqlite3.connect(self.database)
                    c = conn.cursor()
                    # Insert data in content storage
                    c.execute("INSERT INTO storage VALUES (?, ?, ?)", (strftime("%Y-%m-%d %H:%M:%S"), htmlBytes, unicode(url)))
                    # Save changes and close connection
                    conn.commit()
                    conn.close()

                    # parse, replace relative URLs with canonized URL
                    # add URLS to queue
            except Queue.Empty:
                # Kill thread
                break


class Scheduler(object):
    """Docstring for Scheduler class"""

    def __init__(self):
        super(Scheduler, self).__init__()
        #self.arg = arg
        # arg parsing etc.

        nthreads = multiprocessing.cpu_count() -1 # Detect number of logical (not physical; i.e. HyperThreading) cores
        print "Detected", nthreads +1 , "(virtual/logical) cores."

        queue = FrontierQueue()
        # put stuff in the queue here
        for stuff in ['http://www.eivindarvesen.com']:
            queue.put(stuff)
        procs = [CrawlerProcess(queue) for i in xrange(nthreads)]
        for p in procs:
            p.start()
        for p in procs:
            p.join()


if __name__ == "__main__":
    """Run only if the script is called explicitly."""
    obj = Scheduler()
