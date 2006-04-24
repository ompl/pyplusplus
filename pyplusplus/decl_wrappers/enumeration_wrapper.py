# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations 
import decl_wrapper

class enumeration_t(decl_wrapper.decl_wrapper_t, declarations.enumeration_t):
    def __init__(self, *arguments, **keywords):
        declarations.enumeration_t.__init__(self, *arguments, **keywords )
        decl_wrapper.decl_wrapper_t.__init__( self )
        
        self._value_aliases = {}
        #by default export all values
        self._export_values = None

    def _get_value_aliases(self):
        return self._value_aliases
    def _set_value_aliases(self, value_aliases):
        self._value_aliases = value_aliases
    value_aliases = property( _get_value_aliases, _set_value_aliases )

    def _get_export_values(self):
        if self._export_values is None:
            return self.values.keys()
        else:
            return self._export_values
    def _set_export_values(self, export_values):
        self._export_values = export_values
    export_values = property( _get_export_values, _set_export_values )
