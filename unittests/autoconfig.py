#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
from sets import Set as set

#__pychecker__ = 'limit=1000'
#import pychecker.checker


boost_path = ''
gccxml_path = ''
data_directory = ''

if sys.platform == 'linux2':
    boost_path = '/home/roman/boost_cvs'
    gccxml_path = r'/home/roman/gccxml/bin/gccxml'    
elif sys.platform == 'win32':
    boost_path = 'd:/boost_cvs'
    gccxml_path = r'C:\Tools\GCC_XML\bin\gccxml.exe'
else:
    raise RuntimeError( 'There is no configuration for "%s" platform.' % sys.platform )

def pyplusplus_location():
    global __name__
    location = os.path.split( os.path.realpath( __name__ ) )[0]
    location = os.path.normpath( os.path.join( location, '..' ) )
    return location
    
try:
    import pyplusplus
    print "unittests will run on installed version"
    package_location = pyplusplus.__path__[0]
    data_directory = os.path.split( pyplusplus.__file__ )[0]
    data_directory = os.path.join( data_directory, 'unittests/data' )        
except ImportError:
    package_location = pyplusplus_location()    
    print "unittests will run on development version"
    print "    package location: ", package_location
    data_directory = os.path.join( package_location, 'unittests', 'data' )        
    print "    data location   : ", data_directory
    sys.path.append( os.path.split( package_location )[0] )

class scons_config:
    libs = ['boost_python']
    build_dir = os.path.join(  package_location, 'unittests', 'temp' )
    if not os.path.exists( build_dir ):
        os.mkdir( build_dir )
    if sys.platform == 'linux2':	
        libpath = [ '/home/roman/boost_cvs/bin' ]
        cpppath = [ boost_path
                    , '/usr/include/python2.4' ]
        ccflags = []
        cmd_clean = 'scons --clean --file=%s'
        cmd_build = 'scons --file=%s'
        suffix = '.so'
    elif sys.platform == 'win32':
        libpath = [ 'd:/boost_cvs/bin'
                  , 'c:/python/libs' ]
        cpppath = [ boost_path, 'c:/python/include' ]
        ccflags = ['/MD', '/EHsc', '/GR' ] #multi-threading dll + 
        cmd_clean = 'c:/python/scons.bat --clean --file=%s'
        cmd_build = 'c:/python/scons.bat --file=%s'
        suffix = '.dll'
    else:
        raise RuntimeError( 'There is no configuration for "%s" platform.' % sys.platform )
    
    def _make_source_str_const(lst):
        return [ '"' + item + '"' for item in lst ]

    def create_sconstruct():
        include_dirs = scons_config.cpppath[:]
        include_dirs.append( package_location )
        code = [
            "SharedLibrary( target=r'%(target)s'"
          , "    , source=[ %(sources)s ]"
          , "    , LIBS=[ %s ]" % ','.join( [ '"%s"' % lib for lib in scons_config.libs ] )
          , "    , LIBPATH=[ %s ]" % ','.join( [ '"%s"' % path for path in scons_config.libpath ] )
          , "    , CPPPATH=[ %s ]" % ','.join( [ '"%s"' % path for path in include_dirs] )
          , "    , CCFLAGS=[ %s ]" % ','.join( [ '"%s"' % flag for flag in scons_config.ccflags ] )
          , "    , SHLIBPREFIX=''"
          , "    , SHLIBSUFFIX='%s'" % scons_config.suffix #explicit better then implicit
          , ")" ]
        return os.linesep.join( code )
    create_sconstruct = staticmethod(create_sconstruct)
    
sys.path.append( scons_config.build_dir )
os.chdir( scons_config.build_dir )


if sys.platform == 'linux2':	    
    LD_LIBRARY_PATH = 'LD_LIBRARY_PATH'
    if not os.environ.has_key( LD_LIBRARY_PATH ) \
       or not set( scons_config.libpath ).issubset( set( os.environ[LD_LIBRARY_PATH].split(':') ) ):
        #see http://hathawaymix.org/Weblog/2004-12-30
        print 'error: LD_LIBRARY_PATH has not been set'
elif sys.platform == 'win32':    
    PATH = os.environ.get( 'PATH', '' )
    PATH=PATH + ';' + ';'.join( scons_config.libpath )
    os.environ['PATH'] = PATH
else:
    raise RuntimeError( 'There is no configuration for "%s" platform.' % sys.platform )