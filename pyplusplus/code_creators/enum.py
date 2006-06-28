# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import algorithm
import declaration_based

class enum_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code that expose C++ enum
    """
    def __init__(self, enum, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , parent=parent
                                                        , declaration=enum)
        self.works_on_instance = False

    def _get_value_aliases(self):
        return self.declaration.value_aliases
    def _set_value_aliases(self, value_aliases):
        self.declaration.value_aliases = value_aliases
    value_aliases = property( _get_value_aliases, _set_value_aliases )

    def _get_export_values(self):
        return self.declaration.export_values
    def _set_export_values(self, export_values):
        self.declaration.export_values = export_values
    export_values = property( _get_export_values, _set_export_values )

    def _generate_value_code(self, value_name):
        #in C++ you can't write namespace::enum::value, you should write namespace::value
        full_name = self.declaration.parent.decl_string
        return '.value("%(alias)s", %(name)s)' \
               % { 'alias' : self.value_aliases.get( value_name, value_name )
                    , 'name' : algorithm.create_identifier( self, full_name + '::' + value_name ) }
    
    def _create_impl(self):
        bpl_enum = '%(bpl::enum_)s<%(name)s>("%(alias)s")' \
                   % { 'bpl::enum_' : algorithm.create_identifier( self, '::boost::python::enum_' )
                       , 'name' : algorithm.create_identifier( self, self.declaration.decl_string )
                       , 'alias' : self.alias }
        values = []                
        for value_name in self.export_values:
            values.append( self._generate_value_code( value_name ) )
            
        if self.export_values:
            values.append( '.export_values()' )
            
        for name in self.declaration.values.keys():
            if name not in self.export_values:
                values.append( self._generate_value_code( name ) )

        values.append( ';' )
        
        values = self.indent( os.linesep.join( values ) )
        return bpl_enum + os.linesep + values
