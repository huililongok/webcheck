
# sitemap.py - plugin to generate a sitemap
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
# Copyright (C) 2005 Arthur de Jong <arthur@tiefighter.et.tudelft.nl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Your site at-a-glance"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'
title = 'Site Map'

import webcheck
import rptlib

def explore(link, explored={}, level=0):
    """Recursively do a breadth-first traversal of the graph of links
    on the site.  Returns a list of HTML fragments that can be printed 
    to produce a site map."""

    explored[link.URL]=True
    # output this link
    print('<li>')
    if (link.URL in webcheck.Link.badLinks) and not webcheck.config.ANCHOR_BAD_LINKS:
        print(link.URL)
    else:
        print(rptlib.make_link(link.URL,rptlib.get_title(link.URL)))

    # only check children if we are not too deep yet
    if level <= webcheck.config.REPORT_SITEMAP_LEVEL:

        # figure out the links to follow and ensure that they are only
        # explored from here
        to_explore = []
        for i in link.children:
            # skip pages that have already been traversed
            if explored.has_key(i):
                continue
            # mark the link as explored
            explored[i]=True
            to_explore.append(i)

        # go over the children and present them as a list
        if len(to_explore) > 0:
            print('<ul>')
            for i in to_explore:
                explore(webcheck.Link.linkMap[i],explored,level+1)
            print('</ul>')

    print( '</li>' )

# site map
def generate():        
    print('<ul>')
    explore(webcheck.Link.base)
    print('</ul>')
