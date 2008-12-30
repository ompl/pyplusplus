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

        #the following code fails - difference in the calling conventions
        #TODO: the following test failes, because of the wrong calling convention used
        #self.failUnless( ctypes_pof.identity_cpp( int(111) ) == 111 )

        #testing constructors
        n0 = ctypes_pof.pof.number_t()
        self.failUnless( 0 == n0.get_value() )
        n1 = ctypes_pof.pof.number_t( ctypes.c_long(32) )
        self.failUnless( 32 == n1.get_value() )
        n2 = ctypes_pof.pof.number_t( ctypes.pointer(n1) )
        self.failUnless( 32 == n2.get_value() )

        #testing get/set value
        n0.set_value( 1977 )
        self.failUnless( 1977 == n0.get_value() )

    #the following functionality is still missing
    #~ def test_operator_assign( self ):
        #~ obj1 = number_t(1)
        #~ obj2 = number_t(2)
        #~ x = obj1.operator_assign( obj2 )
        #~ #there are special cases, where ctypes could introduce "optimized" behaviour and not create new python object
        #~ self.failUnless( x is obj1 )
        #~ self.failUnless( obj1.m_value == obj2.m_value )

    #~ def test_clone( self ):
        #~ obj1 = number_t(1)
        #~ obj2 = obj1.clone()
        #~ self.fail( obj1.get_value() == obj2.get_value() )


    #~ def test_bsc( self ):
        #~ root = r'E:\Documents and Settings\romany\Desktop\ToInstall\bsckit70\bscsdk'
        #~ mb = ctypes_module_builder_t( [os.path.join( root, 'bsc.h' )]
                                      #~ , os.path.join( root, 'msbsc70.dll' ), autoconfig.cxx_parsers_cfg.gccxml )
        #~ mb.build_code_creator( self.symbols_file )
        #~ mb.write_module( os.path.join( root, 'bsc.py' ) )


def create_suite():
    suite = unittest.TestSuite()
    if 'win' in sys.platform:
        suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
