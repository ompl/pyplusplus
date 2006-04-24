# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
from distutils import sysconfig
from distutils.core import setup

setup( name="pyplusplus"
       , description="pyplusplus is a framework of components for creating C++ code generator for boost.python library"
       , author="Roman Yakovenko"
       , author_email="roman.yakovenko@gmail.com"
       , url='http://pyplusplus.sourceforge.net'
       , scripts= map( lambda script_name: os.path.join( 'pyplusplus', 'scripts', script_name )
                       , os.listdir( os.path.join( 'pyplusplus', 'scripts' ) ) )
       , packages=[ 'pyplusplus'
                    , 'pyplusplus.gui'
                    , 'pyplusplus.file_writers'
                    , 'pyplusplus.code_creators'
                    , 'pyplusplus.module_creator'
                    , 'pyplusplus.code_repository'
                    , 'pyplusplus.decl_wrappers'
                    , 'pyplusplus.module_builder'
                    , 'pyplusplus.utils'
                    , 'pyplusplus._logging_']
)
