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

class ctypes_base_tester_t(unittest.TestCase):
    _module_ref_ = None
    def __init__( self, base_name, *args, **keywd ):
        unittest.TestCase.__init__( self, *args, **keywd )
        self.__base_name = base_name

    @property
    def base_name( self ):
        return self.__base_name

    @property
    def project_dir( self ):
        return os.path.join( autoconfig.data_directory, 'ctypes', self.base_name )

    @property
    def header( self ):
        return os.path.join( self.project_dir, self.base_name + '.h' )

    @property
    def symbols_file( self ):
        return os.path.join( self.project_dir, 'binaries', self.base_name + '.dll' )

    def setUp( self ):
        if ctypes_base_tester_t._module_ref_:
            return

        autoconfig.scons_config.compile( autoconfig.scons.cmd_build + ' ' + self.base_name )
        mb = ctypes_module_builder_t( [self.header], self.symbols_file, autoconfig.cxx_parsers_cfg.gccxml )
        mb.build_code_creator( self.symbols_file )
        mb.write_module( os.path.join( self.project_dir, 'binaries', self.base_name + '.py' ) )
        sys.path.insert( 0, os.path.join( self.project_dir, 'binaries' ) )
        ctypes_base_tester_t._module_ref_ = __import__( self.base_name )

    @property
    def module_ref(self):
        return self._module_ref_


class tester_t( ctypes_base_tester_t ):
    def __init__( self, *args, **keywd ):
        ctypes_base_tester_t.__init__( self, 'pof', *args, **keywd )

    def test_constructors(self):
        n0 = self.module_ref.pof.number_t()
        self.failUnless( 0 == n0.get_value() )
        n1 = self.module_ref.pof.number_t( ctypes.c_long(32) )
        self.failUnless( 32 == n1.get_value() )
        n2 = self.module_ref.pof.number_t( ctypes.pointer(n1) )
        self.failUnless( 32 == n2.get_value() )

    def test_free_functions(self):
        #the following code fails - difference in the calling conventions
        #TODO: the following test failes, because of the wrong calling convention used
        self.failUnless( self.module_ref.identity_cpp( int(111) ) == 111 )

    def test_get_set_values( self ):
        n0 = self.module_ref.pof.number_t()
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

def create_suite():
    suite = unittest.TestSuite()
    if 'win' in sys.platform:
        suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
