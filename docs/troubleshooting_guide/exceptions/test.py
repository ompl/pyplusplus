import unittest
import my_exceptions

print dir( my_exceptions._zero_division_error_.__class__ )

class zero_division_error(my_exceptions._zero_division_error_, ZeroDivisionError ):
    
    def __init__( self, msg ):
        my_exceptions._zero_division_error_.__init__( self, msg )
        
my_exceptions.zero_division_error = zero_division_error

class tester_t( unittest.TestCase ):
    def __init__( self, *args ):
        unittest.TestCase.__init__( self, *args )
    
    def test( self ):
        print my_exceptions.devide( 1, 1 ) 
        self.failUnless( 1 == my_exceptions.devide( 1, 1 ) )
        try:
            my_exceptions.devide( 1, 0 )
        except zero_division_error, err:
            print err.__class__.__name__, str(err)
    
def create_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
