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
    EXTENSION_NAME = 'function_adaptor'

    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__(
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize(self, mb ):
        for suffix in [ 'zero', 'one', 'two' ]:
            mb.calldef( 'get_' + suffix ).adaptor = 'PYPP_IDENTITY'
            mb.calldef( 'get_' + suffix ).create_with_signature = False
    def run_tests( self, module):
        foo = module.foo_t()
        self.failUnless( foo.get_zero() == 0 )
        self.failUnless( foo.get_two() == 2 )
        self.failUnless( module.foo_t.get_two() == 2 )
        self.failUnless( module.get_one() == 1 )

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
