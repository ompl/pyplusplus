#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import sys

class settings:  
    gccxml_path = ''    
    pygccxml_path = ''
    pyplusplus_path = ''
    working_dir = ''
            
    if sys.platform == 'linux2':
        gccxml_path = '/home/roman/gccxml/bin/gccxml'    
        pygccxml_path = '/home/roman/pygccxml_sources/source'
        pyplusplus_path = '/home/roman/pygccxml_sources/source'
        working_dir = '/home/roman/pygccxml_sources/source/pyplusplus/examples/tutorials'
    elif sys.platform == 'win32':
        gccxml_path = 'c:/tools/gcc_xml/bin'    
        pygccxml_path = 'd:/pygccxml_sources/source'
        pyplusplus_path = 'd:/pygccxml_sources/source'
        working_dir = 'd:/pygccxml_sources/source/pyplusplus/examples/tutorials'
    else:
        raise RuntimeError( 'There is no configuration for "%s" platform.' % sys.platform )

sys.path.append( settings.pygccxml_path )
sys.path.append( settings.pyplusplus_path )
