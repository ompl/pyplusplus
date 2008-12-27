# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import compound
import declaration_based

class namespace_as_pyclass_t(compound.compound_t, declaration_based.declaration_based_t):
    def __init__( self, ns ):
        compound.compound_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, ns )

    def _create_impl(self):
        result = []
        result.append( "class %s:" % self.alias )
        result.append( self.indent( '"""namespace %s"""' % self.decl_identifier ) )
        if self.creators:
            result.append( self.indent( "" ) )
        result.append( compound.compound_t.create_internal_code( self.creators ) )
        return os.linesep.join( result )

    def _get_system_headers_impl( self ):
        return []
