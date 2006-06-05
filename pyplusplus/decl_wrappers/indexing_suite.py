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

class indexing_suite_t( object ):
    def __init__( self, no_proxy=None, derived_policies=None ):
        object.__init__( self )
        self.__no_proxy = no_proxy
        self.__derived_policies = None
        
    def value_type(self):
        raise NotImplementedError()
    
    def _get_no_proxy( self ):
        if self.__no_proxy is None:
            value_type = self.value_type()
            if declaration.is_fundamental( value_type ):
                self.__no_proxy = True
            elif declarations.is_enum( value_type ):
                self.__no_proxy = True
            
            
            
            
            