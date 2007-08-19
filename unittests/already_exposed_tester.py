# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import autoconfig
from pyplusplus import utils
import fundamental_tester_base

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'already_exposed'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )
                                                                    
    def customize(self, mb ):
        exposed_db = utils.exposed_decls_db_t()
        map( exposed_db.expose, mb.decls(recursive=True) )
        exposed_db.save( autoconfig.build_dir )
        mb.register_module_dependency( autoconfig.build_dir )
        mb.decls().exclude()
        mb.namespace( 'already_exposed' ).include()

    def run_tests(self, module):        
        self.failUnless(  'ae_t' not in dir( module ) )
        self.failUnless(  'ae_e' not in dir( module ) )
    
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
