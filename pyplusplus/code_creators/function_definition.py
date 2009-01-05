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

CCT = declarations.CALLING_CONVENTION_TYPES

function_prototype_mapping = {
    CCT.UNKNOWN : 'CFUNCTYPE'
    , CCT.CDECL : 'CFUNCTYPE'
    , CCT.STDCALL : 'WINFUNCTYPE'
    , CCT.THISCALL : 'CPPMETHODTYPE'
    , CCT.FASTCALL : '<<<fastcall unsupported>>>'
    , CCT.SYSTEM_DEFAULT : 'CFUNCTYPE'
}

assert len( function_prototype_mapping ) == len( CCT.all )

class METHOD_MODE:
    STAND_ALONE = "stand alone"
    MULTI_METHOD = "multi method"
    all = [ STAND_ALONE, MULTI_METHOD ]


def get_mem_fun_factory_var_name( cc ):
    import methods_definition
    while not isinstance( cc, methods_definition.methods_definition_t ):
        cc = cc.parent
    return cc.mem_fun_factory_var_name

class callable_definition_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, callable ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, callable )
        self.__mode = METHOD_MODE.STAND_ALONE

    def __get_mode(self):
        return self.__mode
    def __set_mode(self, new_mode):
        assert new_mode in METHOD_MODE.all
        self.__mode = new_mode
    method_mode = property( __get_mode, __set_mode )

    @property
    def ftype( self ):
        return self.declaration.function_type()

    def join_arguments( self, args, group_in_list=True ):
        args_str = ''
        arg_separator = ', '
        if 1 == len( args ):
            args_str = ' ' + args[0] + ' '
        else:
            args_str = ' ' + arg_separator.join( args ) + ' '
        if group_in_list:
            return '[%s]' % args_str
        else:
            return args_str

    @property
    def mem_fun_factory_var_name( self ):
        return get_mem_fun_factory_var_name( self )

    def restype_code(self):
        if not declarations.is_void( self.ftype.return_type ):
            return ctypes_formatter.as_ctype( self.ftype.return_type )
        else:
            return ''

    def argtypes_code(self, group_in_list=True):
        if not self.ftype.arguments_types:
            return ''
        args = map( ctypes_formatter.as_ctype, self.ftype.arguments_types )
        return self.join_arguments( args, group_in_list )

    def _get_system_headers_impl( self ):
        return []


class function_definition_t(callable_definition_t):
    def __init__( self, free_fun ):
        callable_definition_t.__init__( self, free_fun )

    def _create_impl(self):
        global function_prototype_mapping
        result = []
        result.append( '%(alias)s_type = ctypes.%(prototype)s( %(restype)s%(argtypes)s )' )
        result.append( '%(alias)s = %(alias)s_type( ( %(library_var_name)s.undecorated_names["%(undecorated_decl_name)s"], %(library_var_name)s ) )' )

        restype = self.restype_code()
        argtypes = self.argtypes_code( group_in_list=False )

        return os.linesep.join( result ) \
               % dict( alias=self.declaration.alias
                       , prototype=function_prototype_mapping[ self.declaration.calling_convention ]
                       , restype=self.iif( restype, restype, 'None' )
                       , argtypes=self.iif( argtypes, ',' + argtypes, '' )
                       , library_var_name=self.top_parent.library_var_name
                       , undecorated_decl_name=self.undecorated_decl_name )

        #~ result.append( '%(alias)s = getattr( %(library_var_name)s, %(library_var_name)s.undecorated_names["%(undecorated_decl_name)s"] )'
                       #~ % dict( alias=self.declaration.alias
                               #~ , library_var_name=self.top_parent.library_var_name
                               #~ , undecorated_decl_name=self.undecorated_decl_name) )
        #~ restype = self.restype_code()
        #~ if restype:
            #~ result.append( '%(alias)s.restype = %(restype)s'
                           #~ % dict( alias=self.declaration.alias, restype=restype ) )

        #~ argtypes = self.argtypes_code()
        #~ if argtypes:
            #~ result.append( '%(alias)s.argtypes = %(argtypes)s'
                           #~ % dict( alias=self.declaration.alias, argtypes=argtypes ) )

        return os.linesep.join( result )

class init_definition_t( callable_definition_t ):
    def __init__( self, constructor ):
        callable_definition_t.__init__( self, constructor )

    def _get_alias_impl( self ):
        return "__init__"

    def _create_impl(self):
        tmpl = ''
        substitue_dict = dict( mfcreator=self.mem_fun_factory_var_name )
        if self.declaration.is_trivial_constructor:
            tmpl = '%(mfcreator)s.default_constructor()'
        elif self.declaration.is_copy_constructor:
            tmpl = '%(mfcreator)s.copy_constructor()'
        else:
            tmpl = '"%(undecorated_decl_name)s", argtypes=%(args)s'
            if self.method_mode == METHOD_MODE.STAND_ALONE:
                tmpl = '%(mfcreator)s( ' + tmpl + ' )'
            substitue_dict['args'] = self.argtypes_code()
            substitue_dict['undecorated_decl_name'] = self.undecorated_decl_name
        if self.method_mode == METHOD_MODE.STAND_ALONE:
            tmpl = '"%s" : %s,' % ( self.alias, tmpl )
        return tmpl % substitue_dict

#TODO: aliases for a mem fun and const mem fun with the same name should be different

class mem_fun_definition_t( callable_definition_t ):
    def __init__( self, constructor ):
        callable_definition_t.__init__( self, constructor )

    def _create_impl(self):
        result = []

        result.append( '"%s"' % self.undecorated_decl_name )

        restype = self.restype_code()
        if self.method_mode == METHOD_MODE.STAND_ALONE and restype:
            result.append( 'restype=%s' % restype )
        argtypes = self.argtypes_code()
        if argtypes:
            result.append( 'argtypes=%s' % argtypes )
        construction_code = ', '.join( result )
        if self.method_mode == METHOD_MODE.MULTI_METHOD:
            return construction_code
        else:
            return '"%(alias)s" : %(mfcreator)s( %(construction_code)s ),' \
                   % dict( alias=self.declaration.alias
                           , mfcreator=self.mem_fun_factory_var_name
                           , construction_code=construction_code )

class multi_method_definition_t( compound.compound_t ):
    def __init__( self ):
        compound.compound_t.__init__( self )

    def get_first_callable( self ):
        return self.find_by_creator_class( callable_definition_t, unique=False )[0]

    @property
    def multi_method_alias(self):
        return self.get_first_callable().alias

    def _create_impl(self):
        #small hack, this class should not be created at all if there is only one callable
        if len( self.creators ) == 1:
            if isinstance( self.creators[0], callable_definition_t ):
                self.creators[0].method_mode = METHOD_MODE.STAND_ALONE
            return self.creators[0].create()

        result = []

        return_type = self.get_first_callable().ftype.return_type
        restype = ''
        if return_type:
            restype = self.iif( not declarations.is_void( return_type )
                                , ctypes_formatter.as_ctype( return_type )
                                , '' )

        result.append( '"%(alias)s" : %(mfcreator)s.multi_method(%(restype)s)'
                       % dict( alias=self.multi_method_alias
                               , mfcreator=get_mem_fun_factory_var_name(self)
                               , restype=restype ) )
        for creator in self.creators:
            code = ''
            if isinstance( creator, callable_definition_t ):
                creator.method_mode = METHOD_MODE.MULTI_METHOD
                code = '.register( %s )' % creator.create()
            else:
                code = creator.create()
            result.append( self.indent( code, 4 ) )
        result.append( self.indent( '.finalize(),', 4 ) )
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []


class del_definition_t( callable_definition_t ):
    def __init__( self, destructor ):
        callable_definition_t.__init__( self, destructor )

    def _create_impl(self):
        return '"__del__" : %(mfcreator)s.destructor(is_virtual=%(virtual)s),' \
               % dict( mfcreator=self.mem_fun_factory_var_name
                       , virtual=self.iif( self.declaration.virtuality==declarations.VIRTUALITY_TYPES.NOT_VIRTUAL
                                           , 'False'
                                           , 'True' ) )
