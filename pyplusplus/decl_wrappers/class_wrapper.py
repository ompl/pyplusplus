# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import user_text
import decl_wrapper
import scopedef_wrapper
from pygccxml import declarations
import indexing_suite1 as isuite1
import indexing_suite2 as isuite2

class class_common_impl_details_t( object ):
    def __init__(self):
        object.__init__( self )
        self._always_expose_using_scope = False
        self._indexing_suite = None
        self._equality_comparable = None
        self._less_than_comparable = None
        self._isuite_version = 1

    def _get_indexing_suite_version( self ):
        return self._isuite_version
    def _set_indexing_suite_version( self, version ):
        assert version in ( 1, 2 )
        if self._isuite_version != version:
            self._isuite_version = version
            self._indexing_suite = None
    indexing_suite_version = property( _get_indexing_suite_version, _set_indexing_suite_version )

    def _get_always_expose_using_scope( self ):
        #I am almost sure this logic should be moved to code_creators
        if isinstance( self.indexing_suite, isuite2.indexing_suite2_t ) \
           and ( self.indexing_suite.disable_methods or self.indexing_suite.disabled_methods_groups ):
            return True
        return self._always_expose_using_scope
    def _set_always_expose_using_scope( self, value ):
        self._always_expose_using_scope = value
    always_expose_using_scope = property( _get_always_expose_using_scope, _set_always_expose_using_scope )

    def _get_indexing_suite( self ):
        if self._indexing_suite is None:
            for container_traits in declarations.all_container_traits:
                if container_traits.is_my_case( self ):
                    if self._isuite_version == 1:
                        self._indexing_suite = isuite1.indexing_suite1_t( self, container_traits )
                    else:
                        self._indexing_suite = isuite2.indexing_suite2_t( self, container_traits )
                    break
        return self._indexing_suite
    indexing_suite = property( _get_indexing_suite )

    def _get_equality_comparable( self ):
        if None is self._equality_comparable:
            self._equality_comparable = declarations.has_public_equal( self )
        return self._equality_comparable

    def _set_equality_comparable( self, value ):
        self._equality_comparable = value

    equality_comparable = property( _get_equality_comparable, _set_equality_comparable )

    def _get_less_than_comparable( self ):
        if None is self._less_than_comparable:
            self._less_than_comparable = declarations.has_public_less( self )
        return self._less_than_comparable

    def _set_less_than_comparable( self, value ):
        self._less_than_comparable = value

    less_than_comparable = property( _get_less_than_comparable, _set_less_than_comparable )


#this will only be exported if indexing suite is not None and only when needed
class class_declaration_t( class_common_impl_details_t
                           , decl_wrapper.decl_wrapper_t
                           , declarations.class_declaration_t ):
    def __init__(self, *arguments, **keywords):
        class_common_impl_details_t.__init__( self )
        declarations.class_declaration_t.__init__(self, *arguments, **keywords )
        decl_wrapper.decl_wrapper_t.__init__( self )

class class_t( class_common_impl_details_t
               , scopedef_wrapper.scopedef_t
               , declarations.class_t):
    def __init__(self, *arguments, **keywords):
        class_common_impl_details_t.__init__( self )
        declarations.class_t.__init__(self, *arguments, **keywords )
        scopedef_wrapper.scopedef_t.__init__( self )

        self._redefine_operators = False
        self._held_type = None
        self._noncopyable = None
        self._wrapper_alias = self._generate_valid_name() + "_wrapper"
        self._registration_code = []
        self._declaration_code = []
        self._wrapper_code = []
        self._null_constructor_body = ''
        self._copy_constructor_body = ''

    def _get_redefine_operators( self ):
        return self._redefine_operators
    def _set_redefine_operators( self, new_value ):
        self._redefine_operators = new_value
    redefine_operators = property( _get_redefine_operators, _set_redefine_operators )

    def _get_held_type(self):
        return self._held_type
    def _set_held_type(self, held_type):
        self._held_type = held_type
    held_type = property( _get_held_type, _set_held_type )

    def _get_noncopyable(self):
        if self._noncopyable is None:
            self._noncopyable = declarations.is_noncopyable( self )
        return self._noncopyable
    def _set_noncopyable(self, noncopyable):
        self._noncopyable= noncopyable
    noncopyable = property( _get_noncopyable, _set_noncopyable)

    def _get_wrapper_alias( self ):
        return self._wrapper_alias
    def _set_wrapper_alias( self, walias ):
        self._wrapper_alias = walias
    wrapper_alias = property( _get_wrapper_alias, _set_wrapper_alias )

    def has_wrapper( self ):
        for decl in self.declarations:
            if decl.has_wrapper():
                return True
        return False

    def _finalize_impl( self, error_behavior ):
        for decl in self.declarations:
            decl.finalize( error_behavior )

    @property
    def declaration_code( self ):
        """
        List of strings, that contains valid C++ code, that will be added to
        the class registration section
        """
        return self._declaration_code

    @property
    def registration_code( self ):
        """
        List of strings, that contains valid C++ code, that will be added to
        the class registration section
        """
        return self._registration_code

    @property
    def wrapper_code( self ):
        """
        List of strings, that contains valid C++ code, that will be added to
        the class wrapper.
        """
        return self._wrapper_code

    def _get_null_constructor_body(self):
        return self._null_constructor_body
    def _set_null_constructor_body(self, body):
        self._null_constructor_body = body
    null_constructor_body = property( _get_null_constructor_body, _set_null_constructor_body )

    def _get_copy_constructor_body(self):
        return self._copy_constructor_body
    def _set_copy_constructor_body(self, body):
        self._copy_constructor_body = body
    copy_constructor_body = property( _get_copy_constructor_body, _set_copy_constructor_body )

    def add_declaration_code( self, code ):
        self.declaration_code.append( user_text.user_text_t( code ) )

    def add_registration_code( self, code, works_on_instance=True ):
        """works_on_instance: If true, the custom code can be applied directly to obj inst.
           Ex: ObjInst."CustomCode"
        """
        self.registration_code.append( user_text.class_user_text_t( code, works_on_instance ) )
    #preserving backward computability
    add_code = add_registration_code

    def add_wrapper_code( self, code ):
        self.wrapper_code.append( user_text.user_text_t( code ) )

    def set_constructors_body( self, body ):
        """Sets the body for all constructors"""
        self.constructors().body = body
        self.null_constructor_body = body
        self.copy_constructor_body = body

    def _exportable_impl( self ):
        if not self.name:
            return 'Py++ can not expose unnamed classes.'
            #it is possible to do so, but not for unnamed classes defined under namespace.
        if isinstance( self.parent, declarations.namespace_t ):
            return ''
        if not self in self.parent.public_members:
            return 'Py++ can not expose private class.'
        return ''