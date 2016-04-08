#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""A minimal web crawler."""

__author__ = "Eivind Arvesen"
__copyright__ = "Copyright (c) 2016, Eivind Arvesen. All rights reserved."
__credits__ = ["Eivind Arvesen"]  # Bugfixers, suggestions etc.
__license__ = "3-clause BSD"  # LGPL/GPL3/BSD/Apache/MIT/CC/C/whatever
__version__ = "0.0.3 Beta"  # "Alpha", "Beta", ""
__maintainer__ = "Eivind Arvesen"
__email__ = "eivind.arvesen@gmail.com"
__status__ = "Prototype"  # Prototype/Development/Production

# Copyright (c) 2016 Eivind Arvesen. All rights Reserved.


import Scheduler

if __name__ == "__main__":
    """Run only if the script is called explicitly."""
    obj = Scheduler.Scheduler()
