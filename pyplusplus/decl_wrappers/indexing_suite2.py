# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
from pygccxml import declarations

"""
method_len            
method_iter           
method_getitem        
method_getitem_slice  
method_index          
method_contains       
method_count          
method_has_key        
method_setitem        
method_setitem_slice  
method_delitem        
method_delitem_slice  
method_reverse        
method_append         
method_insert         
method_extend         
method_sort

slice_methods = method_getitem_slice | method_setitem_slice | method_delitem_slice
search_methods = method_index | method_contains | method_count | method_has_key
reorder_methods = method_sort | method_reverse
insert_methods = method_append | method_insert | method_extend
"""


class indexing_suite2_t( object ):
    METHODS = ( 'len', 'iter', 'getitem', 'getitem_slice', 'index', 'contains'
                , 'count', 'has_key', 'setitem', 'setitem_slice', 'delitem'
                , 'delitem_slice', 'reverse', 'append', 'insert', 'extend', 'sort' )
    
    METHOD_GROUPS = {
        'slice_methods' : ( 'method_getitem_slice', 'method_setitem_slice', 'method_delitem_slice' )
        , 'search_methods' : ( 'method_index', 'method_contains', 'method_count', 'method_has_key' )
        , 'reorder_methods' : ( 'method_sort', 'method_reverse' )
        , 'insert_methods' : ( 'method_append', 'method_insert', 'method_extend' )
    }
    
    def __init__( self, container_class, container_traits ):
        object.__init__( self )
        self.__call_policies = None
        self.__container_class = container_class
        self.__container_traits = container_traits
        self._disabled_methods = set()
        self._disabled_groups = set()
        self._default_applied = False

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

    def __apply_defaults_if_needed( self ):
        if self._default_applied:
            return 
        self._default_applied = True
        #find out what operators are supported by value_type and
        #then configure the _disable_[methods|groups]
        pass
        
    def disable_method( self, method_name ):
        assert method_name in self.METHODS
        self.__apply_defaults_if_needed()
        self._disabled_methods.add( method_name )
        
    def enable_method( self, method_name ):
        assert method_name in self.METHODS
        self.__apply_defaults_if_needed()
        if method_name in self._disabled_methods:
            self._disabled_methods.remove( method_name )
    
    def _get_disabled_methods( self ): 
        self.__apply_defaults_if_needed()
        return self._disabled_methods
    disable_methods = property( _get_disabled_methods )

    def disable_methods_group( self, group_name ):
        assert group_name in self.METHOD_GROUPS
        self.__apply_defaults_if_needed()
        self._disabled_groups.add( group_name )
        
    def enable_methods_group( self, group_name ):
        assert group_name in self.METHOD_GROUPS
        self.__apply_defaults_if_needed()
        if group_name in self._disabled_groups:
            self._disabled_groups.remove( group_name )
    
    def _get_disabled_methods_groups( self ): 
        self.__apply_defaults_if_needed()
        return self._disabled_groups
    disabled_methods_groups = property( _get_disabled_methods_groups )