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

mydll.undecorated_names = name_mapping.data

# what is the best way to treat overloaded constructors
class mem_fun_callable( object ):
    def __init__(self, dll, name, restype=None, argtypes=None ):
        self.name = name
        self.func = getattr( dll, dll.undecorated_names[name] )
        self.func.restype = restype
        self.func.argtypes = argtypes

    def __call__(self, *args, **keywd ):
        return self.func( *args,  **keywd )

class mem_fun_factory( object ):
    def __init__( self, dll, wrapper, class_name, namespace='' ):
        self.dll = dll
        self.namespace = namespace
        self.class_name = class_name
        self.this_type = ctypes.POINTER( wrapper )

    def __call__( self, name, **keywd ):
        if 'argtypes' not in keywd:
            keywd['argtypes'] = [ self.this_type ]
        else:
            keywd['argtypes'].insert( 0, self.this_type )
        return mem_fun_callable( self.dll, name, **keywd )

    def __get_ns_name(self):
        if self.namespace:
            return self.namespace + '::'
        else:
            return ''

    def default_constructor( self ):
        return self( '%(ns)s%(class_name)s::%(class_name)s(void)'
                        % dict( ns=self.__get_ns_name()
                                , class_name=self.class_name ) )

    def constructor( self, argtypes_str, **keywd ):
        return self( '%(ns)s%(class_name)s::%(class_name)s(%(args)s)'
                        % dict( ns=self.__get_ns_name()
                                , class_name=self.class_name
                                , args=argtypes_str )
                     , **keywd )

    def copy_constructor( self ):
        return self( '%(ns)s%(class_name)s::%(class_name)s(%(class_name)s const &)'
                        % dict( ns=self.__get_ns_name()
                                , class_name=self.class_name )
                     , argtypes=[self.this_type] )

    def destructor( self ):
        return self( '%(ns)s%(class_name)s::~%(class_name)s(void)'
                        % dict( ns=self.__get_ns_name()
                                , class_name=self.class_name ) )

    def operator_assign( self ):
        return self( '%(ns)s%(class_name)s & %(class_name)s::operator=(%(class_name)s const &)'
                        % dict( ns=self.__get_ns_name()
                                , class_name=self.class_name )
                     , restype=self.this_type
                     , argtypes=[self.this_type] )

    def method( self, name, restype_str=None, argtypes_str=None, **keywd ):
        if None is restype_str:
            restype_str = 'void'
        if None is argtypes_str:
            argtypes_str = 'void'

        return self( '%(return_)s %(ns)s%(class_name)s::%(method_name)s(%(args)s)'
                        % dict( return_=restype_str
                                , ns=self.__get_ns_name()
                                , class_name=self.class_name
                                , method_name=name
                                , args=argtypes_str )
                     , **keywd )

#names should be preserved
class number_t(ctypes.Structure):
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
        elif isinstance( x, number_t ):
            self._methods_['copy_constructor']( self.__this, ctypes.byref( x ) )
        else:
            raise RuntimeError( "Wrong argument" )

    def get_value( self, *args, **keywd ):
        return self._methods_['get_value']( self.__this, *args, **keywd )

    def set_value( self, *args, **keywd ):
        return self._methods_['set_value']( self.__this, *args, **keywd )

    def clone( self, *args, **keywd ):
        return self._methods_['clone']( self.__this, *args, **keywd )

    def print_it( self, *args, **keywd ):
        return self._methods_['print_it']( self.__this, *args, **keywd )

    def operator_assign( self, *args, **keywd ):
        return self._methods_['operator_assign']( self.__this, *args, **keywd )

    def __del__(self):
        self._methods_['destructor']( self.__this )

class auto_ptr(ctypes.Structure):
    #http://www.phpcompiler.org/articles/virtualinheritance.html,
    _fields_ = [("pointer", ctypes.POINTER(ctypes.c_void_p))]

    _methods_ = {}

    def __init__(self, x=None):
        self.__this = ctypes.byref( self )
        #overloading example
        if None is x:
            self._methods_['default_constructor']( self.__this )
        elif isinstance( x, int ):
            self._methods_['from_pointer_constructor']( self.__this, x )
        elif isinstance( x, auto_ptr ):
            self._methods_['copy_constructor']( self.__this, ctypes.byref( x ) )
        else:
            raise RuntimeError( "Wrong argument" )

    def get( self, *args, **keywd ):
        return self._methods_['get']( self.__this, *args, **keywd )

    def release( self, *args, **keywd ):
        return self._methods_['release']( self.__this, *args, **keywd )

    def assign( self, *args, **keywd ):
        return self._methods_['assign']( self.__this, *args, **keywd )

    def __del__(self):
        self._methods_['destructor']( self.__this )

#important note: the methods of the class could only be generated after all class were defined.
#For example: class X{ std::auto_ptr<X> clone(); };

mfcreator = mem_fun_factory( mydll, number_t, 'number_t' )
number_t._methods_ = {
      'default_constructor' : mfcreator.default_constructor()
    , 'copy_constructor' : mfcreator.copy_constructor()
    , 'operator_assign' : mfcreator.operator_assign()
    , 'destructor' : mfcreator.destructor()
    , 'from_int_constructor' : mfcreator.constructor( argtypes_str='int', argtypes=[ctypes.c_int] )
    , 'get_value' : mfcreator.method( 'get_value', restype_str='int', restype=ctypes.c_int )
    , 'set_value' : mfcreator.method( 'set_value', argtypes_str='int', argtypes=[ctypes.c_int])
    , 'print_it' : mfcreator.method( 'print_it' )
    , 'clone' : mfcreator.method( 'clone', restype_str="number_t", restype=number_t )
    , 'clone_ptr' : mfcreator.method( 'clone_ptr', restype_str="std::auto_ptr<number_t>", restype=auto_ptr )
}
del mfcreator

#~ mfcreator = mem_fun_factory( mydll, auto_ptr )
#~ auto_ptr._methods_ = {
      #~ 'default_constructor' : mfcreator.default_constructor()
    #~ , 'operator_assign' : mfcreator.operator_assign()
    #~ , 'destructor' : mfcreator.destructor()

  #~ u'std::auto_ptr<number_t>::auto_ptr<number_t>(number_t *)': u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@PAVnumber_t@@@Z',
 #~ u'std::auto_ptr<number_t>::auto_ptr<number_t>(std::auto_ptr<number_t> &)': u'??0?$auto_ptr@Vnumber_t@@@std@@QAE@AAV01@@Z',



 #~ u'number_t * std::auto_ptr<number_t>::get(void)': u'?get@?$auto_ptr@Vnumber_t@@@std@@QBEPAVnumber_t@@XZ',
 #~ u'number_t * std::auto_ptr<number_t>::release(void)': u'?release@?$auto_ptr@Vnumber_t@@@std@@QAEPAVnumber_t@@XZ',


#~ }
#~ del mfcreator

class tester_t( unittest.TestCase ):
    def test_constructors(self):
        obj1 = number_t(32)
        self.failUnless( obj1.m_value == 32 )
        obj2 = number_t()
        self.failUnless( obj2.m_value == 0 )
        obj3 = number_t(obj1)
        self.failUnless( obj3.m_value == obj1.m_value == 32 )

    def test_get_value( self ):
        obj = number_t(99)
        self.failUnless( 99 == obj.get_value() )

    def test_set_value( self ):
        obj = number_t()
        obj.set_value( 13 )
        self.failUnless( 13 == obj.get_value() == obj.m_value )

    def test_operator_assign( self ):
        obj1 = number_t(1)
        obj2 = number_t(2)
        x = obj1.operator_assign( obj2 )
        #there are special cases, where ctypes could introduce "optimized" behaviour and not create new python object
        self.failUnless( x is obj1 )
        self.failUnless( obj1.m_value == obj2.m_value )

    def test_clone( self ):
        obj1 = number_t(1)
        obj2 = obj1.clone()
        self.fail( obj1.get_value() == obj2.get_value() )

def main():
    obj = number_t(42)
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
  * how should we deal with namespaces?
  * member function signatures should be generate outside of the classes.

"""
