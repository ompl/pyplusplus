# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus import module_builder


class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'indexing_suites'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )
    
    def customize(self, generator):
        item_cls = generator.class_( 'item_t' )
        item_cls.indexing_suites.append( module_builder.vector_indexing_suite_t( 'items_t' ) )
       
    def run_tests( self, module):
        items = module.items_t()
        item = module.item_t()
        item.value = 1977
        items.append( item )
        self.failUnless( module.get_value( items, 0 ).value == 1977 )
        self.failUnless( len( items ) == 1 )
    
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
