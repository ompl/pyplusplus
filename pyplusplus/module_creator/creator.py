# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import time
import types_database
import class_organizer
import call_policies_resolver 
from pygccxml import declarations
from pyplusplus import decl_wrappers
from pyplusplus import code_creators
from pyplusplus import code_repository
from pyplusplus import _logging_

ACCESS_TYPES = declarations.ACCESS_TYPES
VIRTUALITY_TYPES = declarations.VIRTUALITY_TYPES

#TODO: don't export functions that returns non const pointer to fundamental types
#TODO: add print decl_wrapper.readme messages
#class Foo{
#      union {
#           struct {
#                   float r,g,b,a;
#           };
#           float val[4];
#       };
#};

INDEXING_SUITE_1_CONTAINERS = { 
    'vector<' : "boost/python/suite/indexing/vector_indexing_suite.hpp" 
    , 'map<' : "boost/python/suite/indexing/map_indexing_suite.hpp" 
}

INDEXING_SUITE_2_CONTAINERS = {
      'vector<' : "boost/python/suite/indexing/vector.hpp"
    , 'deque<' : "boost/python/suite/indexing/deque.hpp"
    , 'list<' : "boost/python/suite/indexing/list.hpp"
    , 'map<' : "boost/python/suite/indexing/map.hpp"
    , 'hash_map<' : "boost/python/suite/indexing/map.hpp"
    , 'set<' : "boost/python/suite/indexing/set.hpp"
    , 'hash_set<' : "boost/python/suite/indexing/set.hpp"
    #TODO: queue, priority, stack, multimap, hash_multimap, multiset, hash_multiset
}

INDEXING_SUITE_2_MAIN_HEADER = "boost/python/suite/indexing/container_suite.hpp"

DO_NOT_REPORT_MSGS = [ "pyplusplus does not exports compiler generated constructors" ]

class creator_t( declarations.decl_visitor_t ):
    """Creating code creators.

    This class takes a set of declarations as input and creates a code
    creator tree that contains the Boost.Python C++ source code for the
    final extension module. Each node in the code creators tree represents
    a block of text (C++ source code).

    Usage of this class: Create an instance and pass all relevant input
    data to the constructor. Then call L{create()} to obtain the code
    creator tree whose root node is a L{module_t<code_creators.module_t>}
    object representing the source code for the entire extension module.
    """
    
    def __init__( self
                  , decls
                  , module_name
                  , boost_python_ns_name='bp'
                  , create_castinig_constructor=False
                  , call_policies_resolver_=None
                  , types_db=None
                  , target_configuration=None
                  , enable_indexing_suite=True
                  , doc_extractor=None):
        """Constructor.

        @param decls: Declarations that should be exposed in the final module.
        @param module_name: The name of the final module.
        @param boost_python_ns_name: The alias for the boost::python namespace.
        @param create_castinig_constructor: ...todo...
        @param call_policies_resolver_: Callable that takes one declaration (calldef_t) as input and returns a call policy object which should be used for this declaration.
        @param types_db: ...todo...
        @param target_configuration: A target configuration object can be used to customize the generated source code to a particular compiler or a particular version of Boost.Python.
        @param doc_extractor: callable, that takes as argument declaration reference and returns documentation string
        @type decls: list of declaration_t
        @type module_name: str
        @type boost_python_ns_name: str
        @type create_castinig_constructor: bool
        @type call_policies_resolver_: callable
        @type types_db: L{types_database_t<types_database.types_database_t>}
        @type target_configuration: L{target_configuration_t<code_creators.target_configuration_t>}
        @type doc_extractor: callable
        """
        declarations.decl_visitor_t.__init__(self)        
        self.logger = _logging_.loggers.module_builder
        self.decl_logger = _logging_.loggers.declarations
        
        self.__enable_indexing_suite = enable_indexing_suite
        self.__target_configuration = target_configuration
        if not self.__target_configuration:
            self.__target_configuration = code_creators.target_configuration_t()

        self.__call_policies_resolver = call_policies_resolver_
        if not self.__call_policies_resolver:
            self.__call_policies_resolver \
                = call_policies_resolver.built_in_resolver_t(self.__target_configuration)

        self.__types_db = types_db
        if not self.__types_db:
            self.__types_db = types_database.types_database_t()
        
        self.__extmodule = code_creators.module_t()        
        self.__extmodule.add_system_header( "boost/python.hpp" )
        self.__extmodule.adopt_creator( code_creators.include_t( header="boost/python.hpp" ) )
        self.__create_castinig_constructor = create_castinig_constructor
        if boost_python_ns_name:
            bp_ns_alias = code_creators.namespace_alias_t( alias=boost_python_ns_name
                                                           , full_namespace_name='::boost::python' ) 
            self.__extmodule.adopt_creator( bp_ns_alias )
        
        self.__module_body = code_creators.module_body_t( name=module_name )
        self.__extmodule.adopt_creator( self.__module_body )        
        
        prepared_decls = self._prepare_decls( decls, doc_extractor )
        self.__decls = self._filter_decls( self._reorder_decls( prepared_decls ) )
            
        self.curr_code_creator = self.__module_body
        self.curr_decl = None
        self.__cr_array_1_included = False
        self.__array_1_registered = set() #(type.decl_string,size)
        self.__free_operators = []
        
    def _prepare_decls( self, decls, doc_extractor ):
        global DO_NOT_REPORT_MSGS

        decls = declarations.make_flatten( decls )

        for decl in decls:
            if decl.ignore:
                continue
            
            if doc_extractor and decl.exportable:
                decl.documentation = doc_extractor( decl )

            readme = decl.readme()
            if not readme:
                continue
            
            if not decl.exportable:
                reason = readme[0]
                if reason in DO_NOT_REPORT_MSGS:
                    continue
                readme = readme[1:]
                msgstr = "%s;%s"%(decl, reason.replace(os.linesep, " "))
                self.decl_logger.warn( msgstr )
            
            for msg in readme:
                msgstr = "%s;%s"%(decl, msg.replace(os.linesep, " "))
                self.decl_logger.warn( msgstr )
        
        #leave only declarations defined under namespace, but remove namespaces
        decls = filter( lambda x: not isinstance( x, declarations.namespace_t ) \
                                   and isinstance( x.parent, declarations.namespace_t )
                         , decls )
        #leave only decls that user wants to export and that could be exported
        decls = filter( lambda x: x.ignore == False and x.exportable == True, decls )
        
        return decls

    def _reorder_decls(self, decls ):
        classes = filter( lambda x: isinstance( x, declarations.class_t )
                          , decls )
        
        ordered = class_organizer.findout_desired_order( classes )
        ids = set( [ id( inst ) for inst in ordered ] )
        for decl in decls:
            if id( decl ) not in ids:
                ids.add( id(decl) )
                ordered.append( decl )
        #type should be exported before it can be used.
        variables = []
        enums = []
        others = []
        classes = []
        constructors = []
        for inst in ordered:
            if isinstance( inst, declarations.variable_t ):
                variables.append( inst )
            elif isinstance( inst, declarations.enumeration_t ):
                enums.append( inst )
            elif isinstance( inst, ( declarations.class_t, declarations.class_declaration_t ) ):
                classes.append( inst )
            elif isinstance( inst, declarations.constructor_t ):
                constructors.append( inst )
            else:
                others.append( inst )
        #this will prevent from py++ to change the order of generated code
        cmp_by_name = lambda d1, d2: cmp( d1.name, d2.name ) 
        cmp_by_line = lambda d1, d2: cmp( d1.location.line, d2.location.line ) 

        enums.sort( cmp=cmp_by_name )
        others.sort( cmp=cmp_by_name )
        variables.sort( cmp=cmp_by_name )
        constructors.sort( cmp=cmp_by_line )
        
        new_ordered = []
        new_ordered.extend( enums )
        new_ordered.extend( classes )
        new_ordered.extend( constructors )
        new_ordered.extend( others )
        new_ordered.extend( variables )
        return new_ordered #
    
    def _exportable_class_members( self, class_decl ):
        assert isinstance( class_decl, declarations.class_t )
        members = filter( lambda mv: mv.ignore == False and mv.exportable, class_decl.public_members )
        #protected and private virtual functions that not overridable and not pure
        #virtual should not be exported
        for member in class_decl.protected_members:
            if not isinstance( member, declarations.calldef_t ):
                continue
            else:
                members.append( member )
       
        vfunction_selector = lambda member: isinstance( member, declarations.member_function_t ) \
                                            and member.virtuality == VIRTUALITY_TYPES.PURE_VIRTUAL 
        members.extend( filter( vfunction_selector, class_decl.private_members ) )
        #now lets filter out none public operators: pyplusplus does not support them right now
        members = filter( lambda decl: not isinstance( decl, declarations.member_operator_t )
                                       or decl.access_type == ACCESS_TYPES.PUBLIC 
                          , members )
        #-#if declarations.has_destructor( class_decl ) \
        #-#   and not declarations.has_public_destructor( class_decl ):
            #remove artificial constructors
        members = filter( lambda decl: not isinstance( decl, declarations.constructor_t )
                                       or not decl.is_artificial
                          , members )
        members = filter( lambda member: member.ignore == False and member.exportable, members )
        ordered_members = self._reorder_decls( members )
        return ordered_members
    
    def _does_class_have_smth_to_export(self, exportable_members ):
        return bool( self._filter_decls( exportable_members ) )
    
    def _is_constructor_of_abstract_class( self, decl ):
        assert isinstance( decl, declarations.constructor_t )
        return decl.parent.is_abstract
        
    def _filter_decls( self, decls ):
        # Filter out artificial (compiler created) types unless they are classes
        # See: http://public.kitware.com/pipermail/gccxml/2004-October/000486.html
        decls = filter( lambda x: not (x.is_artificial and 
                                       not (isinstance(x, ( declarations.class_t, declarations.enumeration_t))))
                       , decls )
        # Filter out type defs
        decls = filter( lambda x: not isinstance( x, declarations.typedef_t ), decls )

        return decls

    def __is_same_func( self, f1, f2 ):
        if not f1.__class__ is f2.__class__:
            return False
        if isinstance( f1, declarations.member_calldef_t ) and f1.has_const != f2.has_const:
            return False
        if f1.name != f2.name:
            return False
        if f1.return_type != f2.return_type:
            return False
        if len( f1.arguments ) != len(f2.arguments):
            return False
        for f1_arg, f2_arg in zip( f1.arguments, f2.arguments ):
            if f1_arg.type != f2_arg.type:
                return False
        return True
            
    def redefined_funcs( self, cls ):
        all_included = declarations.custom_matcher_t( lambda decl: decl.ignore == False and decl.exportable )
        all_protected = declarations.access_type_matcher_t( 'protected' ) & all_included
        all_pure_virtual = declarations.virtuality_type_matcher_t( VIRTUALITY_TYPES.PURE_VIRTUAL )
        all_not_pure_virtual = ~all_pure_virtual
        
        query = all_protected | all_pure_virtual
        
        funcs = set()
        defined_funcs = set()
        
        for base in cls.recursive_bases:
            if base.access == ACCESS_TYPES.PRIVATE:
                continue
            base_cls = base.related_class
            funcs.update( base_cls.member_functions( query, allow_empty=True ) )
            funcs.update( base_cls.member_operators( query, allow_empty=True ) )

            defined_funcs.update( base_cls.member_functions( all_not_pure_virtual, allow_empty=True ) )
            defined_funcs.update( base_cls.member_operators( all_not_pure_virtual, allow_empty=True ) )

        not_reimplemented_funcs = set()        
        for f in funcs:
            cls_fs = cls.calldefs( name=f.name, recursive=False, allow_empty=True )
            for cls_f in cls_fs:
                if self.__is_same_func( f, cls_f ):
                    break
            else:
                #should test whether this function has been added or not
                for f_impl in not_reimplemented_funcs:
                    if self.__is_same_func( f, f_impl ):
                        break
                else:
                    #should test whether this function is implemented in base class
                    if f.virtuality != VIRTUALITY_TYPES.PURE_VIRTUAL:
                        not_reimplemented_funcs.add( f )
                    else:
                        for f_defined in defined_funcs:
                            if self.__is_same_func( f, f_defined ):
                                break
                        else:
                            not_reimplemented_funcs.add( f )
        functions = list( not_reimplemented_funcs )
        functions.sort( cmp=lambda f1, f2: cmp( ( f1.name, f1.location.as_tuple() )
                                                , ( f2.name, f2.location.as_tuple() ) ) )
        return functions
    
    def _is_wrapper_needed(self, class_inst, exportable_members):
        if isinstance( self.curr_decl, declarations.class_t ) \
           and self.curr_decl.wrapper_user_code:
            return True
        elif isinstance( self.curr_code_creator, declarations.class_t ) \
           and self.curr_code_creator.wrapper_user_code:
            return True
        else:
            pass
        
        for member in exportable_members:
            if isinstance( member, declarations.destructor_t ):
                continue
            if isinstance( member, declarations.variable_t ):
                if member.bits:
                    return True
                if declarations.is_pointer( member.type ):
                    return True
                if declarations.is_reference( member.type ):
                    return True
                if declarations.is_array( member.type ):
                    return True
            if isinstance( member, declarations.class_t ):
                return True
            if isinstance( member, declarations.calldef_t ):
                if member.virtuality != VIRTUALITY_TYPES.NOT_VIRTUAL:
                    return True #virtual and pure virtual functions requieres wrappers.
                if member.access_type in ( ACCESS_TYPES.PROTECTED, ACCESS_TYPES.PRIVATE ):
                    return True #we already decided that those functions should be exposed, so I need wrapper for them
        return bool( self.redefined_funcs(class_inst) )
    
    def _adopt_free_operator( self, operator ):
        def adopt_operator_impl( operator, found_creators ):
            creator = filter( lambda creator: isinstance( creator, code_creators.class_t )
                              , found_creators )
            if len(creator) == 1:                
                creator = creator[0]
                #I think I don't need this condition any more
                if not find( lambda creator: isinstance( creator, code_creators.declaration_based_t )
                                             and operator is creator.declaration
                             , creator.creators ):
                    #expose operator only once
                    creator.adopt_creator( code_creators.operator_t( operator=operator ) )
            elif not creator:
                pass
            else:
                assert 0
        find = code_creators.creator_finder.find_by_declaration
        if isinstance( operator.parent, declarations.class_t ):
            found = find( lambda decl: operator.parent is decl
                          , self.__extmodule.body.creators )
            adopt_operator_impl( operator, found )
        else:
            arg_type = declarations.base_type( operator.arguments[0].type )
            if isinstance( arg_type, declarations.fundamental_t ):
                arg_type = declarations.base_type( operator.arguments[1].type )
            assert isinstance( arg_type, declarations.declarated_t )
            found = find( lambda decl: arg_type.declaration is decl
                          , self.__extmodule.body.creators )
            adopt_operator_impl( operator, found )

    def _is_registered_smart_pointer_creator( self, creator, db ):
        for registered in db:
            if not isinstance( creator, registered.__class__ ):
                continue
            elif registered.smart_ptr != creator.smart_ptr:
                continue
            elif isinstance( creator, code_creators.smart_pointer_registrator_t ):
                if creator.declaration is registered.declaration:
                    return True
            elif isinstance( creator, code_creators.smart_pointers_converter_t ):
                if ( creator.source is registered.source ) \
                   and ( creator.target is registered.target ):
                    return True
            else:
                assert 0 #unknown instace of registrator
                
    def _treat_smart_pointers( self ):
        """ Go to all class creators and apply held_type and creator registrators
            as needed.
        """
        find_classes = code_creators.creator_finder.find_by_class_instance
        class_creators = find_classes( what=code_creators.class_t
                                       , where=self.__extmodule.body.creators
                                       , recursive=True )
        registrators_db = []
        for creator in class_creators:
            if None is creator.held_type:
                creator.held_type = self.__types_db.create_holder( creator.declaration )
            registrators = self.__types_db.create_registrators( creator )
            for r in registrators:
                if not self._is_registered_smart_pointer_creator( r, registrators_db ):
                    creator.adopt_creator(r)
                    registrators_db.append(r)
    
    def _append_user_code( self ):
        ctext_t = code_creators.custom_text_t
        for creator in code_creators.make_flatten( self.__extmodule ):
            if isinstance( creator, code_creators.class_t ):
                for user_code in creator.declaration.user_code:
                    creator.adopt_creator( 
                        ctext_t( user_code.text
                                 , works_on_instance=user_code.works_on_instance ) )
            elif isinstance( creator, code_creators.class_wrapper_t ):
                for user_code in creator.declaration.wrapper_user_code:
                    creator.adopt_creator( ctext_t( user_code.text ) )
            else:
                pass
    
    def _treat_indexing_suite( self ):
        global INDEXING_SUITE_1_CONTAINERS
        global INDEXING_SUITE_2_CONTAINERS
        global INDEXING_SUITE_2_MAIN_HEADER
        
        def create_explanation(cls):
            msg = '//WARNING: the next line of code will not compile, because "%s" does not have operator== !'
            msg = msg % cls.indexing_suite.element_type.decl_string
            return code_creators.custom_text_t( msg, False )
        
        def create_cls_cc( cls ):
            if isinstance( cls, declarations.class_t ):
                return code_creators.class_t( class_inst=cls )
            else:
                return code_creators.class_declaration_t( class_inst=cls )

        if not self.__types_db.used_containers:
            return 
        
        used_headers = set()

        creators = []
        
        cmp_by_name = lambda cls1, cls2: cmp( cls1.decl_string, cls2.decl_string )
        used_containers = list( self.__types_db.used_containers )
        used_containers.sort( cmp_by_name )
        for cls in used_containers:
            container_name = cls.name.split( '<' )[0] + '<'

            if isinstance( cls.indexing_suite, decl_wrappers.indexing_suite1_t ):
                isuite = INDEXING_SUITE_1_CONTAINERS
            else:
                isuite = INDEXING_SUITE_2_CONTAINERS

            if not isuite.has_key( container_name ):
                continue #not supported
            
            if isuite is INDEXING_SUITE_2_CONTAINERS:
                used_headers.add( INDEXING_SUITE_2_MAIN_HEADER ) 

            used_headers.add( isuite[ container_name ] )

            cls_creator = create_cls_cc( cls )
            creators.append( cls_creator )
            try:
                element_type = cls.indexing_suite.element_type
            except:
                element_type = None
            if isuite is INDEXING_SUITE_1_CONTAINERS:
                if not ( None is element_type ) \
                   and declarations.is_class( element_type ) \
                   and not declarations.has_public_equal( element_type ):
                    cls_creator.adopt_creator( create_explanation( cls ) )  
                cls_creator.adopt_creator( code_creators.indexing_suite1_t(cls) )
            else:
                class_traits = declarations.class_traits
                if not ( None is element_type ) \
                   and class_traits.is_my_case( element_type ):
                    value_cls = class_traits.get_declaration( element_type )
                    element_type_cc = code_creators.value_traits_t( value_cls )
                    self.__extmodule.adopt_declaration_creator( element_type_cc )                        
                cls_creator.adopt_creator( code_creators.indexing_suite2_t(cls) )

        if INDEXING_SUITE_2_MAIN_HEADER in used_headers:
            #I want this header to be the first one.
            used_headers.remove( INDEXING_SUITE_2_MAIN_HEADER )
            self.__extmodule.add_system_header( INDEXING_SUITE_2_MAIN_HEADER )
            self.__extmodule.add_include( INDEXING_SUITE_2_MAIN_HEADER )
            
        for header in used_headers:
            self.__extmodule.add_system_header( header )
            self.__extmodule.add_include( header )
    
        #I am going tp find last class registration and to add all container creators
        #after it.
        last_cls_index = -1
        for i in range( len( self.__module_body.creators ) - 1, -1, -1 ):
            if isinstance( self.__module_body.creators[i], code_creators.class_t ):
                last_cls_index = i
                break
        insert_position = last_cls_index + 1
        creators.reverse()
        for creator in creators:
            self.__module_body.adopt_creator( creator, insert_position )
            
    def create(self, decl_headers=None):
        """Create and return the module for the extension.
        
        @param decl_headers: If None the headers for the wrapped decls are automatically found.
        But you can pass a list of headers here to override that search.
        @returns: Returns the root of the code creators tree
        @rtype: L{module_t<code_creators.module_t>}
        """
        if not decl_headers:
            self._create_includes()
        else:
            for h in decl_headers:
                self.__extmodule.adopt_include(code_creators.include_t(header=h))
        # Invoke the appropriate visit_*() method on all decls
        for decl in self.__decls:
            self.curr_decl = decl
            declarations.apply_visitor( self, decl )
        for operator in self.__free_operators:
            self._adopt_free_operator( operator )
        self._treat_smart_pointers()
        if self.__enable_indexing_suite:
            self._treat_indexing_suite()
        for creator in code_creators.make_flatten( self.__extmodule ):
            creator.target_configuration = self.__target_configuration
        #last action.
        self._append_user_code()
        return self.__extmodule

    def _create_includes(self):
        for fn in declarations.declaration_files( self.__decls ):
            include = code_creators.include_t( header=fn )
            self.__extmodule.adopt_include(include)

    def guess_functions_code_creators( self ):
        maker_cls = None
        fwrapper_cls = None
        access_level = self.curr_decl.parent.find_out_member_access_type( self.curr_decl )
        if access_level == ACCESS_TYPES.PUBLIC:
            if self.curr_decl.virtuality == VIRTUALITY_TYPES.NOT_VIRTUAL:
                maker_cls = code_creators.mem_fun_t
            elif self.curr_decl.virtuality == VIRTUALITY_TYPES.PURE_VIRTUAL:
                fwrapper_cls = code_creators.mem_fun_pv_wrapper_t
                maker_cls = code_creators.mem_fun_pv_t
            else:
                if self.curr_decl.overridable:
                    fwrapper_cls = code_creators.mem_fun_v_wrapper_t
                maker_cls = code_creators.mem_fun_v_t
        elif access_level == ACCESS_TYPES.PROTECTED:
            if self.curr_decl.virtuality == VIRTUALITY_TYPES.NOT_VIRTUAL:
                if self.curr_decl.has_static:
                    fwrapper_cls = code_creators.mem_fun_protected_s_wrapper_t
                    maker_cls = code_creators.mem_fun_protected_s_t
                else:
                    fwrapper_cls = code_creators.mem_fun_protected_wrapper_t
                    maker_cls = code_creators.mem_fun_protected_t
            elif self.curr_decl.virtuality == VIRTUALITY_TYPES.VIRTUAL:
                if self.curr_decl.overridable:
                    fwrapper_cls = code_creators.mem_fun_protected_v_wrapper_t
                    maker_cls = code_creators.mem_fun_protected_v_t
            else:
                fwrapper_cls = code_creators.mem_fun_protected_pv_wrapper_t
                maker_cls = code_creators.mem_fun_protected_pv_t
        else: #private
            if self.curr_decl.virtuality == VIRTUALITY_TYPES.NOT_VIRTUAL:
                pass#in general we should not come here
            elif self.curr_decl.virtuality == VIRTUALITY_TYPES.PURE_VIRTUAL:
                fwrapper_cls = code_creators.mem_fun_private_pv_wrapper_t
            else:
                if self.curr_decl.overridable:
                    fwrapper_cls = code_creators.mem_fun_v_wrapper_t
                    maker_cls = code_creators.mem_fun_v_t
        return ( maker_cls, fwrapper_cls )
    
    def visit_member_function( self ):
        fwrapper = None
        self.__types_db.update( self.curr_decl )
        if None is self.curr_decl.call_policies:
            self.curr_decl.call_policies = self.__call_policies_resolver( self.curr_decl )
    
        maker_cls, fwrapper_cls = self.guess_functions_code_creators()
        
        maker = None
        fwrapper = None
        if fwrapper_cls:
            fwrapper = fwrapper_cls( function=self.curr_decl )
            class_wrapper = self.curr_code_creator.wrapper
            class_wrapper.adopt_creator( fwrapper )
           
        if maker_cls:
            if fwrapper:
                maker = maker_cls( function=self.curr_decl, wrapper=fwrapper )
            else:
                maker = maker_cls( function=self.curr_decl )
            self.curr_code_creator.adopt_creator( maker )            
        
        if self.curr_decl.has_static:
            #static_method should be created only once.
            found = filter( lambda creator: isinstance( creator, code_creators.static_method_t ) 
                                            and creator.declaration.name == self.curr_decl.name
                                     , self.curr_code_creator.creators )
            if not found:
                static_method = code_creators.static_method_t( function=self.curr_decl
                                                               , function_code_creator=maker )
                self.curr_code_creator.adopt_creator( static_method )
        
    def visit_constructor( self ):
        if self.curr_decl.is_copy_constructor:
            return             
        self.__types_db.update( self.curr_decl )
        if not self._is_constructor_of_abstract_class( self.curr_decl ) \
           and 1 == len( self.curr_decl.arguments ) \
           and self.__create_castinig_constructor \
           and self.curr_decl.access_type == ACCESS_TYPES.PUBLIC:
            maker = code_creators.casting_constructor_t( constructor=self.curr_decl )
            self.__module_body.adopt_creator( maker )

        cwrapper = None
        exportable_members = self._exportable_class_members(self.curr_code_creator.declaration)
        if self._is_wrapper_needed( self.curr_decl.parent, exportable_members ):
            class_wrapper = self.curr_code_creator.wrapper
            cwrapper = code_creators.constructor_wrapper_t( constructor=self.curr_decl )
            class_wrapper.adopt_creator( cwrapper )
        maker = code_creators.constructor_t( constructor=self.curr_decl, wrapper=cwrapper )
        if None is self.curr_decl.call_policies:
            self.curr_decl.call_policies = self.__call_policies_resolver( self.curr_decl )
        self.curr_code_creator.adopt_creator( maker )
    
    def visit_destructor( self ):
        pass
    
    def visit_member_operator( self ):
        if self.curr_decl.symbol in ( '()', '[]' ):
            self.visit_member_function()
        else:
            self.__types_db.update( self.curr_decl )
            maker = code_creators.operator_t( operator=self.curr_decl )
            self.curr_code_creator.adopt_creator( maker )
        
    def visit_casting_operator( self ):
        if not declarations.is_fundamental( self.curr_decl.return_type ) \
           and not self.curr_decl.has_const:
            return #only const casting operators can generate implicitly_convertible
        
        if None is self.curr_decl.call_policies:
            self.curr_decl.call_policies = self.__call_policies_resolver( self.curr_decl )
       
        self.__types_db.update( self.curr_decl )
        if not self.curr_decl.parent.is_abstract \
           and not declarations.is_reference( self.curr_decl.return_type ):
            maker = code_creators.casting_operator_t( operator=self.curr_decl )
            self.__module_body.adopt_creator( maker )            
        #what to do if class is abstract
        if self.curr_decl.access_type == ACCESS_TYPES.PUBLIC:
            maker = code_creators.casting_member_operator_t( operator=self.curr_decl )
            self.curr_code_creator.adopt_creator( maker )
            
    def visit_free_function( self ):
        self.__types_db.update( self.curr_decl )
        maker = code_creators.free_function_t( function=self.curr_decl )
        if None is self.curr_decl.call_policies:
            self.curr_decl.call_policies = self.__call_policies_resolver( self.curr_decl )        
        self.curr_code_creator.adopt_creator( maker )
    
    def visit_free_operator( self ):
        self.__types_db.update( self.curr_decl )
        self.__free_operators.append( self.curr_decl )

    def visit_class_declaration(self ):
        pass

    def visit_class(self ):
        assert isinstance( self.curr_decl, declarations.class_t )
        temp_curr_decl = self.curr_decl        
        temp_curr_parent = self.curr_code_creator       
        exportable_members = self._exportable_class_members(self.curr_decl)

        wrapper = None
        class_inst = code_creators.class_t( class_inst=self.curr_decl )

        if self._is_wrapper_needed( self.curr_decl, exportable_members ):
            wrapper = code_creators.class_wrapper_t( declaration=self.curr_decl
                                                     , class_creator=class_inst )
            class_inst.wrapper = wrapper
            #insert wrapper before module body 
            if isinstance( self.curr_decl.parent, declarations.class_t ):
                #we deal with internal class
                self.curr_code_creator.wrapper.adopt_creator( wrapper )
            else:
                self.__extmodule.adopt_declaration_creator( wrapper )
            if declarations.has_trivial_copy( self.curr_decl ):
                #I don't know but sometimes boost.python requieres
                #to construct wrapper from wrapped classe
                if not self.curr_decl.noncopyable:
                    copy_constr = code_creators.copy_constructor_wrapper_t( class_inst=self.curr_decl )
                    wrapper.adopt_creator( copy_constr )    
                null_constr = declarations.find_trivial_constructor(self.curr_decl)
                if null_constr and null_constr.is_artificial:
                    #this constructor is not going to be exposed
                    tcons = code_creators.null_constructor_wrapper_t( class_inst=self.curr_decl )
                    wrapper.adopt_creator( tcons )                                                  
                    
        self.curr_code_creator.adopt_creator( class_inst )
        self.curr_code_creator = class_inst
        for decl in exportable_members:
            self.curr_decl = decl
            declarations.apply_visitor( self, decl )

        for redefined_func in self.redefined_funcs( temp_curr_decl ):
            if isinstance( redefined_func, declarations.operator_t ):
                continue
            self.curr_decl = redefined_func
            declarations.apply_visitor( self, redefined_func )

        #all static_methods_t should be moved to the end
        #better approach is to move them after last def of relevant function
        static_methods = filter( lambda creator: isinstance( creator, code_creators.static_method_t )
                                 , class_inst.creators )
        for static_method in static_methods:
            class_inst.remove_creator( static_method )
            class_inst.adopt_creator( static_method )
        
        self.curr_decl = temp_curr_decl        
        self.curr_code_creator = temp_curr_parent
        
    def visit_enumeration(self):
        assert isinstance( self.curr_decl, declarations.enumeration_t )
        maker = None
        if self.curr_decl.name:
            maker = code_creators.enum_t( enum=self.curr_decl )
        else:
            maker = code_creators.unnamed_enum_t( unnamed_enum=self.curr_decl )
        self.curr_code_creator.adopt_creator( maker )
        
    def visit_namespace(self):
        pass

    def visit_typedef(self):
        pass

    def _register_array_1( self, array_type ):
        data = ( array_type.decl_string, declarations.array_size( array_type ) )
        if data in self.__array_1_registered:
            return False
        else:
            self.__array_1_registered.add( data )
            return True    
    
    def visit_variable(self):
        self.__types_db.update( self.curr_decl )
        
        if declarations.is_array( self.curr_decl.type ):
            if not self.__cr_array_1_included:
                self.__extmodule.add_system_header( code_repository.array_1.file_name )
                self.__extmodule.adopt_creator( code_creators.include_t( code_repository.array_1.file_name )
                                                , self.__extmodule.first_include_index() + 1)
                self.__cr_array_1_included = True
            if self._register_array_1( self.curr_decl.type ):
                array_1_registrator = code_creators.array_1_registrator_t( array_type=self.curr_decl.type )
                self.curr_code_creator.adopt_creator( array_1_registrator )
        
        if isinstance( self.curr_decl.parent, declarations.namespace_t ):
            maker = None
            wrapper = None
            if declarations.is_array( self.curr_decl.type ):
                wrapper = code_creators.array_gv_wrapper_t( variable=self.curr_decl )
                maker = code_creators.array_gv_t( variable=self.curr_decl, wrapper=wrapper )
            else:
                maker = code_creators.global_variable_t( variable=self.curr_decl )
            if wrapper:
                self.__extmodule.adopt_declaration_creator( wrapper )
        else:
            maker = None
            wrapper = None
            if self.curr_decl.bits != None:
                wrapper = code_creators.bit_field_wrapper_t( variable=self.curr_decl )
                maker = code_creators.bit_field_t( variable=self.curr_decl, wrapper=wrapper )
            elif declarations.is_array( self.curr_decl.type ):
                wrapper = code_creators.array_mv_wrapper_t( variable=self.curr_decl )
                maker = code_creators.array_mv_t( variable=self.curr_decl, wrapper=wrapper )
            elif declarations.is_pointer( self.curr_decl.type ):
                wrapper = code_creators.member_variable_wrapper_t( variable=self.curr_decl )
                maker = code_creators.member_variable_t( variable=self.curr_decl, wrapper=wrapper )
            elif declarations.is_reference( self.curr_decl.type ):
                if None is self.curr_decl.getter_call_policies:
                    self.curr_decl.getter_call_policies = self.__call_policies_resolver( self.curr_decl, 'get' )
                if None is self.curr_decl.setter_call_policies:
                    self.curr_decl.setter_call_policies = self.__call_policies_resolver( self.curr_decl, 'set' )
                wrapper = code_creators.mem_var_ref_wrapper_t( variable=self.curr_decl )
                maker = code_creators.mem_var_ref_t( variable=self.curr_decl, wrapper=wrapper )                
            else:
                maker = code_creators.member_variable_t( variable=self.curr_decl )                
            if wrapper:
                self.curr_code_creator.wrapper.adopt_creator( wrapper )
        self.curr_code_creator.adopt_creator( maker )            
