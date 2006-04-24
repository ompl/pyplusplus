# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations
from pyplusplus import code_creators
import class_organizer
import call_policies_resolver 
import types_database
from pyplusplus import code_repository
from sets import Set as set

#TODO: don't export functions that returns non const pointer to fundamental types
#TODO: add print decl_wrapper.readme messages

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
                  , target_configuration=None ):
        """Constructor.

        @param decls: Declarations that should be exposed in the final module.
        @param module_name: The name of the final module.
        @param boost_python_ns_name: The alias for the boost::python namespace.
        @param create_castinig_constructor: ...todo...
        @param call_policies_resolver_: Callable that takes one declaration (calldef_t) as input and returns a call policy object which should be used for this declaration.
        @param types_db: ...todo...
        @param target_configuration: A target configuration object can be used to customize the generated source code to a particular compiler or a particular version of Boost.Python.
        @type decls: list of declaration_t
        @type module_name: str
        @type boost_python_ns_name: str
        @type create_castinig_constructor: bool
        @type call_policies_resolver_: callable
        @type types_db: L{types_database_t<types_database.types_database_t>}
        @type target_configuration: L{target_configuration_t<code_creators.target_configuration_t>}
        """
        declarations.decl_visitor_t.__init__(self)        

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
        self.__extmodule.adopt_creator( code_creators.include_t( header="boost/python.hpp" ) )
        self.__create_castinig_constructor = create_castinig_constructor
        if boost_python_ns_name:
            bp_ns_alias = code_creators.namespace_alias_t( alias=boost_python_ns_name
                                                           , full_namespace_name='::boost::python' ) 
            self.__extmodule.adopt_creator( bp_ns_alias )
        
        self.__module_body = code_creators.module_body_t( name=module_name )
        self.__extmodule.adopt_creator( self.__module_body )        
        
        decls = declarations.make_flatten( decls )
        self.__decls = self._filter_decls( self._reorder_decls( self._prepare_decls( decls ) ) )
            
        self.__curr_parent = self.__module_body
        self.__curr_decl = None
        self.__cr_array_1_included = False
        self.__array_1_registered = set() #(type.decl_string,size)
        self.__free_operators = []
        
    def _prepare_decls( self, decls ):
        #leave only declarations defined under namespace, but remove namespaces
        decls = filter( lambda x: not isinstance( x, declarations.namespace_t ) \
                                   and isinstance( x.parent, declarations.namespace_t )
                         , decls )
        #leave only decls that should be exported
        decls = filter( lambda x: not x.ignore, decls )
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
        for inst in ordered:
            if isinstance( inst, declarations.variable_t ):
                variables.append( inst )
            elif isinstance( inst, declarations.enumeration_t ):
                enums.append( inst )
            else:
                others.append( inst )
        new_ordered = enums
        new_ordered.extend( others )
        new_ordered.extend( variables )
        return new_ordered #

    def _is_calldef_exposable(self, declaration):
        #see http://www.boost.org/libs/python/doc/v2/faq.html#funcptr
        if len( declaration.arguments ) > 10:
            return False #boost.tuple can not contain more than 10 args
        all_types = [ arg.type for arg in declaration.arguments ]
        all_types.append( declaration.return_type )
        for some_type in all_types:
            units = declarations.decompose_type( some_type )
            ptr2functions = filter( lambda unit: isinstance( unit, declarations.calldef_type_t )
                                    , units )
            if ptr2functions:
                return False
            #Function that take as agrument some instance of non public class
            #will not be exported. Same to the return variable
            if isinstance( units[-1], declarations.declarated_t ):
                dtype = units[-1]
                if isinstance( dtype.declaration.parent, declarations.class_t ):
                    if dtype.declaration not in dtype.declaration.parent.public_members:
                        return False
                    
        if isinstance( declaration, declarations.operator_t ):
            if isinstance( declaration, declarations.casting_operator_t ):
                return True
            if isinstance( declaration, declarations.member_operator_t ) \
               and declaration.symbol in ( '()', '[]' ):
                return True
            if not code_creators.operator_t.supported.is_supported( declaration ):
                #see http://www.boost.org/libs/python/doc/v2/operators.html#introduction
                return False
        if isinstance( declaration, declarations.constructor_t ) \
           and declaration.is_artificial:
            return False
        return True
    
    def _exportable_class_members( self, class_decl ):
        assert isinstance( class_decl, declarations.class_t )
        members = []
        for member in class_decl.public_members:
            if isinstance( member, declarations.variable_t ) :
                if member.bits == 0 and member.name == "":
                    continue #alignement bit
                type_ = declarations.remove_const( member.type )
                if declarations.is_pointer( type_ ) \
                   and member.type_qualifiers.has_static:
                    continue #right now I don't know what code should be generated in this case
            members.append( member )
        #protected and private virtual functions that not overridable and not pure
        #virtual should not be exported
        for member in class_decl.protected_members:
            if not isinstance( member, declarations.calldef_t ):
                continue
            if member.virtuality != declarations.VIRTUALITY_TYPES.VIRTUAL:
                members.append( member )
            if self._is_overridable( member ):
                members.append( member )
        
        vfunction_selector = lambda member: isinstance( member, declarations.member_function_t ) \
                                            and member.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL 
        members.extend( filter( vfunction_selector, class_decl.private_members ) )
        #now lets filter out none public operators: pyplusplus does not support them right now
        members = filter( lambda decl: not isinstance( decl, declarations.member_operator_t )
                                       or decl.access_type == declarations.ACCESS_TYPES.PUBLIC 
                          , members )
        #-#if declarations.has_destructor( class_decl ) \
        #-#   and not declarations.has_public_destructor( class_decl ):
            #remove artificial constructors
        members = filter( lambda decl: not isinstance( decl, declarations.constructor_t )
                                       or not decl.is_artificial
                          , members )
        members = filter( lambda member: not member.ignore, members )
        ordered_members = self._reorder_decls( members )
        return ordered_members
    
    def _does_class_have_smth_to_export(self, exportable_members ):
        return bool( self._filter_decls( self._reorder_decls( exportable_members ) ) )
    
    def _is_public_class( self, class_decl ):
        if isinstance( class_decl.parent, declarations.namespace_t ):
            return True
        return class_decl in class_decl.parent.public_members

    def _is_constructor_of_abstract_class( self, decl ):
        assert isinstance( decl, declarations.constructor_t )
        return decl.parent.is_abstract
        
    def _filter_decls( self, decls ):
        # Filter out artificial (compiler created) types unless they are classes
        # See: http://public.kitware.com/pipermail/gccxml/2004-October/000486.html
        decls = filter( lambda x: not (x.is_artificial and 
                                       not (isinstance(x, ( declarations.class_t, declarations.enumeration_t))))
                       , decls )
        # Filter out internal compiler methods        
        decls = filter( lambda x: not x.name.startswith( '__' ), decls )
        decls = filter( lambda x: x.location.file_name != "<internal>", decls )
        # Filter out type defs
        decls = filter( lambda x: not isinstance( x, declarations.typedef_t ), decls )
        # Filter out non-exposable calls
        decls = filter( lambda x: not isinstance( x, declarations.calldef_t) 
                                  or self._is_calldef_exposable(x)
                        , decls )
        decls = filter( lambda x: not isinstance( x, declarations.class_t)
                                  or self._is_public_class( x )
                        , decls )
        return decls

    def _is_wrapper_needed(self, exportable_members):
        if isinstance( self.__curr_decl, declarations.class_t ) \
           and self.__curr_decl.wrapper_user_code:
            return True
        elif isinstance( self.__curr_parent, declarations.class_t ) \
           and self.__curr_parent.wrapper_user_code:
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
                if declarations.is_array( member.type ):
                    return True
            if isinstance( member, declarations.class_t ):
                return True
            if isinstance( member, declarations.member_calldef_t ):
                if member.access_type != declarations.ACCESS_TYPES.PUBLIC:
                    return True
                if self._is_overridable( member ):
                    return True
        return False
    
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
            self.__curr_decl = decl
            declarations.apply_visitor( self, decl )
        for operator in self.__free_operators:
            self._adopt_free_operator( operator )
        self._treat_smart_pointers()
        for creator in code_creators.make_flatten( self.__extmodule ):
            creator.target_configuration = self.__target_configuration
        #last action.
        self._append_user_code()
        return self.__extmodule

    def _create_includes(self):
        for fn in declarations.declaration_files( self.__decls ):
            include = code_creators.include_t( header=fn )
            self.__extmodule.adopt_include(include)

    def _is_overridable( self, decl ):
        #virtual functions that returns const reference to something
        #could not be overriden by Python. The reason is simple: 
        #in boost::python::override::operator(...) result of marshaling 
        #(Python 2 C++) is saved on stack, after functions returns the result
        #will be reference to no where - access violetion.
        #For example see temporal variable tester
        assert isinstance( decl, declarations.member_calldef_t )
        if decl.virtuality == declarations.VIRTUALITY_TYPES.VIRTUAL \
           and decl.access_type == declarations.ACCESS_TYPES.PROTECTED \
           and declarations.is_reference( decl.return_type ):
            return True
        if decl.virtuality == declarations.VIRTUALITY_TYPES.VIRTUAL \
           and declarations.is_reference( decl.return_type ):
            return False        
        if decl.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            return True
        if decl.access_type != declarations.ACCESS_TYPES.PUBLIC:
            return True
        if declarations.is_reference( decl.return_type ):
            return False
        return decl.virtuality != declarations.VIRTUALITY_TYPES.NOT_VIRTUAL \
               or decl in decl.parent.protected_members 
        
    def visit_member_function( self ):
        if self.__curr_decl.ignore:
            return
        if self.__curr_decl.name == 'invert_sign':
            i = 0
        fwrapper = None
        self.__types_db.update( self.__curr_decl )
        access_level = self.__curr_decl.parent.find_out_member_access_type( self.__curr_decl )
        if self._is_overridable( self.__curr_decl ) or access_level == declarations.ACCESS_TYPES.PROTECTED:
            class_wrapper = self.__curr_parent.wrapper
            fwrapper = code_creators.function_wrapper_t( function=self.__curr_decl )
            class_wrapper.adopt_creator( fwrapper )
            if access_level == declarations.ACCESS_TYPES.PRIVATE:
                return 
        maker = code_creators.function_t( function=self.__curr_decl, wrapper=fwrapper )
        if None is maker.call_policies:
            maker.call_policies = self.__call_policies_resolver( self.__curr_decl )
        self.__curr_parent.adopt_creator( maker )
        if self.__curr_decl.has_static:
            #static_method should be created only once.
            found = filter( lambda creator: isinstance( creator, code_creators.static_method_t ) 
                                            and creator.declaration.name == self.__curr_decl.name
                                     , self.__curr_parent.creators )
            if not found:
                static_method = code_creators.static_method_t( function=self.__curr_decl
                                                               , function_code_creator=maker )
                self.__curr_parent.adopt_creator( static_method )
        
    def visit_constructor( self ):
        if self.__curr_decl.ignore:
            return

        if self.__curr_decl.is_copy_constructor:
            return             
        self.__types_db.update( self.__curr_decl )
        if not self._is_constructor_of_abstract_class( self.__curr_decl ) \
           and 1 == len( self.__curr_decl.arguments ) \
           and self.__create_castinig_constructor \
           and self.__curr_decl.access_type == declarations.ACCESS_TYPES.PUBLIC:
            maker = code_creators.casting_constructor_t( constructor=self.__curr_decl )
            self.__module_body.adopt_creator( maker )

        cwrapper = None
        exportable_members = self._exportable_class_members(self.__curr_parent.declaration)
        if self._is_wrapper_needed( exportable_members ):
            class_wrapper = self.__curr_parent.wrapper
            cwrapper = code_creators.constructor_wrapper_t( constructor=self.__curr_decl )
            class_wrapper.adopt_creator( cwrapper )
        maker = code_creators.constructor_t( constructor=self.__curr_decl, wrapper=cwrapper )
        if None is maker.call_policies:
            maker.call_policies = self.__call_policies_resolver( self.__curr_decl )
        self.__curr_parent.adopt_creator( maker )
    
    def visit_destructor( self ):
        pass
    
    def visit_member_operator( self ):
        if self.__curr_decl.ignore:
            return

        if self.__curr_decl.symbol in ( '()', '[]' ):
            self.visit_member_function()
        else:
            self.__types_db.update( self.__curr_decl )
            maker = code_creators.operator_t( operator=self.__curr_decl )
            self.__curr_parent.adopt_creator( maker )
        
    def visit_casting_operator( self ):
        if self.__curr_decl.ignore:
            return

        if not declarations.is_fundamental( self.__curr_decl.return_type ) \
           and not self.__curr_decl.has_const:
            return #only const casting operators can generate implicitly_convertible
        
        self.__types_db.update( self.__curr_decl )
        if not self.__curr_decl.parent.is_abstract \
           and not declarations.is_reference( self.__curr_decl.return_type ):
            maker = code_creators.casting_operator_t( operator=self.__curr_decl )
            self.__module_body.adopt_creator( maker )            
        #what to do if class is abstract
        if self.__curr_decl.access_type == declarations.ACCESS_TYPES.PUBLIC:
            maker = code_creators.casting_member_operator_t( operator=self.__curr_decl )
            if None is maker.call_policies:
                maker.call_policies = self.__call_policies_resolver( self.__curr_decl )
            self.__curr_parent.adopt_creator( maker )
            
    def visit_free_function( self ):
        if self.__curr_decl.ignore:
            return
        self.__types_db.update( self.__curr_decl )
        maker = code_creators.function_t( function=self.__curr_decl )
        if None is maker.call_policies:
            maker.call_policies = self.__call_policies_resolver( self.__curr_decl )        
        self.__curr_parent.adopt_creator( maker )
    
    def visit_free_operator( self ):
        if self.__curr_decl.ignore:
            return

        self.__types_db.update( self.__curr_decl )
        self.__free_operators.append( self.__curr_decl )

    def visit_class_declaration(self ):
        pass
        
    def visit_class(self ):
        if self.__curr_decl.ignore:
            return
        assert isinstance( self.__curr_decl, declarations.class_t )
        temp_curr_decl = self.__curr_decl        
        temp_curr_parent = self.__curr_parent       
        exportable_members = self._exportable_class_members(self.__curr_decl)

        wrapper = None
        class_inst = code_creators.class_t( class_inst=self.__curr_decl )

        if self._is_wrapper_needed( exportable_members ):
            wrapper = code_creators.class_wrapper_t( declaration=self.__curr_decl
                                                     , class_creator=class_inst )
            class_inst.wrapper = wrapper
            #insert wrapper before module body 
            if isinstance( self.__curr_decl.parent, declarations.class_t ):
                #we deal with internal class
                self.__curr_parent.wrapper.adopt_creator( wrapper )
            else:
                self.__extmodule.adopt_creator( wrapper, self.__extmodule.creators.index( self.__module_body ) )
            if declarations.has_trivial_copy( self.__curr_decl ):
                #I don't know but sometimes boost.python requieres
                #to construct wrapper from wrapped classe
                if not declarations.is_noncopyable( self.__curr_decl ):
                    scons = code_creators.special_constructor_wrapper_t( class_inst=self.__curr_decl )
                    wrapper.adopt_creator( scons )    
                trivial_constr = declarations.find_trivial_constructor(self.__curr_decl)
                if trivial_constr and trivial_constr.is_artificial:
                    #this constructor is not going to be exposed
                    tcons = code_creators.trivial_constructor_wrapper_t( class_inst=self.__curr_decl )
                    wrapper.adopt_creator( tcons )                                                  
                    
        self.__curr_parent.adopt_creator( class_inst )
        self.__curr_parent = class_inst
        for decl in self._filter_decls( self._reorder_decls( exportable_members ) ):
            self.__curr_decl = decl
            declarations.apply_visitor( self, decl )

        #all static_methods_t should be moved to the end
        #better approach is to move them after last def of relevant function
        static_methods = filter( lambda creator: isinstance( creator, code_creators.static_method_t )
                                 , class_inst.creators )
        for static_method in static_methods:
            class_inst.remove_creator( static_method )
            class_inst.adopt_creator( static_method )
            
        self.__curr_decl = temp_curr_decl        
        self.__curr_parent = temp_curr_parent
        
    def visit_enumeration(self):
        if self.__curr_decl.ignore:
            return

        assert isinstance( self.__curr_decl, declarations.enumeration_t )
        maker = None
        if self.__curr_decl.name:
            maker = code_creators.enum_t( enum=self.__curr_decl )
        else:
            maker = code_creators.unnamed_enum_t( unnamed_enum=self.__curr_decl )
        self.__curr_parent.adopt_creator( maker )
        
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
        if self.__curr_decl.ignore:
            return

        self.__types_db.update( self.__curr_decl )
        
        if declarations.is_array( self.__curr_decl.type ):
            if not self.__cr_array_1_included:
                self.__extmodule.adopt_creator( code_creators.include_t( code_repository.array_1.file_name )
                                                , self.__extmodule.first_include_index() + 1)
                self.__cr_array_1_included = True
            if self._register_array_1( self.__curr_decl.type ):
                array_1_registrator = code_creators.array_1_registrator_t( array_type=self.__curr_decl.type )
                self.__curr_parent.adopt_creator( array_1_registrator )
        
        if isinstance( self.__curr_decl.parent, declarations.namespace_t ):
            maker = None
            wrapper = None
            if declarations.is_array( self.__curr_decl.type ):
                wrapper = code_creators.array_gv_wrapper_t( variable=self.__curr_decl )
                maker = code_creators.array_gv_t( variable=self.__curr_decl, wrapper=wrapper )
            else:
                maker = code_creators.global_variable_t( variable=self.__curr_decl )
            if wrapper:
                self.__extmodule.adopt_creator( wrapper
                                                , self.__extmodule.creators.index( self.__module_body ) )
        else:
            maker = None
            wrapper = None
            if self.__curr_decl.bits != None:
                wrapper = code_creators.bit_field_wrapper_t( variable=self.__curr_decl )
                maker = code_creators.bit_field_t( variable=self.__curr_decl, wrapper=wrapper )
            elif declarations.is_array( self.__curr_decl.type ):
                wrapper = code_creators.array_mv_wrapper_t( variable=self.__curr_decl )
                maker = code_creators.array_mv_t( variable=self.__curr_decl, wrapper=wrapper )
            elif declarations.is_pointer( self.__curr_decl.type ):
                wrapper = code_creators.member_variable_wrapper_t( variable=self.__curr_decl )
                maker = code_creators.member_variable_t( variable=self.__curr_decl, wrapper=wrapper )
            else:
                maker = code_creators.member_variable_t( variable=self.__curr_decl )                
            if wrapper:
                self.__curr_parent.wrapper.adopt_creator( wrapper )
        self.__curr_parent.adopt_creator( maker )            
