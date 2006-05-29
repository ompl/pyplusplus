# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import decl_wrapper
import scopedef_wrapper
from pygccxml import declarations
import user_text

class vector_indexing_suite_t( object ):
    def __init__( self, name, container='std::vector', no_proxy=False, derived_policies='' ):
        object.__init__( self )
        self.name = name
        self.container = container
        self.no_proxy = no_proxy
        self.derived_policies = derived_policies
        
class class_declaration_t(decl_wrapper.decl_wrapper_t, declarations.class_declaration_t):
    def __init__(self, *arguments, **keywords):
        declarations.class_declaration_t.__init__(self, *arguments, **keywords )
        decl_wrapper.decl_wrapper_t.__init__( self )

class class_t(scopedef_wrapper.scopedef_t, declarations.class_t):
    def __init__(self, *arguments, **keywords):
        declarations.class_t.__init__(self, *arguments, **keywords )
        scopedef_wrapper.scopedef_t.__init__( self )
        
        self._always_expose_using_scope = False
        self._redefine_operators = False        
        self._held_type = None
        self._noncopyable = None
        self._wrapper_alias = self._generate_valid_name() + "_wrapper"
        self._user_code = []
        self._wrapper_user_code = []
        self._indexing_suites = []
        
    def _get_always_expose_using_scope( self ):
        return self._always_expose_using_scope
    def _set_always_expose_using_scope( self, value ):
        self._always_expose_using_scope = value
    always_expose_using_scope = property( _get_always_expose_using_scope, _set_always_expose_using_scope )

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
    
    def _get_user_code( self ):
        return self._user_code
    def _set_user_code( self, value ):
        self._user_code = value
    user_code = property( _get_user_code, _set_user_code )

    def _get_wrapper_user_code( self ):
        return self._wrapper_user_code
    def _set_wrapper_user_code( self, value ):
        self._wrapper_user_code = value
    wrapper_user_code = property( _get_wrapper_user_code, _set_wrapper_user_code )

    def _get_indexing_suites( self ):
        return self._indexing_suites
    def _set_indexing_suites( self, value ):
        self._indexing_suites = value
    indexing_suites = property( _get_indexing_suites, _set_indexing_suites )
    
    def add_code( self, code, works_on_instance=True ):
        """works_on_instance: If true, the custom code can be applied directly to obj inst.
           Ex: ObjInst."CustomCode"
        """
        self.user_code.append( user_text.class_user_text_t( code, works_on_instance ) )
        
    def add_wrapper_code( self, code ):
        self.wrapper_user_code.append( user_text.user_text_t( code ) )
        
    def _exportable_impl( self ):
        if not self.name:
            return 'pyplusplus can not expose unnamed classes.'
        if isinstance( self.parent, declarations.namespace_t ):
            return ''
        if not self in self.parent.public_members:
            return 'pyplusplus can not expose private class.'
        return ''
