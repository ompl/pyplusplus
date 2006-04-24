# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import decl_wrapper
from pygccxml import declarations

##May be in future I will enable this functionality again, right now it seems
##that this is useless
##def is_finalizable(self):
    ##if not self.wrapper:
        ##return False
    ##return self.declaration.virtuality != declarations.VIRTUALITY_TYPES.PURE_VIRTUAL

class calldef_t(decl_wrapper.decl_wrapper_t):
    def __init__(self, *arguments, **keywords):
        decl_wrapper.decl_wrapper_t.__init__( self, *arguments, **keywords )
    
        self._call_policies = None
        self._use_keywords = True
        self._use_default_arguments = True
        self._create_with_signature = False 

    def get_call_policies(self):
        return self._call_policies
    def set_call_policies(self, call_policies):
        self._call_policies = call_policies
    call_policies = property( get_call_policies, set_call_policies )

    def _get_use_keywords(self):
        return self._use_keywords
    def _set_use_keywords(self, use_keywords):
        self._use_keywords = use_keywords
    use_keywords = property( _get_use_keywords, _set_use_keywords )

    def _get_create_with_signature(self):
        return self._create_with_signature
    def _set_create_with_signature(self, create_with_signature):
        self._create_with_signature = create_with_signature
    create_with_signature = property( _get_create_with_signature, _set_create_with_signature)

    def _get_use_default_arguments(self):
        return self._use_default_arguments
    def _set_use_default_arguments(self, use_default_arguments):
        self._use_default_arguments = use_default_arguments
    use_default_arguments = property( _get_use_default_arguments, _set_use_default_arguments )
        
    def has_wrapper( self ):
        if not isinstance( self, declarations.member_calldef_t ):
            return False
        elif self.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            return True
        elif self.access_type == declarations.ACCESS_TYPES.PROTECTED:
            return True
        else:
            return False

    def _finalize_impl( self, error_behavior ):
        if not isinstance( self, declarations.member_calldef_t ):
            pass
        elif self.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            raise RuntimeError( "In order to expose pure virtual function, you should allow to pyplusplus to create wrapper." )
        elif self.access_type == declarations.ACCESS_TYPES.PROTECTED:
            self.ignore = True
        else:
            pass

    def readme( self ):
        def suspicious_type( type_ ):
            if not declarations.is_reference( self.return_type ):
                return False
            type_no_ref = declarations.remove_reference( type_ )
            return not declarations.is_const( type_no_ref ) \
                   and declarations.is_fundamental( type_no_ref )
        msg = []
        if suspicious_type( self.return_type ) and None is self.call_policies:
            msg.append( 'WARNING: Function "%s" returns non-const reference to C++ fundamental type - value can not be modified from Python.' % str( self ) )
        for index, arg in enumerate( self.arguments ):
            if suspicious_type( arg.type ):
                tmpl = 'WARNING: Function "%s" takes as argument (name=%s, pos=%d ) ' \
                       + 'non-const reference to C++ fundamental type - ' \
                       + 'function could not be called from Python.'
                msg.append( tmpl % ( str( self ), arg.name, index ) ) 
        return msg
                
class member_function_t( declarations.member_function_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.member_function_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class constructor_t( declarations.constructor_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.constructor_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class destructor_t( declarations.destructor_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.destructor_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )
      
class member_operator_t( declarations.member_operator_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.member_operator_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )
            
    def _get_alias( self):
        alias = super( member_operator_t, self )._get_alias()
        if alias == self.name:
            if self.symbol == '()':
                alias = '__call__'
            elif self.symbol == '[]':
                alias = '__getitem__'
            else:
                pass
        return alias
    alias = property( _get_alias, decl_wrapper.decl_wrapper_t._set_alias )

class casting_operator_t( declarations.casting_operator_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.casting_operator_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class free_function_t( declarations.free_function_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.free_function_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )

class free_operator_t( declarations.free_operator_t, calldef_t ):
    def __init__(self, *arguments, **keywords):
        declarations.free_operator_t.__init__( self, *arguments, **keywords )
        calldef_t.__init__( self )
