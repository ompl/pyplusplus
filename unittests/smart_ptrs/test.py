import unittest
import custom_sptr

class py_derived_t( custom_sptr.base_i ):
    def __init__( self ):
        custom_sptr.base_i.__init__( self )

    def get_value( self ):
        return 28

class py_double_derived_t( custom_sptr.derived_t ):
    def __init__( self ):
        custom_sptr.derived_t.__init__( self )

    def get_value( self ):
        return 31

class tester_t( unittest.TestCase ):
    def __init__( self, *args ):
        unittest.TestCase.__init__( self, *args )

    def __test_ref( self, inst ):
        try:
            custom_sptr.ref_get_value( inst )
            self.fail( 'ArgumentError was not raised.' )
        except Exception, error:
            self.failUnless( error.__class__.__name__ == 'ArgumentError' )

    def __test_val( self, inst, val ):
        self.assertEqual( custom_sptr.val_get_value( inst ), val )

    def __test_const_ref( self, inst, val ):
        self.assertEqual( custom_sptr.const_ref_get_value( inst ), val )

    def __test_impl( self, inst, val ):
        self.__test_ref( inst )
        self.__test_val( inst, val )
        self.__test_const_ref( inst, val )

    def test_derived( self ):
        self.__test_impl( custom_sptr.derived_t(), 11 )

    def test_py_derived( self ):
        self.__test_impl( py_derived_t(), 28 )

    def test_py_double_derived_t( self ):
        self.__test_impl( py_double_derived_t(), 31 )


def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
