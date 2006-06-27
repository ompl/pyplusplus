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

class indexing_suite2_t( object ):
    def __init__( self, container_class, container_traits ):
        object.__init__( self )
        self.__call_policies = None
        self.__container_class = container_class
        self.__container_traits = container_traits
        self.__disable_len = None 
        self.__disable_slices = None  
        self.__disable_search = None
        self.__disable_reorder = None  
        self.__disable_extend = None  
        self.__disable_insert = None
            
    def _get_container_class( self ):
        return self.__container_class
    container_class = property( _get_container_class )

    def _get_container_traits( self ):
        return self._get_container_traits()
    container_traits = property( _get_container_traits )
    
    def _get_call_policies( self ):
        #TODO find out call policies
        return self.__call_policies
    def _set_call_policies( self, call_policies ):
        self.__call_policies = call_policies
    call_policies = property( _get_call_policies, _set_call_policies )

    def _get_disable_len( self ):
        return self.__disable_len
    def _set_disable_len( self, value ):
        self.__disable_len = value
    disable_len = property( _get_disable_len, _set_disable_len )
    
    def _get_disable_slices( self ):
        return self.__disable_slices
    def _set_disable_slices( self, value ):
        self.__disable_slices = value
    disable_slices = property( _get_disable_slices, _set_disable_slices )
    
    def _get_disable_search( self ): #need operator==
        if None is self.__disable_search:
            value_type = self.container_traits.value_type( self.container_class )
            if not declarations.has_public_equal( value_type ):
                self.__disable_search = True
        return self.__disable_search
    def _set_disable_search( self, value ):
        self.__disable_search = value
    disable_search = property( _get_disable_search, _set_disable_search )
    
    def _get_disable_reorder( self ): #need operator<
        if None is self.__disable_reorder:
            value_type = self.container_traits.value_type( self.container_class )
            if not declarations.has_public_less( value_type ):
                self.__disable_reorder = True
        return self.__disable_reorder
    def _set_disable_reorder( self, value ):
        self.__disable_reorder = value
    disable_reorder = property( _get_disable_reorder, _set_disable_reorder )

    def _get_disable_extend( self ):
        return self.__disable_extend
    def _set_disable_extend( self, value ):
        self.__disable_extend = value
    disable_extend = property( _get_disable_extend, _set_disable_extend )

    def _get_disable_insert( self ):
        return self.__disable_insert
    def _set_disable_insert( self, value ):
        self.__disable_insert = value
    disable_insert = property( _get_disable_insert, _set_disable_insert )
