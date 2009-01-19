# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import algorithm
import code_creator
import ctypes_formatter
import declaration_based
from pygccxml import declarations

#TODO: don't hide public member variables
#TODO: how _fields_ should be defined in a class hierarchy
#TODO: fix 64bit issue with calculating vtable pointer size


class fields_definition_t(code_creator.code_creator_t, declaration_based.declaration_based_t):
    def __init__( self, class_ ):
        code_creator.code_creator_t.__init__(self)
        declaration_based.declaration_based_t.__init__( self, class_ )

    def has_unnamed_type( self, var ):
        type_ = declarations.remove_pointer( var.type )        
        #~ type_ = declarations.remove_declarated( type_ )
        if declarations.class_traits.is_my_case( type_ ):
            cls = declarations.class_traits.get_declaration( type_ )
            return bool( not cls.name )
        else:
            return False

    def _create_impl(self):
        result = []        
        anonymous_vars = self.declaration.vars( self.has_unnamed_type, recursive=False, allow_empty=True )
        if anonymous_vars:
            formated_vars = []
            for var in anonymous_vars:
                formated_vars.append( '"%s"' % var.alias )
            result.append( '%(complete_py_name)s._anonymous_ = [%(vars)s]' 
                           % dict( complete_py_name=self.complete_py_name
                                   , vars=', '.join( formated_vars ) ) )
                                   
        result.append( '%(complete_py_name)s._fields_ = [ #class %(decl_identifier)s'
                       % dict( complete_py_name=self.complete_py_name
                               , decl_identifier=self.decl_identifier) )
        if self.declaration.has_vtable:
            result.append( self.indent( '("_vtable_", ctypes.POINTER(ctypes.c_void_p)),' ) )

        vars = self.declaration.vars( allow_empty=True, recursive=False )
        if not vars:
            result.append( self.indent( '("__empty__", ctypes.c_char * 4)' ) )
        else:
            vars = vars.to_list()
            vars.sort( key=lambda d: d.location.line )
            for v in vars:
                result.append( self.indent( '("%(name)s", %(type)s),'
                               % dict( name=v.alias
                                       ,type=ctypes_formatter.as_ctype( v.type ) ) ) )
        result.append( ']' )
        return os.linesep.join( result )

    def _get_system_files_impl( self ):
        return []
