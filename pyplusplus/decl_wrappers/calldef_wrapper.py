# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import decl_wrapper
from pygccxml import declarations
##May be in future I will enable this functionality again, right now it seems
##that this is useless
##def is_finalizable(self):
    ##if not self.wrapper:
        ##return False
    ##return self.declaration.virtuality != declarations.VIRTUALITY_TYPES.PURE_VIRTUAL

class calldef_t(decl_wrapper.decl_wrapper_t):
    
    BOOST_PYTHON_MAX_ARITY = 10
    
    def __init__(self, *arguments, **keywords):
        decl_wrapper.decl_wrapper_t.__init__( self, *arguments, **keywords )

        self._call_policies = None
        self._use_keywords = True
        self._use_default_arguments = True
        self._create_with_signature = False
        self._overridable = None

    def get_call_policies(self):
        return self._call_policies
    def set_call_policies(self, call_policies):
        self._call_policies = call_policies
    call_policies = property( get_call_policies, set_call_policies )

    def _get_use_keywords(self):
        return self._use_keywords and bool( self.arguments )
    def _set_use_keywords(self, use_keywords):
        self._use_keywords = use_keywords
    use_keywords = property( _get_use_keywords, _set_use_keywords )

    def _get_create_with_signature(self):
        return self._create_with_signature or bool( self.overloads )
    def _set_create_with_signature(self, create_with_signature):
        self._create_with_signature = create_with_signature
    create_with_signature = property( _get_create_with_signature, _set_create_with_signature)

    def _get_use_default_arguments(self):
        return self._use_default_arguments
    def _set_use_default_arguments(self, use_default_arguments):
        self._use_default_arguments = use_default_arguments
    use_default_arguments = property( _get_use_default_arguments, _set_use_default_arguments )

    def has_wrapper( self ):
        if not isinstance( self, declarations.member_calldef_t ):
            return False
        elif self.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            return True
        elif self.access_type == declarations.ACCESS_TYPES.PROTECTED:
            return True
        else:
            return False

    def _finalize_impl( self, error_behavior ):
        if not isinstance( self, declarations.member_calldef_t ):
            pass
        elif self.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            raise RuntimeError( "In order to expose pure virtual function, you should allow to pyplusplus to create wrapper." )
        elif self.access_type == declarations.ACCESS_TYPES.PROTECTED:
            self.ignore = True
        else:
            pass

    def get_overridable( self ):
        """
        Virtual functions, that returns const reference, could not be overriden
        from Python. The reason is simple: in boost::python::override::operator(...)
        result of marshaling (Python 2 C++) is saved on stack, after function
        exit, the result will be reference to no where - access violetion.
        For example see temporal variable tester
        """
        if None is self._overridable:
            if isinstance( self, declarations.member_calldef_t ) \
               and self.virtuality != declarations.VIRTUALITY_TYPES.NOT_VIRTUAL \
               and declarations.is_reference( self.return_type ):
                self._overridable = False
            else:
                self._overridable = True
        return self._overridable

    def set_overridable( self, overridable ):
        self._overridable = overridable

    overridable = property( get_overridable, set_overridable
                            , doc = get_overridable.__doc__ )
    
    def _exportable_impl_derived( self ):
        return ''
    
    def _exportable_impl( self ):
        #TODO: functions that takes as argument pointer to pointer to smth, could not be exported
        #see http://www.boost.org/libs/python/doc/v2/faq.html#funcptr
        if len( self.arguments ) > calldef_t.BOOST_PYTHON_MAX_ARITY:
            msg = "Function '%s' has more than %d arguments ( %d ). "
            msg = msg + " You should adjust BOOST_PYTHON_MAX_ARITY."
            msg = msg + " For more information see: http://mail.python.org/pipermail/c++-sig/2002-June/001554.html"
            self.logger.info( msg % ( self.decl_string, calldef_t.BOOST_PYTHON_MAX_ARITY, len( self.arguments ) ) )

        all_types = [ arg.type for arg in self.arguments ]
        all_types.append( self.return_type )
        for some_type in all_types:
            units = declarations.decompose_type( some_type )
            ptr2functions = filter( lambda unit: isinstance( unit, declarations.calldef_type_t )
                                    , units )
            if ptr2functions:
                return "boost.python can not expose function, which takes as argument/returns pointer to function." \
                       + " See http://www.boost.org/libs/python/doc/v2/faq.html#funcptr for more information."
            #Function that take as agrument some instance of non public class
            #will not be exported. Same to the return variable
            if isinstance( units[-1], declarations.declarated_t ):
                dtype = units[-1]
                if isinstance( dtype.declaration.parent, declarations.class_t ):
                    if dtype.declaration not in dtype.declaration.parent.public_members:
                        return "pyplusplus can not expose fuction that takes as argument/returns instance of non public class. Generated code will not compile."
            no_ref = declarations.remove_reference( some_type )
            no_ptr = declarations.remove_pointer( no_ref )
            no_const = declarations.remove_const( no_ptr )
            if declarations.is_array( no_const ):
                return "pyplusplus can not expose fuction that takes as argument/returns C++ arrays. This will be changed in near future."                
        return self._exportable_impl_derived()

    def _readme_impl( self ):
        def suspicious_type( type_ ):
            if not declarations.is_reference( self.return_type ):
                return False
            type_no_ref = declarations.remove_reference( type_ )
            return not declarations.is_const( type_no_ref ) \
                   and declarations.is_fundamental( type_no_ref )
        msg = []
        if suspicious_type( self.return_type ) and None is self.call_policies:
            msg.append( 'WARNING: Function "%s" returns non-const reference to C++ fundamental type - value can not be modified from Python.' % str( self ) )
        for index, arg in enumerate( self.arguments ):
            if suspicious_type( arg.type ):
                tmpl = 'WARNING: Function "%s" takes as argument (name=%s, pos=%d ) ' \
                       + 'non-const reference to C++ fundamental type - ' \
                       + 'function could not be called from Python.'
                msg.append( tmpl % ( str( self ), arg.name, index ) )

        if False == self.overridable:
            msg.append( self.get_overridable.__doc__ )
        return msg

class member_function_t( declarations.member_function_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.member_function_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class constructor_t( declarations.constructor_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.constructor_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )
        self._body = ''

    def _get_body(self):
        return self._body
    def _set_body(self, body):
        self._body = body
    body = property( _get_body, _set_body )

    def _exportable_impl_derived( self ):
        if self.is_artificial:
            return 'pyplusplus does not exports compiler generated constructors'
        return ''


class destructor_t( declarations.destructor_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.destructor_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class operators_helper:

    inplace = [ '+=', '-=', '*=', '/=',  '%=', '>>=', '<<=', '&=', '^=', '|=' ]
    comparison = [ '==', '!=', '<', '>', '<=', '>=' ]
    non_member = [ '+', '-', '*', '/', '%', '&', '^', '|' ] #'>>', '<<', not implemented
    unary = [ '!', '~', '+', '-' ]

    all = inplace + comparison + non_member + unary

    def is_supported( oper ):
        if oper.symbol == '*' and len( oper.arguments ) == 0:
            #dereference does not make sense
            return False
        return oper.symbol in operators_helper.all
    is_supported = staticmethod( is_supported )

    def exportable( oper ):
        if isinstance( oper, declarations.member_operator_t ) and oper.symbol in ( '()', '[]' ):
            return ''
        if not operators_helper.is_supported( oper ):
            #see http://www.boost.org/libs/python/doc/v2/operators.html#introduction
            return 'operator %s is not supported. Please take a look on http://www.boost.org/libs/python/doc/v2/operators.html#introduction.'
        return ''
    exportable = staticmethod( exportable )

class member_operator_t( declarations.member_operator_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.member_operator_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

    def _get_alias( self):
        alias = super( member_operator_t, self )._get_alias()
        if alias == self.name:
            if self.symbol == '()':
                alias = '__call__'
            elif self.symbol == '[]':
                alias = '__getitem__'
            else:
                pass
        return alias
    alias = property( _get_alias, decl_wrapper.decl_wrapper_t._set_alias )

    def _exportable_impl_derived( self ):
        return operators_helper.exportable( self )


class casting_operator_t( declarations.casting_operator_t, calldef_t ):

    def prepare_special_cases():
        """
        Creates a map of special cases ( aliases ) for casting operator.
        """
        special_cases = {}
        const_t = declarations.const_t
        pointer_t = declarations.pointer_t
        for type_ in declarations.FUNDAMENTAL_TYPES.values():
            alias = None
            if declarations.is_same( type_, declarations.bool_t() ):
                alias = '__int__'
            elif declarations.is_integral( type_ ):
                if 'long' in type_.decl_string:
                    alias = '__long__'
                else:
                    alias = '__int__'
            elif declarations.is_floating_point( type_ ):
                alias = '__float__'
            else:
                continue #void
            if alias:
                special_cases[ type_ ] = alias
                special_cases[ const_t( type_ ) ] = alias
        special_cases[ pointer_t( const_t( declarations.char_t() ) ) ] = '__str__'
        std_string = '::std::basic_string<char,std::char_traits<char>,std::allocator<char> >'
        std_wstring1 = '::std::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t> >'
        std_wstring2 = '::std::basic_string<wchar_t, std::char_traits<wchar_t>, std::allocator<wchar_t> >'
        special_cases[ std_string ] = '__str__'
        special_cases[ std_wstring1 ] = '__str__'
        special_cases[ std_wstring2 ] = '__str__'
        special_cases[ '::std::string' ] = '__str__'
        special_cases[ '::std::wstring' ] = '__str__'

        #TODO: add
        #          std::complex<SomeType> some type should be converted to double
        return special_cases

    SPECIAL_CASES = prepare_special_cases()
    #casting_member_operator_t.prepare_special_cases()

    def __init__(self, *arguments, **keywords):
        declarations.casting_operator_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

    def _get_alias( self):
        if not self._alias or self.name == super( member_operator_t, self )._get_alias():
            return_type = declarations.remove_alias( self.return_type )
            decl_string = return_type.decl_string
            for type_, alias in self.SPECIAL_CASES.items():
                if isinstance( type_, declarations.type_t ):
                    if declarations.is_same( return_type, type_ ):
                        self._alias = alias
                        break
                else:
                    if decl_string == type_:
                        self._alias = alias
                        break
            else:
                self._alias = 'as_' + self._generate_valid_name(self.return_type.decl_string)
        return self._alias
    alias = property( _get_alias, decl_wrapper.decl_wrapper_t._set_alias )

class free_function_t( declarations.free_function_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.free_function_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class free_operator_t( declarations.free_operator_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.free_operator_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

    def _exportable_impl_derived( self ):
        return operators_helper.exportable( self )
