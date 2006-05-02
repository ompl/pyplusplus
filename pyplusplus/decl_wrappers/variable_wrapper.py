# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations 
import decl_wrapper

class variable_t(decl_wrapper.decl_wrapper_t, declarations.variable_t):
    def __init__(self, *arguments, **keywords):
        declarations.variable_t.__init__(self, *arguments, **keywords )
        decl_wrapper.decl_wrapper_t.__init__( self )
        
    def _exportable_impl( self ):
        if not isinstance( self.parent, declarations.class_t ):
            return ''
        if self.bits == 0 and self.name == "":
            return "pyplusplus can not expose alignement bit."
        type_ = declarations.remove_const( self.type )
        if declarations.is_pointer( type_ ):
            if self.type_qualifiers.has_static:
                return "pyplusplus, right now, can not expose static pointer member variables. This could be changed in future."
            if declarations.is_fundamental( type_.base ):
                return "pyplusplus, right now, can not expose pointer to fundamental member variables. This could be changed in future."
        return ''
    