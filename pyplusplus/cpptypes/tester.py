import ctypes
import unittest
import name_mapping
mydll = ctypes.CPPDLL( './mydll/release/mydll.dll' )

#we should keep somewhere decorated-undecorated name mappings
#I don't feel like parsing source code is a good strategy
#    - there is no way to create mangled name for a function.  In this example, other way is used - binary file is parsed
#      and the functions are mapped to dll entry using "human readable" format.
#      GCCXML reports mangled and demangled names of the function, but it is not a cross platform( compile ) solution.
#      It looks like I will have to cause mspdb package to work ( from where ctypes loads dlls? ctypes.windll.msvcr90 ???

mydll.name_mapping = name_mapping.data

# what is the best way to treat overloaded constructors
class public( object ):
    def __init__(self, dll, name, restype=None, argtypes=None ):
        self.name = name
        self.func = getattr( dll, dll.name_mapping[name] )
        self.func.restype = restype
        self.func.argtypes = argtypes

    def __call__(self, *args, **keywd ):
        return self.func( *args,  **keywd )

class mem_fun_factory( object ):
    def __init__( self, dll, class_ ):
        self.dll = dll
        self.this_type = ctypes.POINTER( class_ )

    def __call__( self, name, **keywd ):
        if 'argtypes' not in keywd:
            keywd['argtypes'] = [ self.this_type ]
        else:
            keywd['argtypes'].insert( 0, self.this_type )
        return public( self.dll, name, **keywd )


class Number(ctypes.Structure):
    #http://www.phpcompiler.org/articles/virtualinheritance.html,
    _fields_ = [("vptr", ctypes.POINTER(ctypes.c_void_p)),
                ("m_value", ctypes.c_int)]

    _methods_ = {}

    def __init__(self, x=None):
        self.__this = ctypes.byref( self )
        #overloading example
        if None is x:
            self._methods_['default_constructor']( self.__this )
        elif isinstance( x, int ):
            self._methods_['from_int_constructor']( self.__this, x )
        elif isinstance( x, Number ):
            self._methods_['copy_constructor']( self.__this, ctypes.byref( x ) )
        else:
            raise RuntimeError( "Wrong argument" )

    def get_value( self, *args, **keywd ):
        return self._methods_['get_value']( self.__this, *args, **keywd )

    def set_value( self, *args, **keywd ):
        return self._methods_['set_value']( self.__this, *args, **keywd )

    def print_it( self, *args, **keywd ):
        return self._methods_['print_it']( self.__this, *args, **keywd )

    def assign( self, *args, **keywd ):
        return self._methods_['assign']( self.__this, *args, **keywd )

    def __del__(self):
        self._methods_['destructor']( self.__this )


mem_fun = mem_fun_factory( mydll, Number )
Number._methods_ = {
    #constructors
      'default_constructor' : mem_fun( 'number_t::number_t(void)' )
    , 'from_int_constructor' : mem_fun( 'number_t::number_t(int)', argtypes=[ctypes.c_int] )
    , 'copy_constructor' : mem_fun( 'number_t::number_t(number_t const &)', argtypes=[ctypes.POINTER(Number)] )
    #member functions
    , 'get_value' : mem_fun( 'int number_t::get_value(void)', restype=ctypes.c_int )
    , 'set_value' : mem_fun( 'void number_t::set_value(int)', argtypes=[ctypes.c_int])
    , 'print_it' : mem_fun( 'void number_t::print_it(void)' )
    #operator=
    , 'assign' : mem_fun( "number_t & number_t::operator=(number_t const &)"
                           , restype=ctypes.POINTER(Number)
                           , argtypes=[ctypes.POINTER(Number)] )
    #destructor
    , 'destructor' : mem_fun( 'number_t::~number_t(void)' )
}
del mem_fun


class tester_t( unittest.TestCase ):
    def test_constructors(self):
        obj1 = Number(32)
        self.failUnless( obj1.m_value == 32 )
        obj2 = Number()
        self.failUnless( obj2.m_value == 0 )
        obj3 = Number(obj1)
        self.failUnless( obj3.m_value == obj1.m_value == 32 )

    def test_get_value( self ):
        obj = Number(99)
        self.failUnless( 99 == obj.get_value() )

    def test_set_value( self ):
        obj = Number()
        obj.set_value( 13 )
        self.failUnless( 13 == obj.get_value() == obj.m_value )

    def test_assign( self ):
        obj1 = Number(1)
        obj2 = Number(2)
        x = obj1.assign( obj2 )
        #there are special cases, where ctypes could introduce "optimized" behaviour and not create new python object
        self.failUnless( x is obj1 )
        self.failUnless( obj1.m_value == obj2.m_value )

def main():
    obj = Number(42)
    print obj.m_value
    print hex(obj.vptr[0])
    obj.print_it()
    print '42 == ', obj.get_value()

if __name__ == "__main__":
    unittest.main()

#problems:
#consider generic algorithm for resolving overloaded functions call
#    * function name should be unique
#    *  write something very smart and bugy and let the smart people to improve it


"""
TODO:

* I think more testers and "demos",  before I write code generator:
  * a class instance passed\returned by value\reference\pointer\smart pointer
  * function overloading
  * how much code, we can put in the helper files. I mean class like "public". Or std::vector - there is no reason, to define\generate this class every time
  * how we are going to manage relationship between objects:
    class X{...};
    class Y{ X x; public: const X& get_x() const { return x;} };
    I think our solution should be very similar to Boost.Python call policies. It is definitely possible to go without it.
* template classes:
    in the following use case, the members of std:auto_ptr class are not exported
    class number_t{...};
    std::auto_ptr<number_t> do_smth();
    The user will have to change the code to add
        template class __declspec(dllexport) std::auto_ptr< number_t >;
    and recompile

"""
