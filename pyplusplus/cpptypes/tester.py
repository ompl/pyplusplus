import ctypes
import unittest
import decorators

mydll = ctypes.CPPDLL( './mydll/release/mydll.dll' )

#we should keep somewhere decorated-undecorated name mappings
#I don't feel like parsing source code is a good strategy
#    - there is no way to create mangled name for a function.  In this example, other way is used - binary file is parsed
#      and the functions are mapped to dll entry using "human readable" format.
#      GCCXML reports mangled and demangled names of the function, but it is not a cross platform( compile ) solution.
#      It looks like I will have to cause mspdb package to work ( from where ctypes loads dlls? ctypes.windll.msvcr90 ???


tmp = [ ( "number_t::number_t(class number_t const &)", "??0number_t@@QAE@ABV0@@Z" )
        , ( "number_t::number_t(int)", "??0number_t@@QAE@H@Z" )
        , ( "number_t::number_t(void)", "??0number_t@@QAE@XZ" )
        , ( "number_t::~number_t(void)", "??1number_t@@UAE@XZ" )
        , ( "class number_t & number_t::operator=(class number_t const &)", "??4number_t@@QAEAAV0@ABV0@@Z" )
        , ( "const number_t::'vftable'", "??_7number_t@@6B@" )
        , ( "int number_t::get_value(void)", "?get_value@number_t@@QBEHXZ" )
        , ( "void number_t::print_it(void)", "?print_it@number_t@@QBEXXZ" )
        , ( "void number_t::set_value(int)", "?set_value@number_t@@QAEXH@Z" ) ]

mydll.name_mapping = {}
for n1, n2 in tmp:
    mydll.name_mapping[n1] = n2
    mydll.name_mapping[n2] = n1

# what is the best way to treat overloaded constructors
class public( object ):
    def __init__(self, dll, this, name, restype=None, argtypes=None ):
        self.this = this #reference to class instance
        self.name = name
        self.func = getattr( dll, dll.name_mapping[name] )
        self.func.restype = restype
        this_call_arg_types = [ ctypes.POINTER( this._obj.__class__ ) ]
        if argtypes:
            this_call_arg_types.extend( argtypes )
        self.func.argtypes = this_call_arg_types

    def __call__(self, *args, **keywd ):
        return self.func( self.this, *args,  **keywd )

class mem_fun_factory( object ):
    def __init__( self, dll, this ):
        self.dll = dll
        self.this = this

    def __call__( self, *args, **keywd ):
        return public( self.dll, self.this, *args, **keywd )

class Number(ctypes.Structure):
    #http://www.phpcompiler.org/articles/virtualinheritance.html,
    _fields_ = [("vptr", ctypes.POINTER(ctypes.c_void_p)),
                ("m_value", ctypes.c_int)]

    def __init__(self, x=None):
        mem_fun = mem_fun_factory( mydll, ctypes.byref( self ) )
        self.get_value = mem_fun( 'int number_t::get_value(void)', restype=ctypes.c_int )
        self.set_value = mem_fun( 'void number_t::set_value(int)', argtypes=[ctypes.c_int])
        self.print_it = mem_fun( 'void number_t::print_it(void)' )
        self.assign = mem_fun( "class number_t & number_t::operator=(class number_t const &)"
                               , restype=ctypes.POINTER(Number)
                               , argtypes=[ctypes.POINTER(Number)] )
        #overloading example
        if None is x:
            mem_fun( 'number_t::number_t(void)' )()
        elif isinstance( x, int ):
            mem_fun( 'number_t::number_t(int)', argtypes=[ctypes.c_int] )( x )
        elif isinstance( x, Number ):
            mem_fun( 'number_t::number_t(class number_t const &)', argtypes=[ctypes.POINTER(Number)] )( ctypes.byref( x ) )
        else:
            raise RuntimeError( "Wrong argument" )

    def __del__(self):
        public( mydll, ctypes.byref(self), "number_t::~number_t(void)" )()

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

"""
