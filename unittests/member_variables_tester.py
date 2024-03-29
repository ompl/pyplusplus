# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import ctypes
import unittest
import fundamental_tester_base

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'member_variables'

    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__(
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize(self, mb ):
        mb.variable( 'prefered_color' ).alias = 'PreferedColor'
        mb.classes().always_expose_using_scope = True
        image = mb.class_( 'image_t' )
        image.variable( 'data' ).expose_address = True
        image.variable( 'none_image' ).expose_address = True
        mb.class_( 'Andy' ).variable('userData').expose_address = True

    def change_default_color( self, module ):
        module.point.default_color = module.point.color.blue

    def change_prefered_color( self, module ):
        xypoint = module.point()
        xypoint.PreferedColor = module.point.color.blue

    def set_b( self, bf, value ):
        bf.b = value

    def run_tests(self, module):
        sbk = module.status_bits_keeper_t()
        sb = sbk.status_bits
        sb.bcr = 2
        self.assertTrue( sbk.get_sb_bcr() == 2 )

        self.failIfRaisesAny( module.point )
        xypoint = module.point()
        self.assertTrue( module.point.instance_count == 1)
        self.assertTrue( xypoint.instance_count == 1)
        self.assertTrue( module.point.default_color == module.point.color.red)
        self.assertTrue( xypoint.default_color == module.point.color.red)
        self.assertTrue( xypoint.x == -1)
        self.assertTrue( xypoint.y == 2 )
        self.assertTrue( xypoint.PreferedColor == xypoint.color.blue )
        self.assertRaises( Exception, self.change_default_color )
        self.assertRaises( Exception, self.change_prefered_color )

        bf = module.bit_fields_t()
        module.set_a( bf, 1 )
        self.assertTrue( 1 == bf.a )
        self.assertTrue( bf.b == module.get_b( bf ) )
        self.failIfNotRaisesAny( lambda: self.set_b( bf, 23 ) )

        tree = module.create_tree()
        self.assertTrue( tree.parent is None )
        self.assertTrue( tree.data.value == 0 )
        self.assertTrue( tree.right is None )
        self.assertTrue( tree.left )
        self.assertTrue( tree.left.data.value == 1 )

        tree.right = module.create_tree()
        self.assertTrue( tree.right.parent is None )
        self.assertTrue( tree.right.data.value == 0 )
        self.assertTrue( tree.right.right is None )
        self.assertTrue( tree.right.left )
        self.assertTrue( tree.right.left.data.value == 1 )

        mem_var_str = module.mem_var_str_t()
        mem_var_str.identity( module.mem_var_str_t.class_name )

        image = module.image_t()

        data_type = ctypes.POINTER( ctypes.c_int )
        data = data_type.from_address( image.data )
        for j in range(5):
            self.assertTrue( j == data[j] )

        int_array = ctypes.c_int * 5
        array = int_array()
        for i in range( 5 ):
            array[i] = 2*i
        image.data = ctypes.addressof(array)
        data = data_type.from_address( image.data )
        for j in range(5):
            self.assertTrue( j*2 == data[j] )

        data_type = ctypes.POINTER( ctypes.c_int )
        data = data_type.from_address( module.image_t.none_image )
        self.assertTrue( 1997 == data.contents.value )

        array = module.array_t()
        self.assertTrue( len( array.ivars ) == 10 )

        ivars = array.ivars
        del array #testing call policies
        for i in range(20):
            for index in range(10):
                self.assertTrue( ivars[index] == -index )

        array = module.array_t()
        for index in range( len(array.ivars) ):
            array.ivars[index] = index * index
            self.assertTrue( array.get_ivars_item( index ) == index * index )

        #~ import pdb
        #~ pdb.set_trace()

        self.assertTrue( len( module.array_t.vars ) == 3 )
        for i in range( len( module.array_t.vars ) ):
            self.assertTrue( module.array_t.vars[i].value == -9 )

        self.assertTrue( len( module.array_t.vars_nonconst ) == 3 )
        for i in range( len( module.array_t.vars_nonconst ) ):
            self.assertTrue( module.array_t.vars_nonconst[i].value == -9 )

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
