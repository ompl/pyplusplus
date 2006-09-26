# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus.function_transformers.arg_policies import *
from pyplusplus.decl_wrappers import *

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'function_transformations'

    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__(
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize( self, mb ):
        image = mb.class_( "image_t" )
        image.member_function( "get_size" ).function_transformers.extend([output_t(1), output_t(2)])
        image.member_function( "get_one_value" ).function_transformers.extend([output_t(1)])
        image.member_function( "get_size2" ).function_transformers.extend([output_t(1), output_t(2)])
        image.member_function( "input_arg" ).function_transformers.extend([input_t(1)])
        image.member_function( "fixed_input_array" ).function_transformers.extend([input_array_t(1,3)])
        image.member_function( "fixed_output_array" ).function_transformers.extend([output_array_t(1,3)])
        mb.free_function("get_cpp_instance").call_policies = return_value_policy(reference_existing_object)
        mb.variable( "cpp_instance" ).exclude()
        
        cls = mb.class_("no_virtual_members_t")
        cls.member_function("member").function_transformers.append(output_t(1))

        #cls = mb.class_("ft_private_destructor_t")
        #cls.member_function("get_value").function_transformers.append(output_t(1))

        mb.decls(lambda decl: decl.name[0]=="_").exclude()

    def run_tests(self, module):
        """Run the actual unit tests.
        """
        
        ####### Do the tests directly on the wrapper C++ class ########
        
        img = module.image_t( 2, 6)

        # Check a method that returns two values by reference
        self.assertEqual(img.get_size(), (2,6))

        # Check a method that only returns one value by reference
        self.assertEqual(img.get_one_value(), 2)

        # Check if the C++ class can also be passed back to C++
        self.assertEqual(module.get_image_one_value(img), 2)

        # Check get_size2()
        self.assertEqual(img.get_size2(), (0,2,6))
        self.assertEqual(img.get_size2(1), (1,2,6))

        # Check the input_arg method
        self.assertEqual(img.input_arg(5), 5)

        # Check the fixed_input_array method
        self.assertEqual(img.fixed_input_array([1,2,3]), 6)
        self.assertEqual(img.fixed_input_array((1,2,3)), 6)
        self.assertRaises(ValueError, lambda : img.fixed_input_array([1,2,3,4]))
        self.assertRaises(ValueError, lambda : img.fixed_input_array([1,2]))
        self.assertRaises(ValueError, lambda : img.fixed_input_array(1))
        self.assertRaises(ValueError, lambda : img.fixed_input_array(None))

        # Check the fixed_output_array method
        self.assertEqual(img.fixed_output_array(), [1,2,3])

        ####### Do the tests on a class derived in Python ########
        
        class py_image1_t(module.image_t):
            def __init__(self, h, w):
                module.image_t.__init__(self, h, w)
                self.fixed_output_array_mode = 0

            # Override a virtual method
            def get_one_value(self):
                return self.m_height+1

            def fixed_output_array(self):
                # Produce a correct return value
                if self.fixed_output_array_mode==0:
                    return (2,5,7)
                # Produce the wrong type
                elif self.fixed_output_array_mode==1:
                    return 5
                # Produce a sequence with the wrong number of items
                elif self.fixed_output_array_mode==2:
                    return (2,5)

        pyimg1 = py_image1_t(3,7)
        
        # Check a method that returns two values by reference
        self.assertEqual(pyimg1.get_size(), (3,7))

        # Check a method that only returns one value by reference
        self.assertEqual(pyimg1.get_one_value(), 4)

        # Check if the Python class can also be passed back to C++
        self.assertEqual(module.get_image_one_value(pyimg1), 4)

        # Check if fixed_output_array() is correctly called from C++
        self.assertEqual(module.image_fixed_output_array(pyimg1), 14)
        pyimg1.fixed_output_array_mode = 1
        self.assertRaises(ValueError, lambda : module.image_fixed_output_array(pyimg1))
        pyimg1.fixed_output_array_mode = 2
        self.assertRaises(ValueError, lambda : module.image_fixed_output_array(pyimg1))

        class py_image2_t(module.image_t):
            def __init__(self, h, w):
                module.image_t.__init__(self, h, w)

            # Override a virtual method and invoke the inherited method
            def get_one_value(self):
                return module.image_t.get_one_value(self)+2
        
        pyimg2 = py_image2_t(4,8)

        # Check the derived get_one_value() method
        self.assertEqual(pyimg2.get_one_value(), 6)

        # Check if the Python class can also be passed back to C++
        self.assertEqual(module.get_image_one_value(pyimg2), 6)

        ####### Do the tests on a class instantiated in C++ ########

        cppimg = module.get_cpp_instance()

        # Check a method that returns two values by reference
        self.assertEqual(cppimg.get_size(), (12,13))

        # Check a method that only returns one value by reference
        self.assertEqual(cppimg.get_one_value(), 12)

        # Check if the C++ class can also be passed back to C++
        self.assertEqual(module.get_image_one_value(cppimg), 12)

        ######### Test no_virtual_members_t ########

        cls = module.no_virtual_members_t()
        self.assertEqual(cls.member(), (True, 17))

def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
