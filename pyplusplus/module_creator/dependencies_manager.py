# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""defines class, which informs user about used, but unexposed declarations"""

import os
from pygccxml import declarations
from pyplusplus import decl_wrappers

class manager_t( object ):
    def __init__( self, logger ):
        object.__init__( self )
        self.__exported_decls = []
        self.__logger = logger
        
    def add_exported( self, decl ):
        self.__exported_decls.append( decl )  

    def __is_std_decl( self, decl ):
        if not decl.parent:
            return False

        if not isinstance( decl.parent, declarations.namespace_t ):
            return False

        if 'std' != decl.parent.name:
            return False

        ns_std = decl.parent
        if not ns_std.parent:
            return False

        if not isinstance( ns_std.parent, declarations.namespace_t ):
            return False

        if '::' != ns_std.parent.name:
            return False

        global_ns = ns_std.parent
        if global_ns.parent:
            return False 
        
        if decl.name.startswith( 'pair<' ):
            #special case
            return False
        return True

    def __build_dependencies( self, decl ):
        if self.__is_std_decl( decl ):
            return [] #std declarations should be exported by Py++!
        
        dependencies = decl.i_depend_on_them(recursive=False)
        if isinstance( decl, declarations.class_t ):
            dependencies = filter( lambda d: d.access_type != declarations.ACCESS_TYPES.PRIVATE
                                   , dependencies )
        return dependencies
    
    def __find_out_used_but_not_exported( self ):
        used_not_exported = []
        exported_ids = set( map( lambda d: id( d ), self.__exported_decls ) )
        for decl in self.__exported_decls:
            for dependency in self.__build_dependencies( decl ):
                depend_on_decl = dependency.find_out_depend_on_declaration()
                if None is depend_on_decl:
                    continue
                if self.__is_std_decl( depend_on_decl ):
                    continue
                if isinstance( depend_on_decl, declarations.class_types ) and depend_on_decl.opaque:
                    continue
                if id( depend_on_decl ) not in exported_ids:
                    used_not_exported.append( dependency )                    
        return used_not_exported

    def __group_by_unexposed( self, dependencies ):
        groups = {}
        for dependency in dependencies:
            depend_on_decl = dependency.find_out_depend_on_declaration()
            if not groups.has_key( id( depend_on_decl ) ):
                groups[ id( depend_on_decl ) ] = []
            groups[ id( depend_on_decl ) ].append( dependency )
        return groups

    def __create_msg( self, dependencies ):
        depend_on_decl = dependencies[0].find_out_depend_on_declaration()
        reason = [ 'There are declarations, which depend on the unexposed one:' ]
        for dependency in dependencies:
            reason.append( ' ' + str( dependency.declaration ) )
        return "%s;%s" % ( depend_on_decl, os.linesep.join( reason ) )
        
    def inform_user( self ):
        used_not_exported_decls = self.__find_out_used_but_not_exported()
        groups = self.__group_by_unexposed( used_not_exported_decls )
        for group in groups.itervalues():
            self.__logger.warn( self.__create_msg( group ) )
