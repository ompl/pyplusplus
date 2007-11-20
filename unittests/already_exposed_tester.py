# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import autoconfig
from pyplusplus import utils
from pyplusplus import module_builder
import fundamental_tester_base

class tester_t( unittest.TestCase ):    
    def test(self):
        exposed_db = utils.exposed_decls_db_t()
        
        fpath = os.path.join( autoconfig.data_directory, 'already_exposed_to_be_exported.hpp' )
        mb = module_builder.module_builder_t( [module_builder.create_source_fc( fpath )]
                                              , gccxml_path=autoconfig.gccxml.executable )
        
        mb.global_ns.exclude()
        mb.namespace( 'already_exposed' ).include()
        exposed_db.register_decls( mb.global_ns )
        exposed_db.save( autoconfig.build_dir )
        mb.register_module_dependency( autoconfig.build_dir )
        mb.class_( 'ae_derived' ).include()

        mb.build_code_creator( 'xxx' )
        
        body = mb.code_creator.body
        self.failUnless( 1 == len( body.creators ) )
        ae_derived_code = body.creators[0].create()
        self.failUnless( mb.class_( 'ae_base' ).decl_string in ae_derived_code )
    
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
