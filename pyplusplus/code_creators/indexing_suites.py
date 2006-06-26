# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import types
import algorithm 
import code_creator
from pygccxml import declarations

class indexing_suite_t( code_creator.code_creator_t ):
    def __init__(self, parent=None ):        
        code_creator.code_creator_t.__init__( self, parent=parent )
            
    def _get_configuration( self ):
        return self.parent.declaration.indexing_suite
    configuration = property( _get_configuration )

    def _get_container( self ):
        return self.parent.declaration 
    container = property( _get_container )

    def guess_suite_name( self ):
        if self.container.name.startswith( 'vector' ):
            return 'boost::python::vector_indexing_suite'
        else:
            return 'boost::python::map_indexing_suite'

    def _create_suite_declaration( self ):
        suite_identifier = algorithm.create_identifier( self, self.guess_suite_name() )
        args = [ self.container.decl_string ]
        if self.configuration.derived_policies:
            if self.configuration.no_proxy:
                args.append( 'true' )
            else:
                args.append( 'false' )
            args.append( self.configuration.derived_policies )
        else:
            if self.configuration.no_proxy:
                args.append( 'true' )        
        return declarations.templates.join( suite_identifier, args )        

    def _create_impl(self):
        return "def( %s() )" %  self._create_suite_declaration()
    