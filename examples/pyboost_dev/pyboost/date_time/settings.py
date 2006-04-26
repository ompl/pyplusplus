#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys

_script_dir = os.path.split( os.path.abspath( sys.argv[0] ) )[0]
environment_path = os.path.normpath( os.path.join( _script_dir, '..', '..', '..', '..' ) )

sys.path.append( environment_path )

from environment import boost, scons, gccxml

module_name = '_date_time_'
working_dir = _script_dir
generated_files_dir = os.path.join( _script_dir, 'generated' )
unittests_dir = os.path.join( _script_dir, '..', '..', 'unittests', 'date_time' )
date_time_pypp_include = os.path.join( _script_dir, 'include' )

undefined_symbols = [ '__MINGW32__' ]
defined_symbols = ['BOOST_DATE_TIME_NO_MEMBER_INIT']
if sys.platform == 'win32':
    defined_symbols.extend( [ 'BOOST_DATE_TIME_DYN_LINK' ] )