#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


import os
import sys
import time
import shutil
import crc_settings
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
        #self.__file = os.path.join( crc_settings.boost.include
                                    #,'libs', 'crc', 'crc_test.cpp' )
        self.__file = os.path.join( crc_settings.working_dir, 'crc_export.hpp' )
        
        self.__mb = module_builder.module_builder_t( 
                        [ parser.create_cached_source_fc( 
                            self.__file
                            , os.path.join( crc_settings.generated_files_dir, 'crc.xml' ) ) ]
                        , gccxml_path=crc_settings.gccxml.executable
                        , include_paths=[crc_settings.boost.include]
                        , define_symbols=crc_settings.defined_symbols
                        , undefine_symbols=crc_settings.undefined_symbols)
        
    def filter_declarations(self ):
        self.__mb.global_ns.exclude()
        boost_ns = self.__mb.global_ns.namespace( 'boost', recursive=False )
        boost_ns.classes( lambda decl: decl.name.startswith( 'crc_basic' ) ).include()
        boost_ns.classes( lambda decl: decl.name.startswith( 'crc_optimal' ) ).include()
        boost_ns.member_functions( 'process_bytes' ).exclude()
        boost_ns.member_functions( 'process_block' ).exclude()
        
    def prepare_decls( self ):
        boost_ns = self.__mb.namespace( 'boost' )
        classes = boost_ns.classes( lambda decl: decl.name.startswith( 'crc_basic' ) )
        classes.always_expose_using_scope = True
        for cls in classes:
            name, args = declarations.templates.split(cls.name)
            cls.alias = name + '_' + args[0]
            
        classes = boost_ns.classes( lambda decl: decl.name.startswith( 'crc_optimal' ) )
        classes.always_expose_using_scope = True
        for cls in classes:
            name, args = declarations.templates.split(cls.name)
            InitRem = args[2]
            for f in cls.calldefs():
                for arg in f.arguments:
                    if arg.default_value == 'InitRem':
                        arg.default_value = InitRem
            aliases = set( map( lambda decl: decl.name, cls.typedefs ) )
            if 'optimal_crc_type' in aliases:
                aliases.remove( 'optimal_crc_type' )
            if len( aliases ) == 1:
                cls.alias = list(aliases)[0]
            elif cls.name == 'crc_optimal<32, 79764919, 0, 0, false, false>':
                cls.alias = 'fast_crc_type'
            elif cls.name == 'crc_optimal<32, 0, 0, 0, false, false>':
                cls.alias = 'slow_crc_type'
            else:
                print 'no alias for class ', cls.name
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
        extmodule.adopt_include( code_creators.include_t( header='boost/crc.hpp' ) )

    def customize_extmodule( self ):
        global LICENSE
        extmodule = self.__mb.code_creator
        #beautifying include code generation
        extmodule.license = LICENSE
        extmodule.user_defined_directories.append( crc_settings.boost.include )
        extmodule.user_defined_directories.append( crc_settings.working_dir )
        extmodule.user_defined_directories.append( crc_settings.generated_files_dir )
        extmodule.precompiled_header = 'boost/python.hpp'
        self.replace_include_directives()
        self.beautify_code( )

    def write_files( self ):
        self.__mb.write_module( os.path.join( crc_settings.generated_files_dir, 'crc.pypp.cpp' ) )

    def create(self):
        start_time = time.clock()      
        self.filter_declarations()

        self.prepare_decls()
        
        self.__mb.build_code_creator( crc_settings.module_name )
        
        self.customize_extmodule()
        self.write_files( )
        print 'time taken : ', time.clock() - start_time, ' seconds'

def export():
    cg = code_generator_t()
    cg.create()

if __name__ == '__main__':
    export()
    print 'done'
    
    
