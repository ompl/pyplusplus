# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations

#NoProxy
#By default indexed elements have Python reference semantics and are returned by 
#proxy. This can be disabled by supplying true in the NoProxy template parameter.
#When we want to disable is:
#1. We deal with immutable objects:
#   1. fundamental types
#   2. enum type
#   3. std::[w]string
#   4. std::complex
#   5. shared_ptr

class indexing_suite1_t( object ):
    def __init__( self, container_class, container_traits, no_proxy=None, derived_policies=None ):
        object.__init__( self )
        self.__no_proxy = no_proxy
        self.__derived_policies = None
        self.__container_class = container_class
        self.__container_traits = container_traits
        
    def _get_container_class( self ):
        return self.__container_class
    container_class = property( _get_container_class )
    
    def value_type(self):
        return self.__container_traits.value_type( self.container_class )
    
    def _get_no_proxy( self ):
        if self.__no_proxy is None:
            value_type = self.value_type()
            if declarations.is_fundamental( value_type ) \
               or declarations.is_enum( value_type )    \
               or declarations.is_std_string( value_type ) \
               or declarations.is_std_wstring( value_type ) \
               or declarations.smart_pointer_traits.is_smart_pointer( value_type ):
                self.__no_proxy = True
            else:
                self.__no_proxy = False
        return self.__no_proxy
            
    def _set_no_proxy( self, no_proxy ):
        self.__no_proxy = no_proxy
        
    no_proxy = property( _get_no_proxy, _set_no_proxy )
            
    def _get_derived_policies( self ):
        return self.__derived_policies
    def _set_derived_policies( self, derived_policies ):
        self.__derived_policies = derived_policies
    derived_policies = property( _get_derived_policies, _set_derived_policies )
    