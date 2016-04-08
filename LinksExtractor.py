#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from HTMLParser import HTMLParser
import urlparse


class LinksExtractor(HTMLParser):
    """Extract links from document."""

    def handle_starttag(self, tag, attrs):
        """Find a-tags."""
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    self.links.append(urlparse.urljoin(self.baseurl, value))

    def get_links(self, page, baseurl):
        """Get and return links from document."""
        self.links = []
        self.baseurl = baseurl
        self.feed(page)
        return self.links
