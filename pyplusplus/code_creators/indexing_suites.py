# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import types
import algorithm 
import code_creator
import declaration_based
from pygccxml import declarations

class indexing_suite1_t( declaration_based.declaration_based_t ):
    def __init__(self, container, parent=None ):        
        declaration_based.declaration_based_t.__init__( self, declaration=container, parent=parent )
            
    def _get_configuration( self ):
        return self.declaration.indexing_suite
    configuration = property( _get_configuration )

    def _get_container( self ):
        return self.declaration 
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
    

class indexing_suite2_t( declaration_based.declaration_based_t ):
    def __init__(self, container, parent=None ):        
        declaration_based.declaration_based_t.__init__( self, declaration=container, parent=parent )
        
    def _get_configuration( self ):
        return self.declaration.indexing_suite
    configuration = property( _get_configuration )
            
    def _create_impl( self ):
        container_suite = algorithm.create_identifier(self, "::boost::python::indexing::container_suite" )
        return "def( %s< %s >() )" % ( container_suite, self.decl_identifier )