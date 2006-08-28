# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'no_init'

    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__(
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def create_py_controller( self, module ):
        class py_controller_t( module.controller_i ):
            def __init__( self ):
                module.controller_i.__init__( self )
                self.value = True

            def get_value(self):
                return self.value

            def set_value( self, v ):
                self.value = v
        return py_controller_t()

    def run_tests(self, module):
        controller = self.create_py_controller( module )
        self.failUnless( 1 == module.get_value( controller ) )
        controller.set_value( False )
        self.failUnless( 0 == module.get_value( controller ) )
        self.failUnless( -1 == module.get_value( None ) )

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
