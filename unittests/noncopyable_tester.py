# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'noncopyable'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )
        
    def run_tests(self, module):      
        self.assertTrue( module.a_t.get_a() == 'a' )
        self.assertTrue( module.b_t.get_b() == 'b' )
        self.assertTrue( module.c_t.get_c() == 'c' )
        self.assertTrue( module.d_t.get_d() == 'd' )
        self.assertTrue( module.dd_t.get_dd() == 'D' )
        
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()