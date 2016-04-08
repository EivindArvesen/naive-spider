#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import multiprocessing.queues
import os
import sqlite3
import time


class FrontierQueue(multiprocessing.queues.Queue):
    """Queue based on SQLite-database."""

    def __init__(self, database):
        """Set things up."""
        self.database = database
        if not os.path.isfile(self.database):
            # Create DB if it doesn't exist
            open(self.database, 'w+').close()

            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Create tables
            c.execute('''CREATE TABLE frontier
                    (URL text)''')
            c.execute('''CREATE TABLE storage
                    (date text, content text, canonizedurl text)''')

            # Save changes and close connection
            conn.commit()
            conn.close()

        self.lastOperation = time.clock()

        super(FrontierQueue, self).__init__()

    def put(self, obj, block=True, timeout=None):
        """Put URL in queue."""
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        # Insert data
        url = (obj,)
        c.execute("INSERT INTO frontier VALUES (?)", (unicode(url),))
        # Save changes and close connection
        conn.commit()
        conn.close()

        self.lastOperation = time.time()

        return super(FrontierQueue, self).put(obj, block, timeout)

    def get(self, block=True, timeout=None):
        """Get URL from queue."""
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        # Select data
        url = super(FrontierQueue, self).get(block, timeout)
        c.execute("DELETE FROM frontier WHERE url IS (?)", (unicode(url),))
        # Save changes and close connection
        conn.commit()
        conn.close()

        return url

    def isTimedOut(self):
        """Check if there has been no new URL for an amount of time."""
        if time.time() - self.lastOperation >= 5:
            return True
        else:
            return False
