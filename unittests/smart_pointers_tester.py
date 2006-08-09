# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus import code_creators

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'smart_pointers'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )
   
    def customize( self, mb ):
        base = mb.class_( 'base' )
        #base.held_type = ''
   
    def create_py_derived( self, module ):
        class py_derived_t( module.base ):
            def __init__( self ):
                module.base.__init__( self )
            
            def get_some_value( self ):
                return 28
        
        return py_derived_t()
        
    def run_tests( self, module):
        da = module.create_auto()
        py_derived = self.create_py_derived( module )
        
        self.failUnless( 11 == da.value )
        ds = module.create_shared()
        self.failUnless( 11 == ds.value )
        
        self.failUnless( 11 == module.ref_auto(da) )
        self.failUnless( 11 == module.ref_shared(ds) )
        
        #why? because in this case held type could not be set
        #self.failUnless( 11 == module.ref_shared(py_derived) )

        self.failUnless( 11 == module.val_auto(da) )
        self.failUnless( 11 == module.val_shared(ds) )

        da = module.create_auto()

        self.failUnless( 11 == module.const_ref_auto(da) )
        self.failUnless( 11 == module.const_ref_shared(ds) )
        
        #TODO: find out why this fails
        #self.failUnless( 19 == module.ref_auto_base_value(da) )
        #self.failUnless( 19 == module.ref_shared_base_value(ds) )

        da = module.create_auto()

        self.failUnless( 19 == module.const_ref_auto_base_value(da) )
        self.failUnless( 19 == module.const_ref_shared_base_value(ds) )
        self.failUnless( 19 == module.const_ref_shared_base_value(py_derived) )

        da = module.create_auto()

        self.failUnless( 19 == module.val_auto_base_value(da) )
        self.failUnless( 19 == module.val_shared_base_value(ds) )
        self.failUnless( 19 == module.val_shared_base_value(py_derived) )
        
        da = module.create_auto()
        
        self.failUnless( 23 == module.val_auto_some_value(da) )
        self.failUnless( 28 == module.val_shared_some_value(py_derived) )

        da = module.create_auto()

        self.failUnless( 23 == module.const_ref_auto_some_value(da) )
        self.failUnless( 28 == module.const_ref_shared_some_value(py_derived) )


def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()