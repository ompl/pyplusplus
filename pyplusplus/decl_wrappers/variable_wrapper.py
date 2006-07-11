# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations 
import decl_wrapper

class variable_t(decl_wrapper.decl_wrapper_t, declarations.variable_t):
    def __init__(self, *arguments, **keywords):
        declarations.variable_t.__init__(self, *arguments, **keywords )
        decl_wrapper.decl_wrapper_t.__init__( self )
        self._getter_call_policies = None
        self._setter_call_policies = None
        
    __call_policies_doc__ = \
    """There are usecase, when exporting member variable forces pyplusplus to 
    create accessors functions. Sometime, those functions requires call policies.
    To be more specific: when you export member variable that has reference or
    pointer type, you need to tell boost.python library how to manage object 
    life-time. In all cases, pyplusplus will give reasonable default value. I am 
    sure, that there are use cases, when you need to change it. You should use this
    property to change it.
    """
    
    def get_getter_call_policies( self ):
        return self._getter_call_policies
    def set_getter_call_policies( self, call_policies ):
        self._getter_call_policies = call_policies
    getter_call_policies = property( get_getter_call_policies, set_getter_call_policies
                                     , doc=__call_policies_doc__ )

    def get_setter_call_policies( self ):
        return self._setter_call_policies
    def set_setter_call_policies( self, call_policies ):
        self._setter_call_policies = call_policies
    setter_call_policies = property( get_setter_call_policies, set_setter_call_policies
                                     , doc=__call_policies_doc__ )

    def _exportable_impl( self ):
        #if not isinstance( self.parent, declarations.class_t ):
        #    return ''
        if not self.name:
            return "pyplusplus can not expose unnamed variables"
        if self.bits == 0 and self.name == "":
            return "pyplusplus can not expose alignement bit."
        type_ = declarations.remove_alias( self.type )
        type_ = declarations.remove_const( type_ )
        if declarations.is_pointer( type_ ):
            if self.type_qualifiers.has_static:
                return "pyplusplus can not expose static pointer member variables. This could be changed in future."
            if declarations.is_fundamental( type_.base ):
                return "pyplusplus can not expose pointer to fundamental member variables. This could be changed in future."
            
            units = declarations.decompose_type( type_ )
            ptr2functions = filter( lambda unit: isinstance( unit, declarations.calldef_type_t )
                                    , units )
            if ptr2functions:
                return "boost.python can not expose variables, which are pointer to function." \
                       + " See http://www.boost.org/libs/python/doc/v2/faq.html#funcptr for more information."
        type_ = declarations.remove_pointer( type_ )
        if declarations.class_traits.is_my_case( type_ ):
            cls = declarations.class_traits.get_declaration( type_ )
            if not cls.name:
                return "pyplusplus can not expose variables of with unnamed type."
        return ''
    