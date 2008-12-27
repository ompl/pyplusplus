# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import code_creator
import declaration_based
from pygccxml import declarations

class mem_fun_introduction_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, mem_fun ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, mem_fun )

    def _create_impl(self):
        tmpl = ['def %(alias)s( self, *args ):']
        tmpl.append( self.indent('"""%(name)s"""') )
        tmpl.append( self.indent("return self._methods_['%(alias)s']( ctypes.byref( self ), *args )") )
        return os.linesep.join( tmpl ) \
               % dict( alias=self.declaration.alias, name=self.undecorated_decl_name )

    def _get_system_headers_impl( self ):
        return []

class vmem_fun_introduction_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, mem_fun ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, mem_fun )

    def _create_impl(self):
        tmpl = ['def %(alias)s( self, *args ):']
        tmpl.append( self.indent('"""%(name)s"""') )
        tmpl.append( self.indent("return self._vtable_['%(ordinal)d'].%(alias)s( ctypes.byref( self ), *args )") )
        return os.linesep.join( tmpl ) \
               % dict( alias=self.declaration.alias
                       , name=self.undecorated_decl_name
                       , ordinal=0)

    def _get_system_headers_impl( self ):
        return []
