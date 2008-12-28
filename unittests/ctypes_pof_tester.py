# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import ctypes
import unittest
import autoconfig
from pyplusplus.module_builder import ctypes_module_builder_t

class tester_t(unittest.TestCase):
    def __init__( self, *args, **keywd ):
        unittest.TestCase.__init__( self, *args, **keywd )
        self.project_dir = os.path.join( autoconfig.data_directory, 'ctypes_pof' )
        self.header = os.path.join( self.project_dir, 'mydll.h' )
        self.symbols_file = os.path.join( self.project_dir, 'release', 'mydll.dll' )
        self.module_name = 'ctypes_pof'

    def test(self):
        mb = ctypes_module_builder_t( [self.header], self.symbols_file, autoconfig.cxx_parsers_cfg.gccxml )
        #~ mb.print_declarations()
        mb.build_code_creator( self.symbols_file )
        mb.write_module( os.path.join( autoconfig.build_directory, self.module_name + '.py' ) )
        #mb.code_creator.create()
        sys.path.append( autoconfig.build_directory )
        import ctypes_pof
        print ctypes_pof.identity( 23 )
        self.failUnless( ctypes_pof.identity( 23 ) == 23 )

def create_suite():
    suite = unittest.TestSuite()
    if 'win' in sys.platform:
        suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
