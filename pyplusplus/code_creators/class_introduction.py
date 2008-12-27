# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import compound
import declaration_based
from pygccxml import declarations

class class_introduction_t(compound.compound_t, declaration_based.declaration_based_t):
    def __init__( self, class_ ):
        compound.compound_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, class_ )

    def _create_impl(self):
        result = []
        result.append( "class %s(ctypes.Structure):" % self.alias )
        result.append( self.indent( '"""class %s"""' % self.decl_identifier ) )
        result.append( self.indent( '#_fields_  = [] <-- class member variables definition list' ) )
        result.append( self.indent( '#_methods_ = {} <-- class non-virtual member functions definition list' ) )
        if self.creators:
            result.append( self.indent( '' ) )
        result.append( compound.compound_t.create_internal_code( self.creators ) )

        if isinstance( self.declaration.parent, declarations.namespace_t ) \
           and self.declaration.parent is not self.declaration.top_parent: #not a global namespace
            result.append( '%(ns_full_name)s = %(name)s'
                           % dict( ns_full_name=self.complete_py_name, name=self.alias ))
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []
