
# __init__.py - plugin function module
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import sys
import urllib
import string
import debugio
import config
import xml.sax.saxutils
import time

def get_title(link):
    """Returns the title of a link if it is set otherwise returns url."""
    if link.title is None or link.title == '':
        return link.url
    return link.title

def _floatformat(f):
    """Return a float as a string while trying to keep it within three
    characters."""
    r = '%.1f' % f
    if len(r) > 3:
        r = r[:r.find('.')]
    return r

def get_size(i):
    """Return the size in bytes as a readble string."""
    K = 1024
    M = K*1024
    G = M*1024
    if i > 1024*1024*999:
        return _floatformat(float(i)/float(G))+'G'
    elif i > 1024*999:
        return _floatformat(float(i)/float(M))+'M'
    elif i >= 1024:
        return _floatformat(float(i)/float(K))+'K'
    else:
        return '%d' % i

def get_info(link):
    """Return a string with a summary of the information in the link."""
    info = 'url: %s\n' % link.url
    if link.status:
        info += '%s\n' % link.status
    if link.title:
        info += 'title: %s\n' % link.title.strip()
    if link.author:
        info += 'author: %s\n' % link.author.strip()
    if link.isinternal:
        info += 'internal link'
    else:
        info += 'external link'
    if link.isyanked:
        info += ', not checked\n'
    else:
        info += '\n'
    if link.redirectdepth > 0:
        if len(link.children) > 0:
            info += 'redirect: %s\n' % link.children[0].url
        else:
            info += 'redirect (not followed)\n'
    if len(link.parents) == 1:
        info += 'linked from 1 page\n'
    elif len(link.parents) > 1:
        info += 'linked from %d pages\n' % len(link.parents)
    if link.mtime:
        info += 'last modified: %s\n' % time.ctime(link.mtime)
    if link.size:
        info += 'size: %s\n' % get_size(link.size)
    if link.mimetype:
        info += 'mime-type: %s\n' % link.mimetype
    for problem in link.linkproblems:
        info += 'problem: %s\n' % xml.sax.saxutils.escape(problem)
    # trim trailing newline
    return info.strip()

def make_link(link,title=None):
    """Return an <a>nchor to a url with title. If url is in the Linklist and
    is external, insert "class=external" in the <a> tag."""
    # try to fetch the link object for this url
    if link.isinternal:
        cssclass='internal'
    else:
        cssclass='external'
    if title is None:
        title=get_title(link)
    # gather some information about the link to report
    info = xml.sax.saxutils.quoteattr(get_info(link),{'\n':'&#10;'})
    return '<a href="'+link.url+'" class="'+cssclass+'" title='+info+'>'+xml.sax.saxutils.escape(title)+'</a>'

def print_parents(fp,link,indent='     '):
    # present a list of parents
    parents = link.parents
    # if there are no parents print nothing
    if len(parents) == 0:
        return
    parents.sort(lambda a, b: cmp(a.title, b.title))
    fp.write(
      indent+'<div class="parents">\n'+ \
      indent+' referenced from:\n'+ \
      indent+' <ul>\n' )
    for parent in parents:
        fp.write(
          indent+'  <li>%(parent)s</li>\n'
          % { 'parent': make_link(parent) })
    fp.write(
      indent+' </ul>\n'+ \
      indent+'</div>\n' )

def open_file(filename):
    """ given config.OUTPUT_DIR checks if the directory already exists; if
    not, it creates it, and then opens filename for writing and returns the
    file object """
    import os
    if os.path.isdir(config.OUTPUT_DIR) == 0:
        os.mkdir(config.OUTPUT_DIR)
    fname = os.path.join(config.OUTPUT_DIR,filename)
    if os.path.exists(fname) and not config.OVERWRITE_FILES:
        # mv: overwrite `/tmp/b'?
        # cp: overwrite `/tmp/b'?
        # zip: replace aap.txt? [y]es, [n]o, [A]ll, [N]one, [r]ename:
        ow = raw_input('webcheck: overwrite %s? [y]es, [a]ll, [q]uit: ' % fname)
        ow = ow.lower() + " "
        if ow[0] == 'a':
            config.OVERWRITE_FILES = True
        elif ow[0] != 'y':
            print 'Aborted.'
            sys.exit(0)
    return open(fname,'w')

def generate(site,plugins):
    """Generate pages for plugins."""
    # generate navigation part
    navbar='  <ul class="navbar">\n'
    for plugin in plugins:
        # if this is the first plugin use index.html as filename
        filename = plugin + '.html'
        if plugin == plugins[0]:
            filename = 'index.html'
        # import the plugin
        report = __import__('plugins.' + plugin, globals(), locals(), [plugin])
        # generate a link to the plugin page
        navbar += '   <li><a href="%(pluginfile)s" title="%(description)s">%(title)s</a></li>\n' \
                  % { 'pluginfile':  filename,
                      'title':       xml.sax.saxutils.escape(report.__title__),
                      'description': xml.sax.saxutils.escape(report.__doc__) }
    navbar+='  </ul>\n'
    for plugin in plugins:
        debugio.info('  ' + plugin)
        # if this is the first plugin use index.html as filename
        filename = plugin + '.html'
        if plugin == plugins[0]:
            filename = 'index.html'
        report = __import__('plugins.' + plugin, globals(), locals(), [plugin])
        fp = open_file(filename)
        # write basic html head
        # TODO: make it possible to use multiple stylesheets (possibly reference external stylesheets)
        fp.write( \
          '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' \
          '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n' \
          '<html xmlns="http://www.w3.org/1999/xhtml">\n' \
          ' <head>\n' \
          '  <title>Webcheck report for %(sitetitle)s</title>\n' \
          '  <link rel="stylesheet" type="text/css" href="webcheck.css" />\n' \
          '  <meta name="Generator" content="webcheck %(version)s" />\n' \
          ' </head>\n' \
          ' <body>\n' \
          '  <h1 class="basename">Webcheck report for <a href="%(siteurl)s">%(sitetitle)s</a></h1>\n' \
          % { 'sitetitle':  xml.sax.saxutils.escape(get_title(site.linkMap[site.base])),
              'siteurl':    site.base,
              'version':    config.VERSION })
        # write navigation bar
        fp.write(navbar)
        # write plugin heading
        fp.write('  <h2>%s</h2>\n' % xml.sax.saxutils.escape(report.__title__))
        if hasattr(report,"__description__"):
            fp.write('  <p class="description">\n    %s\n  </p>\n' % xml.sax.saxutils.escape(report.__description__))
        # write plugin contents
        fp.write('  <div class="content">\n')
        report.generate(fp,site)
        fp.write('  </div>\n')
        # write bottom of page
        fp.write( \
          '  <p class="footer">\n' \
          '   Generated %(time)s by <a href="%(homepage)s">webcheck %(version)s</a>\n' \
          '  </p>\n' \
          ' </body>\n' \
          '</html>\n' \
          % { 'time':     xml.sax.saxutils.escape(time.ctime(time.time())),
              'homepage': config.HOMEPAGE,
              'version':  xml.sax.saxutils.escape(config.VERSION) })
        fp.close()
