# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This package contains few classes, that writes L{code_creators.module_t} to files.

Right now 2 strategies were implemented:

    1. classic strategy of deviding classes to files one class in one header + source 
       files.
   
    2. all code is written in one file.

"""

import types
from writer import writer_t
from single_file import single_file_t
from multiple_files import multiple_files_t

def write_file( data, file_path ):
    if isinstance( data, types.StringTypes ):
        writer_t.write_file( data, file_path )
    else:
        sf = single_file_t( data, file_path )
        sf.write()
    
def write_multiple_files( extmodule, dir_path ):
    mfs = multiple_files_t( extmodule, dir_path )
    mfs.write()