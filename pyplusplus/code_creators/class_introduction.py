# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import compound
import code_creator
import declaration_based
from pygccxml import declarations

ctypes_base_classes = {
    declarations.CLASS_TYPES.CLASS : 'Structure'
    , declarations.CLASS_TYPES.UNION : 'Union'
    , declarations.CLASS_TYPES.STRUCT : 'Structure'
}

class class_introduction_t(compound.compound_t, declaration_based.declaration_based_t):
    def __init__( self, class_ ):
        compound.compound_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, class_ )

    @property
    def ctypes_base_class( self ):
        global ctypes_base_classes
        return ctypes_base_classes[ self.declaration.class_type ]

    def _create_impl(self):
        result = []
        result.append( "class %(alias)s(ctypes.%(base)s):" 
                       % dict( alias=self.alias, base=self.ctypes_base_class ) )
        result.append( self.indent( '"""class %s"""' % self.decl_identifier ) )
        if self.creators:
            result.append( self.indent( '' ) )
        result.append( compound.compound_t.create_internal_code( self.creators ) )

        if isinstance( self.declaration.parent, declarations.namespace_t ) \
           and self.declaration.parent is not self.declaration.top_parent: #not a global namespace
            result.append("")
            result.append( '%(ns_full_name)s = %(name)s'
                           % dict( ns_full_name=self.complete_py_name, name=self.alias ))
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []


class class_declaration_introduction_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, class_declaration ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, class_declaration )

    def _create_impl(self):
        result = []
        result.append( "class %s(ctypes.Structure):" % self.alias )
        result.append( self.indent( '"""class declaration %s"""' % self.decl_identifier ) )
        result.append( self.indent( '_fields_  = []' ) )

        if isinstance( self.declaration.parent, declarations.namespace_t ) \
           and self.declaration.parent is not self.declaration.top_parent: #not a global namespace
            result.append( '%(ns_full_name)s = %(name)s'
                           % dict( ns_full_name=self.complete_py_name, name=self.alias ))
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []
