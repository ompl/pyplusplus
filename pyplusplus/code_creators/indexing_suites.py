# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import types
import scoped
import custom
import calldef
import algorithm 
import smart_pointers
import declaration_based
import array_1_registrator
from pygccxml import declarations

class indexing_suite_t( scoped.scoped_t ):
    def __init__(self, class_inst, suite_configuration, parent=None ):        
        scoped.scoped_t.__init__( self
                                  , parent=parent
                                  , declaration=class_inst )
        self._suite_configuration = suite_configuration
        
    def _get_suite_configuration( self ):
        return self._suite_configuration
    suite_configuration = property( _get_suite_configuration )

class vector_indexing_suite_t( indexing_suite_t ):
    """
    Creates boost.python code that needed to export a vector of some class
    """
    #class_< std::vector<X> >("XVec")
    #    .def(vector_indexing_suite<std::vector<X> >())
    #;

    def __init__(self, class_inst, suite_configuration, parent=None ):        
        indexing_suite_t.__init__( self
                                   , class_inst=class_inst
                                   , suite_configuration=suite_configuration
                                   , parent=parent )

    def _create_indexing_suite_declaration( self ):
        vector_indexing_suite = algorithm.create_identifier( self, 'boost::python::vector_indexing_suite' )
        container_identifier = algorithm.create_identifier( self, self.suite_configuration.container )
        container = declarations.templates.join( container_identifier, [ self.decl_identifier ] )
        args = [container]
        if self.suite_configuration.derived_policies:
            if self.suite_configuration.no_proxy:
                args.append( 'true' )
            else:
                args.append( 'false' )
            args.append( self.suite_configuration.derived_policies )
        else:
            if self.suite_configuration.no_proxy:
                args.append( 'true' )        
        return declarations.templates.join( vector_indexing_suite, args )        

    def _create_class_declaration( self ):
        class_ = algorithm.create_identifier( self, 'boost::python::class_' )
        container_identifier = algorithm.create_identifier( self, self.suite_configuration.container )
        container = declarations.templates.join( container_identifier, [ self.decl_identifier ] )
        return declarations.templates.join( class_, [ container ] )        

    def _create_impl(self):
        result = []
        result.append( self._create_class_declaration() + '("%s")' % self.suite_configuration.name )
        result.append( self.indent( ".def( %s() )" %  self._create_indexing_suite_declaration() ) )
        result.append( ';' )
        return os.linesep.join( result )
        
    