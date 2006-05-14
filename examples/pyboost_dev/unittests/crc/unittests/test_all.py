#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import sys
sys.path.append( '../..' )

import unittest
import crc

class consts:
    data = [ 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39 ]
    crc_ccitt_result = 0x29B1
    crc_16_result = 0xBB3D
    crc_32_result = 0xCBF43926

class tester_t( unittest.TestCase ):
    def __init__( self, *args ):
        unittest.TestCase.__init__( self, *args )
    
    def fundamental_test( self, cls, data, expected ):
        inst = cls()
        inst.process_bytes( data )
        print inst.checksum()
        #self.failUnless( inst.checksum() == expected )
        
    def compute_test( self, fast_crc, slow_crc, expected ):
        fast_crc.process_bytes( consts.data, len(consts.data) )
        slow_crc.process_bytes( consts.data, len(consts.data) )
    
    def test( self ):
        self.fundamental_test( crc.crc_ccitt, consts.data, consts.crc_ccitt_result )

    def test_small_crc_3( self ):
        #The CRC standard is a SDH/SONET Low Order LCAS control word with CRC-3
        #taken from ITU-T G.707 (12/03) XIII.2.

        #Four samples, each four bytes should all have a CRC of zero
        samples = \
        [
            [ 0x3A, 0xC4, 0x08, 0x06 ],
            [ 0x42, 0xC5, 0x0A, 0x41 ],
            [ 0x4A, 0xC5, 0x08, 0x22 ],
            [ 0x52, 0xC4, 0x08, 0x05 ]
        ]

        # Basic computer
        tester1 = crc.basic[3]( 0x03 ) #same as crc.crc_basic_3
    
        tester1.process_bytes( samples[0] )
        self.failUnless( tester1.checksum() == 0 )
    
        tester1.reset()
        tester1.process_bytes( samples[1] )
        self.failUnless( tester1.checksum() == 0 )
    
        tester1.reset()
        tester1.process_bytes( samples[2] )
        self.failUnless( tester1.checksum() == 0 )
    
        tester1.reset()
        tester1.process_bytes( samples[3] )
        self.failUnless( tester1.checksum() == 0 )
    
        # Optimal computer
        #define PRIVATE_CRC_FUNC   boost::crc<3, 0x03, 0, 0, false, false>
        #define PRIVATE_ACRC_FUNC  boost::augmented_crc<3, 0x03>
    
        #self.failUnless( 0 == PRIVATE_CRC_FUNC(samples[0], 4) )
        #self.failUnless( 0 == PRIVATE_CRC_FUNC(samples[1], 4) )
        #self.failUnless( 0 == PRIVATE_CRC_FUNC(samples[2], 4) )
        #self.failUnless( 0 == PRIVATE_CRC_FUNC(samples[3], 4) )
    
        # maybe the fix to CRC functions needs to be applied to augmented CRCs?
    
        #undef PRIVATE_ACRC_FUNC
        #undef PRIVATE_CRC_FUNC
    
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t) )
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
