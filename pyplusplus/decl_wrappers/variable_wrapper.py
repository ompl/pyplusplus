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
        self._call_policies = None
        
    def _get_call_policies( self ):
        return self._call_policies
    def _set_call_policies( self, call_policies ):
        self._call_policies = call_policies
    
    __call_policies_doc__ = \
    """There are usecase, when exporting member variable forces pyplusplus to 
    create accessors functions. Sometime, those functions requires call policies.
    To be more specific: when you export member variable that has reference or
    pointer type, you need to tell boost.python library how to manage object 
    life-time. In all cases, pyplusplus will give reasonable default value. I am 
    sure, that there are use cases, when you need to change it. You should use this
    property to change it.
    """
    call_policies = property( _get_call_policies, _set_call_policies
                              , doc=__call_policies_doc__ )

    def _exportable_impl( self ):
        if not isinstance( self.parent, declarations.class_t ):
            return ''
        if self.bits == 0 and self.name == "":
            return "pyplusplus can not expose alignement bit."
        type_ = declarations.remove_const( self.type )
        if declarations.is_pointer( type_ ):
            if self.type_qualifiers.has_static:
                return "pyplusplus, right now, can not expose static pointer member variables. This could be changed in future."
            if declarations.is_fundamental( type_.base ):
                return "pyplusplus, right now, can not expose pointer to fundamental member variables. This could be changed in future."
        return ''
    