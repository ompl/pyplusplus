# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import math
import unittest
import fundamental_tester_base
from pygccxml import declarations
from pyplusplus import function_transformers as ft
from pyplusplus.module_builder import call_policies


class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'ft_inout_bugs'

    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__(
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize( self, mb ):        
        #~ mb.global_ns.exclude()
        #~ mb.namespace( 'tests' ).include()
        set_flag = mb.calldefs( 'set_flag' )
        set_flag.add_transformation( ft.inout(1) )
        
    def run_tests(self, module):
        x = False
        self.failUnless( True == module.set_flag( True, x ) )
        self.failUnless( False == module.set_flag( False, x ) )
        b = module.base()
        self.failUnless( True == b.set_flag( True, x ) )
        self.failUnless( False == b.set_flag( False, x ) )
        inventor = module.inventor()        
        self.failUnless( False == inventor.set_flag( True, x ) )
        self.failUnless( True == inventor.set_flag( False, x ) )
        
        
def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
