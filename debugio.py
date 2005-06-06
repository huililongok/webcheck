
# debugio.py - output logging module
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

"""debugio.py: debugging and input/output module

   This module contains facilities for logging program output.  The use of
   this module is really simple: import it, set loglevel, and use debug(),
   info(), warn() and error() whenever you want to print something.
"""

import sys

# log levels that can be used
ERROR=0
WARN=1
INFO=2
DEBUG=3

# initialize logging at default level
loglevel=INFO

def debug(msg):
    """log the message to stderr if loglevel will allow it"""
    if loglevel>=DEBUG:
        print >>sys.stderr,"webcheck: DEBUG: "+str(msg)

def info(msg):
    """log the message to stdout if loglevel will allow it"""
    if loglevel>=INFO:
        # FIXME: remove ">>sys.stderr," part once plugin system is rewritten
        print >>sys.stderr,"webcheck: "+str(msg)

def warn(msg):
    """log a warning to stderr if loglevel will allow it"""
    if loglevel>=WARN:
        print >>sys.stderr,"webcheck: Warning: "+str(msg)

def error(msg):
    """log an error to stderr if loglevel will allow it"""
    if loglevel>=ERROR:
        print >>sys.stderr,"webcheck: Error: "+str(msg)
