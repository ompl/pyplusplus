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
    
class vector_indexing_suite_t( indexing_suite_t ):
    """
    Creates boost.python code that needed to export a vector of some class
    """
    #class_< std::vector<X> >("XVec")
    #    .def(vector_indexing_suite<std::vector<X> >())
    #;

    def __init__(self, parent=None ):        
        indexing_suite_t.__init__( self, parent=parent )

    def _create_indexing_suite_declaration( self ):
        vector_indexing_suite = algorithm.create_identifier( self, 'boost::python::vector_indexing_suite' )
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
        return declarations.templates.join( vector_indexing_suite, args )        

    def _create_impl(self):
        return "def( %s() )" %  self._create_indexing_suite_declaration()

    