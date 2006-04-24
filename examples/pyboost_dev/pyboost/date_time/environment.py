#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys

class settings:    
    module_name = '_date_time_'
    boost_path = ''
    boost_libs_path = ''
    gccxml_path = ''    
    pygccxml_path = ''
    pyplusplus_path = ''
    python_libs_path = ''
    python_include_path = ''
    working_dir = ''
    generated_files_dir = ''
    unittests_dir = ''
    date_time_pypp_include = ''
    
    defined_symbols = ['BOOST_DATE_TIME_NO_MEMBER_INIT']
                        
    if sys.platform == 'win32':
        defined_symbols.extend( [ 'BOOST_DATE_TIME_DYN_LINK' ] )
    
    undefined_symbols = [ '__MINGW32__' ]

if sys.platform == 'linux2':
    settings.boost_path = '/home/roman/boost_cvs'
    settings.boost_libs_path = '/home/roman/boost_cvs/bin'
    settings.gccxml_path = '/home/roman/gccxml/bin/gccxml'    
    settings.pygccxml_path = '/home/roman/pygccxml_sources/source'
    settings.pyplusplus_path = '/home/roman/pygccxml_sources/source'
    settings.python_include_path = '/usr/include/python2.3'
    settings.working_dir = '/home/roman/pygccxml_sources/source/pyplusplus/examples/py_date_time'
elif sys.platform == 'win32':
    settings.boost_path = 'd:/boost_cvs'
    settings.boost_libs_path = 'd:/boost_cvs/bin'
    settings.gccxml_path = 'c:/tools/gcc_xml/bin'    
    settings.pygccxml_path = 'd:/pygccxml_sources/source'
    settings.pyplusplus_path = 'd:/pygccxml_sources/source'
    settings.python_libs_path = 'c:/python/libs'
    settings.python_include_path = 'c:/python/include'
    settings.working_dir = 'd:/pygccxml_sources/source/pyplusplus/examples/py_date_time'
else:
    raise RuntimeError( 'There is no configuration for "%s" platform.' % sys.platform )

settings.generated_files_dir = os.path.join( settings.working_dir, 'generated' )
settings.unittests_dir = os.path.join( settings.working_dir, 'unittests' )
settings.date_time_pypp_include = os.path.join( settings.working_dir, 'include' )

sys.path.append( settings.pygccxml_path )
sys.path.append( settings.pyplusplus_path )
