# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus.module_builder import call_policies

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'call_policies'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )
                                                                    
    def customize(self, mb ):
        mb.calldef( 'return_second_arg' ).call_policies = call_policies.return_arg( 2 )
        mb.calldef( 'return_self' ).call_policies = call_policies.return_self()

    def run_tests(self, module):        
        self.failUnless( module.compare( module.my_address() ) )

        x = module.return_second_arg( 1, 2, 3)
        self.failUnless( x == 2 )
        
        x = module.dummy()
        y = module.return_self( x, 0 )
        self.failUnless( x.id() == y.id() )

        y = module.copy_const_reference( x )
        self.failUnless( x.id() != y.id() )
        
        cont = module.container()
        self.failUnless( 1977 == cont[1977] )

def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()