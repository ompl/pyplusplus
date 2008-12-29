# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import compound
import code_creator
import ctypes_formatter
import declaration_based
from pygccxml import declarations

#TODO - unable to call C function, if dll was loaded as CPPDLL

def join_arguments( args ):
    args_str = ''
    arg_separator = ', '
    if 1 == len( args ):
        args_str = ' ' + args[0] + ' '
    else:
        args_str = ' ' + arg_separator.join( args ) + ' '
    return '[%s]' % args_str

class function_definition_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, free_fun ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, free_fun )

    @property
    def ftype( self ):
        return self.declaration.function_type()

    def _create_impl(self):
        result = []
        result.append( '%(alias)s = getattr( %(library_var_name)s, %(library_var_name)s.undecorated_names["%(undecorated_decl_name)s"] )'
                       % dict( alias=self.declaration.alias
                               , library_var_name=self.top_parent.library_var_name
                               , undecorated_decl_name=self.undecorated_decl_name) )

        if not declarations.is_void( self.ftype.return_type ):
            result.append( '%(alias)s.restype = %(restype)s'
                           % dict( alias=self.declaration.alias
                                   , restype=ctypes_formatter.as_ctype( self.ftype.return_type ) ) )

        if self.ftype.arguments_types:
            tmp = []
            tmp.append( '%(alias)s.argtypes = ' % dict( alias=self.declaration.alias ) )
            args = map( ctypes_formatter.as_ctype, self.ftype.arguments_types )
            tmp.append( join_arguments( args ) )
            result.append( ''.join( tmp ) )

        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []

def mem_fun_factory_var_name( cc ):
    import methods_definition
    while not isinstance( cc, methods_definition.methods_definition_t ):
        cc = cc.parent
    return cc.mem_fun_factory_var_name


class METHOD_MODE:
    STAND_ALONE = "stand alone"
    MULTI_METHOD = "multi method"
    all = [ STAND_ALONE, MULTI_METHOD ]

class init_definition_t( code_creator.code_creator_t, declaration_based.declaration_based_t ):
    def __init__( self, constructor ):
        code_creator.code_creator_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, constructor )
        self.__mode = METHOD_MODE.STAND_ALONE

    def __get_mode(self):
        return self.__mode
    def __set_mode(self, new_mode):
        assert new_mode in METHOD_MODE.all
        self.__mode = new_mode
    method_mode = property( __get_mode, __set_mode )

    def _create_impl(self):
        tmpl = ''
        substitue_dict = dict( mfcreator=mem_fun_factory_var_name( self ) )
        if self.declaration.is_trivial_constructor:
            tmpl = '%(mfcreator)s.default_constructor()'
        elif self.declaration.is_copy_constructor:
            tmpl = '%(mfcreator)s.copy_constructor()'
        else:
            if self.method_mode == METHOD_MODE.STAND_ALONE:
                tmpl = '%(mfcreator)s( "%(undecorated_decl_name)s", argtypes=%(args)s )'
            else:
                tmpl = '"%(undecorated_decl_name)s", argtypes=%(args)s'
            args = map( ctypes_formatter.as_ctype, self.declaration.function_type().arguments_types )
            substitue_dict['args'] = join_arguments( args )
            substitue_dict['undecorated_decl_name'] = self.undecorated_decl_name
        if self.method_mode == METHOD_MODE.STAND_ALONE:
            tmp = '"__init__" : ' + tmpl
        return tmpl % substitue_dict

    def _get_system_headers_impl( self ):
        return []

class multi_init_definition_t( compound.compound_t ):
    def __init__( self ):
        compound.compound_t.__init__( self )

    def _create_impl(self):
        result = []
        result.append( '"__init__" : %s.multi_method()' % mem_fun_factory_var_name(self) )
        for creator in self.creators:
            code = ''
            if isinstance( creator, init_definition_t ):
                creator.method_mode = METHOD_MODE.MULTI_METHOD
                code = '.register( %s )' % creator.create()
            else:
                code = creator.create()
            result.append( self.indent( code, 4 ) )
        result.append( self.indent( '.finalize(),', 4 ) )
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []


class del_definition_t( code_creator.code_creator_t, declaration_based.declaration_based_t ):
    def __init__( self, destructor ):
        code_creator.code_creator_t.__init__( self )
        declaration_based.declaration_based_t.__init__( self, destructor )

    def _create_impl(self):
        return '"__del__" : %(mfcreator)s.destructor(is_virtual=%(virtual)s)' \
               % dict( mfcreator=mem_fun_factory_var_name( self )
                       , virtual=self.iif( self.declaration.virtuality==declarations.VIRTUALITY_TYPES.NOT_VIRTUAL
                                           , 'False'
                                           , 'True' ) )

    def _get_system_headers_impl( self ):
        return []






