#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import FrontierQueue
import LinksExtractor

import argparse
import multiprocessing
import os
import signal
import sqlite3
import sys
import urlparse

from __builtin__ import any as b_any
from time import strftime, sleep
from urllib import urlopen


def __workerProcess__(queue, database):
    """
    Worker process. Downloads documents from URLs.

    Then parses them and puts any URLs in the queue.
    """
    while True:
        try:
            url = queue.get(block=False)
            print "Starting processing of " + url
            response = urlopen(url)

            # Check headers to find out if URL leads to a html document
            if b_any('text/html' in x for x in response.info().headers):
                htmlBytes = response.read().decode('utf-8')

                conn = sqlite3.connect(database)
                c = conn.cursor()
                # Insert data(document) in content storage
                c.execute("INSERT INTO storage VALUES (?, ?, ?)",
                          (strftime("%Y-%m-%d %H:%M:%S"),
                           htmlBytes, unicode(url)))
                # Save changes and close connection
                conn.commit()
                conn.close()

                # parse document, replace relative URLs with canonized URL
                htmlparser = LinksExtractor.LinksExtractor()
                links = htmlparser.get_links(htmlBytes, url)

                # add URLs to queue
                for link in links:
                    conn = sqlite3.connect(database)
                    c = conn.cursor()
                    # Check if URL is already in queue
                    c.execute(
                        """SELECT count(*) FROM frontier WHERE url = (?)
                        """, (unicode(link),))
                    result = c.fetchone()[0]
                    # Save changes and close connection
                    conn.commit()
                    conn.close()
                    if not result:
                        queue.put(link)
            else:
                print url + ' is not a document'
        except Exception, e:
            # sleep if queue is (temporarily) empty or there is no response
            sleep(1)

            # if no update for a while: kill thread
            if queue.isTimedOut():
                break


class Scheduler(object):
    """Scheduler class."""

    def __init__(self):
        """Constructor."""
        super(Scheduler, self).__init__()

        database = os.path.dirname(
            os.path.realpath(__file__)) + os.sep + 'crawler.db'

        # Detect number of logical (not physical; i.e. HyperThreading) cores
        if multiprocessing.cpu_count() < 1:
            nProcesses = multiprocessing.cpu_count() - 1
        else:
            nProcesses = 1

        queue = FrontierQueue.FrontierQueue(database)

        # parse command line arguments
        parser = argparse.ArgumentParser(
            description='A minimal web crawler."', prog='Naive Spider')
        parser.add_argument('urls', nargs='*', help='URL(s)', action='store')
        self.args = []

        # Normalize URL (http...)
        for url in parser.parse_args().urls:
            if not url.startswith('http://'):
                self.args.append('http://' + url)
            else:
                self.args.append(url)

        if not self.args and not os.path.isfile(database):
            # exit if no URL provided and there are no saved URLs
            parser.error('No URLs provided.')
            sys.exit()

        else:
            # check if URLs are valid
            tokens = [urlparse.urlparse(url) for url in self.args]
            min_attributes = ('scheme', 'netloc')
            for token in tokens:
                if not all([getattr(token, attr) for attr in min_attributes]):
                    print token.geturl() + ' is not a valid url'
                    sys.exit()

            # kill/cleanup on ctrl+c
            signal.signal(signal.SIGINT, self.signal_handler)
            #signal.pause()

            # put url(s) in the queue
            for address in self.args:
                queue.put(address)

            # start worker processes
            p = multiprocessing.Pool(
                nProcesses, __workerProcess__, (queue, database, ))
            p.close()
            p.join()  # Wait for all child processes to close.

    def signal_handler(self, signal, frame):
        """Handle ctrl+c signal."""
        # Perform cleanup on ctrl+c
        print '\nInterrupting...'
        sys.exit(0)
