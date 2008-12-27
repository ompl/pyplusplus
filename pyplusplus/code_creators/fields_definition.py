# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import code_creator
import declaration_based
from pygccxml import declarations

class fields_definition_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, class_ ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, class_ )

    def _create_impl(self):
        result = []
        result.append( '%(complete_py_name)s._fields_ = [ #class member variables definition list'
                       % dict( complete_py_name=self.complete_py_name ) )
        if self.declaration.has_vtable:
            result.append( self.indent( '("_vtable_", ctypes.POINTER(ctypes.c_void_p)),' ) )
        result.append( self.indent( "#TODO: don't hide public member variables" ) )
        result.append( self.indent( "#TODO: how _fields_ should be defined in a class hierarchy" ) )
        result.append( self.indent( "#TODO: fix 64bit issue with calculating vtable pointer size" ) )
        result.append( self.indent( '("__hidden__", ctypes.c_char * %d),'
                                      % ( self.declaration.byte_size - 4*int(self.declaration.has_vtable) ) ) )
        result.append( ']' )
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []
