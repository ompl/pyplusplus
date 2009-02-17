# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import dl
import sys
import unittest
import autoconfig
import fundamental_tester_base
from pyplusplus import code_creators

sys.setdlopenflags(dl.RTLD_NOW | dl.RTLD_GLOBAL)



class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( self, self.EXTENSION_NAME, indexing_suite_version=2, *args  )

    def run_tests(self, module):
        try:
            v = module.create_vector()
            print self.__class__.__name__
            for i in v:
                print i
            print self.__class__.__name__, ' - done'
            print self.__class__.__name__
            for i in v:
                print i
            print self.__class__.__name__, ' - done(2)'
        except Exception, ex:
            print 'Error: ', str( ex )
            
class tester_a_t(tester_t):
    EXTENSION_NAME = 'indexing_suites_v2_bug_a'
    def __init__( self, *args ):
        tester_t.__init__( self, *args )


class tester_b_t(tester_t):
    EXTENSION_NAME = 'indexing_suites_v2_bug_b'
    def __init__( self, *args ):
        tester_t.__init__( self, *args )


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_a_t))
    suite.addTest( unittest.makeSuite(tester_b_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
