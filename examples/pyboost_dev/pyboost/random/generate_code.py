#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


import os
import sys
import time
import shutil
import settings
from pygccxml import parser
from pygccxml import declarations
from pyplusplus import code_creators
from pyplusplus import module_builder

LICENSE = """// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
"""

class code_generator_t(object):    
    def __init__(self):
        self.__file = os.path.join( settings.boost.include
                                    , 'libs', 'random', 'random_test.cpp' )
        self.__mb = module_builder.module_builder_t( 
                        [ parser.create_cached_source_fc( 
                            self.__file
                            , os.path.join( settings.generated_files_dir, 'random_test.xml' ) ) ]
                        , gccxml_path=settings.gccxml.executable
                        , include_paths=[settings.boost.include]
                        , undefine_symbols=settings.undefined_symbols)
            
    def filter_declarations(self ):
        self.__mb.global_ns.exclude()
        boost_ns = self.__mb.global_ns.namespace( 'boost', recursive=False )
        boost_ns.namespace( 'random' ).include()
        boost_ns.namespaces( 'detail' ).exclude()
        for cls in boost_ns.namespace( 'random' ).classes():
            if cls.ignore: 
                continue
            else:
                aliases = set([ t.name for t in cls.typedefs ])
                for alias  in [ 'engine_value_type', 'value_type', 'base_type', 'engine_type' ]:
                    if alias in aliases:
                        aliases.remove( alias )
                if len( aliases ) == 1:
                    cls.alias = list( aliases )[0]
                else:
                    print cls.name
                    for t in aliases:
                        print '    ', t
        
        boost_ns.free_functions( "lessthan_signed_unsigned" ).exclude()
        boost_ns.free_functions( "equal_signed_unsigned" ).exclude()
        
    def beautify_code( self ):
        extmodule = self.__mb.code_creator
        position = extmodule.last_include_index() + 1
        extmodule.adopt_creator( code_creators.namespace_using_t( 'boost' )
                                 , position )
        
    def customize_extmodule( self ):
        global LICENSE
        extmodule = self.__mb.code_creator
        #beautifying include code generation
        extmodule.license = LICENSE
        extmodule.user_defined_directories.append( settings.boost.include )
        extmodule.user_defined_directories.append( settings.working_dir )
        extmodule.user_defined_directories.append( settings.generated_files_dir )
        extmodule.precompiled_header = 'boost/python.hpp'
        self.beautify_code( )
        
    def write_files( self ):
        self.__mb.write_module( os.path.join( settings.generated_files_dir, 'random.pypp.cpp' ) )

    def create(self):
        start_time = time.clock()      
        self.filter_declarations()
        
        self.__mb.build_code_creator( settings.module_name )
        
        self.customize_extmodule()
        self.write_files( )
        print 'time taken : ', time.clock() - start_time, ' seconds'

def export():
    cg = code_generator_t()
    cg.create()

if __name__ == '__main__':
    export()
    print 'done'
    
    
