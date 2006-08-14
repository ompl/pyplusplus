#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest

#__pychecker__ = 'limit=1000'
#import pychecker.checker


build_dir = os.path.abspath( os.path.join( os.curdir, 'temp' ) )
data_directory = os.path.abspath( os.path.join( os.curdir, 'data' ) )
sys.path.append( os.path.join( os.curdir, '..' ) )

from environment import scons, boost, python, gccxml

class scons_config:
    libs = ['boost_python']
    libpath = [ boost.libs, python.libs ]
    cpppath = [ boost.include, python.include ]    
    include_dirs = cpppath + [data_directory]
    
    @staticmethod
    def create_sconstruct():
        code = [
            "SharedLibrary( target=r'%(target)s'"
          , "    , source=[ %(sources)s ]"
          , "    , LIBS=[ %s ]" % ','.join( [ '"%s"' % lib for lib in scons_config.libs ] )
          , "    , LIBPATH=[ %s ]" % ','.join( [ '"%s"' % path for path in scons_config.libpath ] )
          , "    , CPPPATH=[ %s ]" % ','.join( [ '"%s"' % path for path in scons_config.include_dirs] )
          , "    , CCFLAGS=[ %s ]" % ','.join( [ '"%s"' % flag for flag in scons.ccflags ] )
          , "    , SHLIBPREFIX=''"
          , "    , SHLIBSUFFIX='%s'" % scons.suffix #explicit better then implicit
          , ")" ]
        return os.linesep.join( code )
    
#I need this in order to allow Python to load just compiled modules    
sys.path.append( build_dir )

os.chdir( build_dir )

if sys.platform == 'linux2':	    
    LD_LIBRARY_PATH = 'LD_LIBRARY_PATH'
    if not os.environ.has_key( LD_LIBRARY_PATH ) \
       or not set( scons_config.libpath ).issubset( set( os.environ[LD_LIBRARY_PATH].split(':') ) ):
        #see http://hathawaymix.org/Weblog/2004-12-30
        print 'error: LD_LIBRARY_PATH has not been set'
else:    
    PATH = os.environ.get( 'PATH', '' )
    PATH=PATH + ';' + ';'.join( scons_config.libpath )
    os.environ['PATH'] = PATH
