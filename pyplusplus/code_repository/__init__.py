# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
Code repository package is used as a repository of C++ classes/functions.
Those classes/functions solve problems, that are typical to most projects.
Right now, this package contains set of classes that help to export one
dimensional static arrays. For example:

C{char data[23];}

"""

import array_1
import gil_guard
import named_tuple
import convenience
import return_range
import ctypes_utils
import call_policies
import indexing_suite
import ctypes_integration

all = [ array_1
        , gil_guard
        , convenience
        , call_policies
        , named_tuple
        , return_range
        , ctypes_utils
        , ctypes_integration ]

all.extend( indexing_suite.all )

headers = map( lambda f: f.file_name, all )

def i_depend_on_them( fname ):
    """returns list of files, the file fname depends on"""
    if fname in indexing_suite.headers:
        result = indexing_suite.all[:]
        del result[ indexing_suite.headers.index( fname ) ]
        return result
    else:
        return []
