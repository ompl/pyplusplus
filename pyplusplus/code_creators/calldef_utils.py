# Copyright 2004 Roman Yakovenko
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import code_creator
from pygccxml import declarations
from pyplusplus import decl_wrappers
#virtual functions that returns const reference to something
#could not be overriden by Python. The reason is simple:
#in boost::python::override::operator(...) result of marshaling
#(Python 2 C++) is saved on stack, after functions returns the result
#will be reference to no where - access violetion.
#For example see temporal variable tester

use_enum_workaround = False

class argument_utils_t:
    
    PARAM_SEPARATOR = code_creator.code_creator_t.PARAM_SEPARATOR
    
    def __init__( self, declaration, identifier_creator, arguments=None ):
        self.__decl = declaration
        if None is arguments:
            arguments = self.__decl.arguments
        self.__args = arguments
        self.__id_creator = identifier_creator

    def __should_use_enum_wa( self, arg ):
        global use_enum_workaround
        if not declarations.is_enum( arg.type ):
            return False
        if use_enum_workaround:
            return True
        #enum belongs to the class we are working on
        if self.__decl.parent is declarations.enum_declaration( arg.type ).parent \
           and isinstance( self.__decl, declarations.constructor_t ):
            return True
        return False

    def keywords_args(self):
        boost_arg = self.__id_creator( '::boost::python::arg' )
        boost_obj = self.__id_creator( '::boost::python::object' )
        result = ['( ']
        for arg in self.__args:
            if 1 < len( result ):
                result.append( self.PARAM_SEPARATOR )
            result.append( boost_arg )
            result.append( '("%s")' % arg.name )
            if self.__decl.use_default_arguments and arg.default_value:
                if not declarations.is_pointer( arg.type ) or arg.default_value != '0':
                    arg_type_no_alias = declarations.remove_alias( arg.type )
                    if declarations.is_fundamental( arg_type_no_alias ) \
                       and declarations.is_integral( arg_type_no_alias ) \
                       and not arg.default_value.startswith( arg_type_no_alias.decl_string ):
                        result.append( '=(%s)(%s)' % ( arg_type_no_alias.decl_string, arg.default_value ) )
                    elif self.__should_use_enum_wa( arg ):
                        #Work around for bug/missing functionality in boost.python.
                        #registration order
                        result.append( '=(long)(%s)' % arg.default_value )
                    else:
                        result.append( '=%s' % arg.default_value )
                else:
                    result.append( '=%s()' % boost_obj )
        result.append( ' )' )
        return ''.join( result )

    def argument_name( self, index ):
        arg = self.__args[ index ]
        if arg.name:
            return arg.name
        else:
            return 'p%d' % index

    def args_declaration( self ):
        args = []
        for index, arg in enumerate( self.__args ):
            result = arg.type.decl_string + ' ' + self.argument_name(index)
            if arg.default_value:
                result += '=%s' % arg.default_value
            args.append( result )
        if len( args ) == 1:
            return args[ 0 ]
        return self.PARAM_SEPARATOR.join( args )
        
    def call_args( self ):
        params = []
        for index, arg in enumerate( self.__args ):
            params.append( decl_wrappers.python_traits.call_traits( arg.type )  %  self.argument_name( index ) )
        return ', '.join( params )



