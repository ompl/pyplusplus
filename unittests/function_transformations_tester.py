# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus.function_transformers.arg_policies import *

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'function_transformations'

    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__(
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize( self, mb ):
        image = mb.class_( "image_t" )
        image.member_function( "get_size" ).function_transformers.extend([Output(1), Output(2)])

    def run_tests(self, module):
        img = module.image_t( 2, 6)
        h,w = img.get_size()
        self.failUnless( h == 2 and w == 6 )

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
