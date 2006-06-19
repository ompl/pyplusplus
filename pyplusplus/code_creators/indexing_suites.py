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
    def __init__(self, suite_name, parent=None ):        
        code_creator.code_creator_t.__init__( self, parent=parent )
        self.__suite_name = suite_name
        
    def _get_configuration( self ):
        return self.parent.declaration.indexing_suite
    configuration = property( _get_configuration )

    def _get_container( self ):
        return self.parent.declaration 
    container = property( _get_container )

    def _create_suite_declaration( self ):
        suite_identifier = algorithm.create_identifier( self, self.__suite_name )
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

class vector_indexing_suite_t( indexing_suite_t ):
    """
    Creates boost.python code that needed to export a vector of some class
    """
    #class_< std::vector<X> >("XVec")
    #    .def(vector_indexing_suite<std::vector<X> >())
    #;

    def __init__(self, parent=None ):        
        indexing_suite_t.__init__( self, 'boost::python::vector_indexing_suite', parent=parent )

class map_indexing_suite_t( indexing_suite_t ):
    """
    Creates boost.python code that needed to export a vector of some class
    """
    #class_< std::vector<X> >("XVec")
    #    .def(vector_indexing_suite<std::vector<X> >())
    #;

    def __init__(self, parent=None ):        
        indexing_suite_t.__init__( self, 'boost::python::map_indexing_suite', parent=parent )

        