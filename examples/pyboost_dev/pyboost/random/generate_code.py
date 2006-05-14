#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


import os
import sys
import time
import shutil
import random_settings
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
        self.__file = os.path.join( random_settings.boost.include
                                    , 'libs', 'random', 'random_test.cpp' )
        self.__mb = module_builder.module_builder_t( 
                        [ parser.create_cached_source_fc( 
                            self.__file
                            , os.path.join( random_settings.generated_files_dir, 'random_test.xml' ) ) ]
                        , gccxml_path=random_settings.gccxml.executable
                        , include_paths=[random_settings.boost.include]
                        , define_symbols=random_settings.defined_symbols
                        , undefine_symbols=random_settings.undefined_symbols)
        
    def filter_declarations(self ):
        self.__mb.global_ns.exclude()
        boost_ns = self.__mb.global_ns.namespace( 'boost', recursive=False )
        boost_ns.namespace( 'random' ).include()
        boost_ns.namespaces( 'detail' ).exclude()
        for cls in boost_ns.namespace( 'random' ).classes():
            if cls.ignore: 
                continue
            if cls.name.startswith( 'const_mod' ):
                cls.exclude()
                continue
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
            if cls.alias == 'ecuyer1988':
                seed = cls.member_function( 'seed', arg_types=[None, None] )
                seed.exclude()
                
        boost_ns.free_functions( "lessthan_signed_unsigned" ).exclude()
        boost_ns.free_functions( "equal_signed_unsigned" ).exclude()
        
    def beautify_code( self ):
        extmodule = self.__mb.code_creator
        position = extmodule.last_include_index() + 1
        extmodule.adopt_creator( code_creators.namespace_using_t( 'boost' )
                                 , position )
        self.__mb.calldefs().create_with_signature = True
        
    def replace_include_directives( self ):
        extmodule = self.__mb.code_creator
        includes = filter( lambda creator: isinstance( creator, code_creators.include_t )
                           , extmodule.creators )
        includes = includes[1:] #all includes except boost\python.hpp
        map( lambda creator: extmodule.remove_creator( creator ), includes )
        for include_header in ['boost/random.hpp', 'boost/nondet_random.hpp' ]:
            extmodule.adopt_include( code_creators.include_t( header=include_header ) )

    def customize_extmodule( self ):
        global LICENSE
        extmodule = self.__mb.code_creator
        #beautifying include code generation
        extmodule.license = LICENSE
        extmodule.user_defined_directories.append( random_settings.boost.include )
        extmodule.user_defined_directories.append( random_settings.working_dir )
        extmodule.user_defined_directories.append( random_settings.generated_files_dir )
        extmodule.precompiled_header = 'boost/python.hpp'
        self.replace_include_directives()
        self.beautify_code( )

#include "boost/random.hpp"
#include "boost/nondet_random.hpp"

        
        
    def write_files( self ):
        self.__mb.write_module( os.path.join( random_settings.generated_files_dir, 'random.pypp.cpp' ) )

    def create(self):
        start_time = time.clock()      
        self.filter_declarations()
        
        self.__mb.build_code_creator( random_settings.module_name )
        
        self.customize_extmodule()
        self.write_files( )
        print 'time taken : ', time.clock() - start_time, ' seconds'

def export():
    cg = code_generator_t()
    cg.create()

if __name__ == '__main__':
    export()
    print 'done'
    
    
