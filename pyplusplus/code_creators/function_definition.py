# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import code_creator
import ctypes_formatter
import declaration_based
from pygccxml import declarations

"""
BSCGetBaseArray = _libraries['msbsc70.dll'].BSCGetBaseArray
BSCGetBaseArray.restype = BOOL
BSCGetBaseArray.argtypes = [POINTER(Bsc), IINST, POINTER(POINTER(IINST)), POINTER(ULONG)]

"""

class c_function_definition_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, free_fun ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, free_fun )

    @property
    def ftype( self ):
        return self.declaration.function_type()

    def __join_args( self, args ):
        args_str = ''
        arg_separator = ', '
        if 1 == len( args ):
            args_str = ' ' + args[0] + ' '
        else:
            args_str = ' ' + arg_separator.join( args ) + ' '
        return '[%s]' % args_str


    def _create_impl(self):
        result = []
        result.append( '#%s' % self.undecorated_decl_name )
        result.append( '%(alias)s = %(library_var_name)s.%(alias)s'
                       % dict( alias=self.declaration.alias
                               , library_var_name=self.top_parent.library_var_name ) )

        if not declarations.is_void( self.ftype.return_type ):
            result.append( '%(alias)s.restype = %(restype)s'
                           % dict( alias=self.declaration.alias
                                   , restype=ctypes_formatter.as_ctype( self.ftype.return_type ) ) )

        if self.ftype.arguments_types:
            tmp = []
            tmp.append( '%(alias)s.argtypes = ' % dict( alias=self.declaration.alias ) )
            args = map( ctypes_formatter.as_ctype, self.ftype.arguments_types )
            tmp.append( self.__join_args( args ) )
            result.append( ''.join( tmp ) )

        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []
