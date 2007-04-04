# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations
from pyplusplus import code_creators
from pyplusplus import code_repository

class manager_t( object ):
    def __init__( self, extmodule ):
        object.__init__( self )
        self.__extmodule = extmodule
        self.__already_included = set()
        self.normalize = code_creators.include_directories_t.normalize
        
        self.__extmodule.add_system_header( "boost/python.hpp" )
        self.__extmodule.adopt_creator( code_creators.include_t( header="boost/python.hpp" ) )

    def include( self, header, system=False, once=True, user_defined=False ):
        if once:
            normalized_header = self.normalize( header )
            if normalized_header in self.__already_included:
                return
        self.__extmodule.add_system_header( header )
        self.__extmodule.adopt_include( code_creators.include_t( header, user_defined=user_defined ) )
        if system:
            self.__extmodule.add_system_header( header )
        

    def include_call_policy( self, call_policy ):
        if not call_policy:
            return 
        if call_policy.is_predefined():
            #boost/python.hpp is already included
            return 
        self.include( call_policy.header_file, system=True )
    
    def include_ft( self, required_headers ): #include function transformation headers
        for header in required_headers:
            # Check whether the header is already included
            system = bool( header in code_repository.headers )
            self.include( header, system=system, user_defined=True )
                
        if not self.__extmodule.is_system_header( code_repository.named_tuple.file_name ):
            self.__extmodule.add_system_header( code_repository.named_tuple.file_name )
        
        
        
        
        
        
        