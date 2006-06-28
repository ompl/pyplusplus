# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pygccxml import declarations
from pyplusplus import module_builder


class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'indexing_suites2'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , indexing_suite_version=2
            , *args)

    #~ @staticmethod
    #~ def matcher( item, decl ):
        #~ if not declarations.vector_traits.is_my_case( decl ):
            #~ return False
        #~ value_type = declarations.vector_traits.value_type(decl)
        #~ if item is value_type:
            #~ return True
        #~ return False
    
    def customize(self, generator):
        ivector = generator.global_ns.typedef( 'ivector' )
        ivector = declarations.remove_declarated( ivector.type )
        ivector.indexing_suite.disable_method( 'extend' )
        ivector.indexing_suite.disable_methods_group( 'reorder' )
        #ivector.indexing_suite.call_policies = module_builder.call_policies.default_call_policies()
       
    def run_tests( self, module):
        iv = module.ivector()
        #~ items = module.items_t()
        #~ item = module.item_t()
        #~ item.value = 1977
        #~ items.append( item )
        #~ self.failUnless( module.get_value( items, 0 ).value == 1977 )
        #~ self.failUnless( len( items ) == 1 )
    
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
