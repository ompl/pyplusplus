# -*- coding: utf-8 -*-
# Copyright 2004 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

'''
Code generation is started in a own thread. To exchange data, queues
are used.
'''

import os
import time
from pygccxml import parser
from pyplusplus import module_builder

def gen_xml(params, q_result, q_error):
    '''
    Generate XML code
    @param params: List of parameters [gccxml,incPath,macros]
    @param q_result: python queue to put result in
    @param q_error: python queue to put error in
    @return None (isn't evaluated)
    '''
    try:
        config = parser.config_t( gccxml_path=params[0]
                                  , include_paths=params[1]
                                  , define_symbols=params[2])
    
        header_file = params[3]
        config.include_paths.append( os.path.split( header_file )[0] )
        config.working_directory = os.path.split( header_file )[0]
        reader = parser.source_reader_t( config=config )
        xml_file = reader.create_xml_file( header_file )
        
        xml_file_obj = file( xml_file )
        q_result.put( xml_file_obj.read() )
        xml_file_obj.close()
        os.remove( xml_file )
        #self._statistics.set_parse_time( parsed_time )
        #self._statistics.set_code_generation_time( 0 )
    except Exception, error:
        q_result.put(str( error ))
        q_error.put(str( error ))
    
def gen_cpp(params, q_result, q_error):
    '''
    Generate cpp (Boost.Python) code
    @param params: List of parameters [gccxml,incPath,macros]
    @param q_result: python queue to put result in
    @param q_error: python queue to put error in
    @return None (isn't evaluated)
    '''
    try:
        header_file = params[3]
    
        include_paths = params[1]
        include_paths.append( os.path.split( header_file )[0] )
        
        mb = module_builder.module_builder_t( 
                [ header_file ]
                , gccxml_path=params[0]
                , working_directory=os.path.split( header_file )[0]
                , include_paths=include_paths
                , define_symbols=params[2] )

        mb.build_code_creator( "pyplusplus" )
        mb.code_creator.user_defined_directories.extend( include_paths )
        code = mb.code_creator.create()
        code = code.replace( '\n\r', '\n' )
        code = code.replace( '\r\n', '\n' )

        q_result.put( code )
    except Exception, error:
        q_result.put(str( error ))
        q_error.put(str( error ))

def gen_pypp(params, q_result, q_error):
    '''
    Generate Python (Py++) code
    @param params: List of parameters [gccxml,incPath,macros]
    @param q_result: python queue to put result in
    @param q_error: python queue to put error in
    @return None (isn't evaluated)
    '''
    pass

    