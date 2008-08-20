# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""defines class, which informs user about used, but unexposed declarations"""

import os
from pyplusplus import utils
from pyplusplus import messages
from pygccxml import declarations
from pyplusplus import decl_wrappers


class manager_t( object ):
    def __init__( self, logger ):
        object.__init__( self )
        self.__exported_decls = []
        self.__logger = logger

    def add_exported( self, decl ):
        self.__exported_decls.append( decl )

    def __select_duplicate_aliases( self, decls ):
        duplicated = {}
        for decl in decls:
            if not duplicated.has_key( decl.alias ):
                duplicated[ decl.alias ] = set()
            duplicated[ decl.alias ].add( decl )
        for alias, buggy_decls in duplicated.items():
            if 1 == len( buggy_decls ):
                del duplicated[ alias ]
        return duplicated

    def __report_duplicate_aliases_impl( self, control_decl, duplicated ):
        if control_decl.alias in duplicated:
            buggy_decls = duplicated[control_decl.alias].copy()
            buggy_decls.remove( control_decl )
            warning = messages.W1047 % ( control_decl.alias
                                         , os.linesep.join( map( str, buggy_decls ) ) )
            self.__logger.warn( "%s;%s" % ( control_decl, warning ) )

        if isinstance( control_decl, declarations.class_t ):
            query = lambda i_decl: isinstance( i_decl, declarations.class_types ) \
                                   and i_decl.ignore == False
            i_decls = control_decl.classes( query, recursive=False, allow_empty=True )
            i_duplicated = self.__select_duplicate_aliases( i_decls )
            for i_decl in i_decls:
                self.__report_duplicate_aliases_impl( i_decl, i_duplicated )

    def __report_duplicate_aliases( self ):
        decls = filter( lambda decl: isinstance( decl, declarations.class_types ) \
                                     and isinstance( decl.parent, declarations.namespace_t )
                        , self.__exported_decls )
        duplicated = self.__select_duplicate_aliases( decls )
        for decl in decls:
            self.__report_duplicate_aliases_impl( decl, duplicated )

    def __is_std_decl( self, decl ):
        #Every class under std should be exported by Boost.Python and\\or Py++
        #Also this is not the case right now, I prefer to hide the warnings
        dpath = declarations.declaration_path( decl )
        if len( dpath ) < 3:
            return False
        if dpath[1] != 'std':
            return False
        if decl.name.startswith( 'pair<' ):
            #special case
            return False
        return True

    def __build_dependencies( self, decl ):
        if self.__is_std_decl( decl ):
            #TODO add element_type to the list of dependencies
            return [] #std declarations should be exported by Py++!
        if decl.already_exposed:
            return []
        dependencies = decl.i_depend_on_them(recursive=False)
        
        if isinstance( decl, declarations.class_t ):
            dependencies = filter( lambda d: d.access_type != declarations.ACCESS_TYPES.PRIVATE
                                   , dependencies )            
            
        return dependencies

    def __has_unexposed_dependency( self, exported_ids, depend_on_decl, dependency ):       
        sptr_traits = declarations.smart_pointer_traits
                
        if None is depend_on_decl:
            return
            
        if self.__is_std_decl( depend_on_decl ):
            return 
            
        if sptr_traits.is_smart_pointer( depend_on_decl ):
            try:
                value_type = sptr_traits.value_type( depend_on_decl )
                return self.__has_unexposed_dependency( exported_ids, value_type, dependency )
            except RuntimeError:
                pass 
                
        if isinstance( depend_on_decl, decl_wrappers.decl_wrapper_t ):
            if depend_on_decl.already_exposed:
                return 
            if isinstance( depend_on_decl, declarations.class_types ):
                if depend_on_decl.opaque:
                    return 
                if dependency.hint == "base class":
                    return #base class for some class don't have to be exported
            if isinstance( depend_on_decl, declarations.variable_t ):
                if not decl.expose_value:
                    return 
        
        if isinstance( dependency.decl, declarations.variable_t ):
            #the only dependency of the variable is its type
            if not dependency.decl.expose_value:
                return 
                
        if dependency.hint == "return type":
            #in this case we don't check, the return type but the function
            if isinstance( dependency.decl, declarations.calldef_t ):
                if dependency.decl.return_type and dependency.decl.call_policies \
                   and decl_wrappers.is_return_opaque_pointer_policy( dependency.decl.call_policies ):
                   return

        return id( depend_on_decl ) not in exported_ids
            
    def __find_out_used_but_not_exported( self ):
        used_not_exported = []
        exported_ids = set( map( lambda d: id( d ), self.__exported_decls ) )
        for decl in self.__exported_decls:
            for dependency in self.__build_dependencies( decl ):        
                depend_on_decl = dependency.find_out_depend_on_declaration()                
                if self.__has_unexposed_dependency( exported_ids, depend_on_decl, dependency ):
                    if messages.filter_disabled_msgs([messages.W1040], depend_on_decl.disabled_messages ):
                        #need to report dependency errors
                        used_not_exported.append(dependency)
        return used_not_exported

    def __group_by_unexposed( self, dependencies ):
        groups = {}
        for dependency in dependencies:
            depend_on_decl = dependency.find_out_depend_on_declaration()
            if not groups.has_key( id( depend_on_decl ) ):
                groups[ id( depend_on_decl ) ] = []
            groups[ id( depend_on_decl ) ].append( dependency )
        return groups

    def __create_dependencies_msg( self, dependencies ):
        depend_on_decl = dependencies[0].find_out_depend_on_declaration()
        decls = []
        for dependency in dependencies:
            decls.append( os.linesep + ' ' + str( dependency.declaration ) )
        return "%s;%s" % ( depend_on_decl, messages.W1040 % ''.join( decls ) )

    def inform_user( self ):
        used_not_exported_decls = self.__find_out_used_but_not_exported()
        groups = self.__group_by_unexposed( used_not_exported_decls )
        for group in groups.itervalues():
            self.__logger.warn( self.__create_dependencies_msg( group ) )
        self.__report_duplicate_aliases()
