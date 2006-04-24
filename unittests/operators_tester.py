# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus.module_builder import call_policies

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'operators'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize( self, mb ):
        mb.global_ns.exclude()

        rational = mb.class_('rational<long int>')
        rational.include()
        rational.alias = "pyrational"
        
        r_assign = rational.calldef( 'assign', recursive=False )
        r_assign.call_policies = call_policies.return_self()

        foperators = mb.free_operators( lambda decl: 'rational<long int>' in decl.decl_string )
        foperators.include()
            
        bad_rational = mb.class_('bad_rational' )
        bad_rational.include()

    def run_tests(self, module):      
        pyrational = module.pyrational
        self.failUnless( pyrational( 28, 7) == 4 )
        self.failUnless( pyrational( 28, 7) == pyrational( 4 ) )
        
        r1 = pyrational( 5, 7 )
        
        r1 += pyrational( 4, 11 )
        r2 = pyrational( 5*11 + 7*4, 7*11 )
        self.failUnless( r1 == r2 )
        
        r1 -= pyrational( 5, 7)
        self.failUnless( r1 == pyrational( 4, 11) )
        
        r1 *= 2
        self.failUnless( r1 == pyrational( 8, 11) )
        
        r1 /= 3
        self.failUnless( r1 == pyrational( 8, 33) )
    
        r2 = not r1 
        self.failUnless( r2 == False )
        
        self.failUnless( 0 < r1 )
        
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
