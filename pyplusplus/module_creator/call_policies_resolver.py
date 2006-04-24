# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations
from pyplusplus import decl_wrappers
from pyplusplus import code_creators

class resolver_t( object ):
    def __init__( self ):
        object.__init__( self )

    def __call__(self, calldef):
        raise NotImplementedError()

class default_policy_resolver_t(resolver_t):
    def __init__( self ):
        resolver_t.__init__( self )
        self.__const_char_pointer \
            = declarations.pointer_t( declarations.const_t( declarations.char_t() ) )

    def _resolve_by_type( self, some_type ):
        temp_type = declarations.remove_alias( some_type )
        temp_type = declarations.remove_cv( temp_type )
        if isinstance( temp_type, declarations.fundamental_t ) \
           or isinstance( temp_type, declarations.declarated_t ):
            return decl_wrappers.default_call_policies()
        if declarations.is_same( some_type, self.__const_char_pointer ):
            return decl_wrappers.default_call_policies()
        return None

    def __call__(self, calldef):
        assert isinstance( calldef, declarations.calldef_t )
        if not isinstance( calldef, declarations.constructor_t ):
            return self._resolve_by_type( calldef.return_type )
        else:
            for arg in calldef.arguments:
                if not self._resolve_by_type( arg.type ):
                    return None
            return decl_wrappers.default_call_policies()

class void_pointer_resolver_t(resolver_t):
    def __init__( self ):
        resolver_t.__init__( self )

    def __call__( self, calldef ):
        assert isinstance( calldef, declarations.calldef_t )
        if isinstance( calldef, declarations.constructor_t ):
            return None
        return_type = declarations.remove_alias( calldef.return_type )
        void_ptr = declarations.pointer_t( declarations.void_t() )
        const_void_ptr = declarations.pointer_t( declarations.const_t( declarations.void_t() ) )
        if declarations.is_same( return_type, void_ptr ) \
           or declarations.is_same( return_type, const_void_ptr ):
            return decl_wrappers.return_value_policy( decl_wrappers.return_opaque_pointer )
        return None

class return_value_policy_resolver_t(resolver_t):
    def __init__( self ):
        resolver_t.__init__( self )
        self.__const_wchar_pointer \
            = declarations.pointer_t( declarations.const_t( declarations.wchar_t() ) )
        
    def __call__(self, calldef):
        assert isinstance( calldef, declarations.calldef_t )
        if isinstance( calldef, declarations.constructor_t ):
            return None

        return_type = declarations.remove_alias( calldef.return_type )
        if isinstance( return_type, declarations.reference_t ) \
           and isinstance( return_type.base, declarations.const_t ):
            return decl_wrappers.return_value_policy( decl_wrappers.copy_const_reference )

        if declarations.is_same( return_type, self.__const_wchar_pointer ):
            return decl_wrappers.return_value_policy( decl_wrappers.return_by_value )
        
        return None
        
class return_internal_reference_resolver_t( resolver_t ):
    def __init__( self ):    
        resolver_t.__init__( self )
        
    def __call__(self, calldef):
        if not isinstance( calldef, declarations.member_operator_t ):
            return None
        
        if calldef.symbol != '[]':
            return None
            
        return_type = declarations.remove_cv( calldef.return_type )
        if declarations.is_reference( return_type ): 
            return_type = declarations.remove_reference( return_type )
        if declarations.is_fundamental( return_type ) or declarations.is_enum( return_type ):
            if declarations.is_const( calldef.return_type ):
                return decl_wrappers.return_value_policy( decl_wrappers.copy_const_reference )
            else:
                return decl_wrappers.return_value_policy( decl_wrappers.copy_non_const_reference )
        else:
            return decl_wrappers.return_internal_reference()
            
class built_in_resolver_t(resolver_t):
    def __init__( self, config=None):
        resolver_t.__init__( self )
        self.__resolvers = [ default_policy_resolver_t()
                             , return_value_policy_resolver_t() ]        
        assert not config or isinstance( config, code_creators.target_configuration_t )
        if not config or config.boost_python_supports_void_ptr:
            self.__resolvers.append( void_pointer_resolver_t() )
        self.__resolvers.append( return_internal_reference_resolver_t() )

    def __call__( self, calldef ):
        for resolver in self.__resolvers:
            resolved = resolver( calldef )
            if resolved:
                return resolved
        return None
