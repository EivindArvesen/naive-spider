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
# Frontier -> Queue -> Scheduler -> ThreadPool -> DownloaderAndParser -> Frontier(URLs)
#                                                                    |-> ContentStorage(TextAndMetadata)

import multiprocessing
import os
import Queue

class Scheduler(object):
    # Get content from Frontier (SQLite), put on queue, spawn process
    pass

class Frontier(object):
    # Save, load, delete (URLs) from SQLite...
    pass

class ContentStorage(object):
    # Save, load, delete (pages) from SQLite...

class CrawlerProcess(multiprocessing.Process):
    def __init__(self, queue):
        super(CrawlerProcess, self).__init__()
        self.queue = queue

    def run(self):
        print('hello')
        while True:
            try:
                a = self.queue.get(block=False)
                print a
                # download
                # parse
            except Queue.Empty:
                # Kill thread
                break


class Runner(object):
    """Docstring for Runner class"""

    def __init__(self):
        super(Runner, self).__init__()
        #self.arg = arg
        # arg parsing etc.

        db_path = os.path.realpath(__file__)

        nthreads = multiprocessing.cpu_count() # Detect number of logical (not physical; i.e. HyperThreading) cores
        print "Detected", nthreads, "(virtual/logical) cores."

        queue = multiprocessing.Queue()
        # put stuff in the queue here
        for stuff in ['one', 'two', 'three', 'four', 'five', 'six', 'seven']:
            queue.put(stuff)
        procs = [CrawlerProcess(queue) for i in xrange(nthreads)]
        for p in procs:
            p.start()
        for p in procs:
            p.join()

    def __outputProcess__(self, queue):
        """Listen for messages on queue. Perform all writing of output."""
        print '\nLol...'


if __name__ == "__main__":
    """Run only if the script is called explicitly."""
    obj = Runner()
