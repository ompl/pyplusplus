# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus import code_creators

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'special_operators'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )
    
    def create_python_call( self, module ):
        class python_call_t( module.base_call_t ):
            def __init__( self ):
                module.base_call_t.__init__( self )
            def __call__( self, x, y ):
                return x * y
        return python_call_t()
    
    def run_tests( self, module):
        opers = module.operators_t()
        self.assertTrue( 28 == int( opers ) )
        self.assertTrue( 3.5 == float( opers ) )
        self.assertTrue( "hello world" == str( opers ) )
        to_string = module.to_string_t()
        try:
            self.assertTrue( "hello world" == str(to_string) )
        except:
            self.assertTrue( "hello world" == to_string.as__scope_std_scope_string() )
        to_wstring = module.to_wstring_t()
        self.assertTrue( "hello world" == str( to_wstring ) )
        call = module.call_t()
        self.assertTrue( 7 == call( 2, 5 ) )
        self.assertTrue( 3.5 == call( 3.5 ) )
        python_call = self.create_python_call( module )
        self.assertTrue( 12 == module.virtual_call( python_call, 3, 4 ) )

        derived_call = module.derive_call_t()
        self.assertTrue( 7 == module.virtual_call( derived_call, 3, 4 ) )

def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()