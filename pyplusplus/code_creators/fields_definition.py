# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import code_creator
import ctypes_formatter
import declaration_based
from pygccxml import declarations

#TODO: don't hide public member variables
#TODO: how _fields_ should be defined in a class hierarchy
#TODO: fix 64bit issue with calculating vtable pointer size


class fields_definition_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, class_ ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, class_ )

    def _create_impl(self):
        result = []
        result.append( '%(complete_py_name)s._fields_ = [ #class %(decl_identifier)s'
                       % dict( complete_py_name=self.complete_py_name
                               , decl_identifier=self.decl_identifier) )
        if self.declaration.has_vtable:
            result.append( self.indent( '("_vtable_", ctypes.POINTER(ctypes.c_void_p)),' ) )

        vars = self.declaration.vars( allow_empty=True, recursive=False )
        if not vars:
            result.append( self.indent( '("__empty__", ctypes.c_char * 4)' ) )
        else:
            vars = vars.to_list()
            vars.sort( key=lambda d: d.location.line )
            for v in vars:
                result.append( self.indent( '("%(name)s", %(type)s),'
                               % dict( name=v.name
                                       ,type=ctypes_formatter.as_ctype( v.type ) ) ) )
        result.append( ']' )
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []
