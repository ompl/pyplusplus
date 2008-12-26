# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


import dependencies_manager
from pygccxml import declarations
from pyplusplus import decl_wrappers
from pyplusplus import code_creators
from pyplusplus import code_repository
from pyplusplus import _logging_

ACCESS_TYPES = declarations.ACCESS_TYPES
VIRTUALITY_TYPES = declarations.VIRTUALITY_TYPES

class ctypes_creator_t( declarations.decl_visitor_t ):
    def __init__( self
                  , global_ns
                  , library_path
                  , exported_symbols
                  , doc_extractor=None ):
        declarations.decl_visitor_t.__init__(self)
        self.logger = _logging_.loggers.module_builder
        self.decl_logger = _logging_.loggers.declarations

        self.__library_path = library_path
        self.__exported_symbols = exported_symbols

        self.__extmodule = code_creators.ctypes_module_t( global_ns )
        self.__dependencies_manager = dependencies_manager.manager_t(self.decl_logger)

        #~ prepared_decls = self.__prepare_decls( global_ns, doc_extractor )
        #~ self.__decls = sort_algorithms.sort( prepared_decls )
        self.curr_decl = global_ns
        self.curr_code_creator = self.__extmodule

    def __print_readme( self, decl ):
        readme = decl.readme()
        if not readme:
            return

        if not decl.exportable:
            reason = readme[0]
            readme = readme[1:]
            self.decl_logger.warn( "%s;%s" % ( decl, reason ) )

        for msg in readme:
            self.decl_logger.warn( "%s;%s" % ( decl, msg ) )

    #~ def __prepare_decls( self, global_ns, doc_extractor ):
        #~ to_be_exposed = []
        #~ for decl in declarations.make_flatten( global_ns ):
            #~ if decl.ignore:
                #~ continue

            #~ if not decl.exportable:
                #~ #leave only decls that user wants to export and that could be exported
                #~ self.__print_readme( decl )
                #~ continue

            #~ if decl.already_exposed:
                #~ #check wether this is already exposed in other module
                #~ continue

            #~ if isinstance( decl.parent, declarations.namespace_t ):
                #~ #leave only declarations defined under namespace, but remove namespaces
                #~ to_be_exposed.append( decl )

            #~ if doc_extractor:
                #~ decl.documentation = doc_extractor( decl )

            #~ self.__print_readme( decl )

        #~ return to_be_exposed


    def create(self ):
        """Create and return the module for the extension.

        @returns: Returns the root of the code creators tree
        @rtype: L{module_t<code_creators.module_t>}
        """
        # Invoke the appropriate visit_*() method on all decls
        self.__extmodule.adopt_creator( code_creators.import_t( 'ctypes' ) )
        self.__extmodule.adopt_creator( code_creators.separator_t() )
        self.__extmodule.adopt_creator( code_creators.library_reference_t( self.__library_path ) )
        self.__extmodule.adopt_creator( code_creators.name_mappings_t( self.__exported_symbols ) )
        self.__extmodule.adopt_creator( code_creators.separator_t() )

        declarations.apply_visitor( self, self.curr_decl )

        self.__dependencies_manager.inform_user()

        return self.__extmodule

    def visit_member_function( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_constructor( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_destructor( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_member_operator( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_casting_operator( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_free_function( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_free_operator( self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_class_declaration(self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_class(self ):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_enumeration(self):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_namespace(self):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_typedef(self):
        self.__dependencies_manager.add_exported( self.curr_decl )

    def visit_variable(self):
        self.__dependencies_manager.add_exported( self.curr_decl )
