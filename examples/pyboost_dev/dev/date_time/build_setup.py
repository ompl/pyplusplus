#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import shutil

def create( source_dir, target_dir ):
    sys.path.append( source_dir )
    environment = __import__( 'environment' )
    files_dir = os.path.join( source_dir, 'unittests' )
    files = ['date_time.py'
             , 'date_time_zonespec.csv'
             , 'LICENSE_1_0.txt'
             , 'local_time_tester.py'
             , 'posix_time_tester.py'
             , 'gregorian_tester.py' 
             , 'test_all.py' 
    ]
    
    if 'win32' == sys.platform:
        files.append( '_date_time_.pyd' )
    else:
        files.append( '_date_time_.so' )


    files = map( lambda fname: os.path.join( files_dir, fname ), files )
    if 'win32' == sys.platform:
        files.append( os.path.join( environment.settings.boost_libs_path, 'boost_python.dll' ) )
        files.append( os.path.join( environment.settings.boost_libs_path, 'boost_date_time-vc71-mt-1_33_1.dll' ) )
    else:
        files.append( os.path.join( environment.settings.boost_libs_path, 'libboost_python.so' ) )
        files.append( os.path.join( environment.settings.boost_libs_path, 'libboost_python.so.1.33.1' ) )
        files.append( os.path.join( environment.settings.boost_libs_path, 'libboost_date_time-gcc-1_33_1.so' ) )
        files.append( os.path.join( environment.settings.boost_libs_path, 'libboost_date_time-gcc-1_33_1.so.1.33.1' ) )
    for f in files:
        shutil.copy( f, target_dir )