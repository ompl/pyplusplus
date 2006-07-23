# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import writer
import multiple_files
from sets import Set as set
from pygccxml import declarations
from pyplusplus import decl_wrappers
from pyplusplus import code_creators

#TODO: to add namespace_alias_t classes
class class_multiple_files_t(multiple_files.multiple_files_t):
    """
    This class will split code, generated for huge classes, to few files.
    Next strategy will be used:
    1. New directory with class alias name will be created.
    2. pyplusplus will generate 
       wrapper header - header that will contain code generated for class wrappers
       classes h/cpp - will contain registration code for internal classes
       memfun h/cpp - will contain registration code for member functions

       alias + _main h/cpp this class will contain main registration function.
    """ 

    def __init__(self, extmodule, directory_path, huge_classes):
        multiple_files.multiple_files_t.__init__(self, extmodule, directory_path)
        self.huge_classes = huge_classes
        self.internal_splitters = [
            self.split_internal_enums
            , self.split_internal_unnamed_enums
            #, self.split_internal_member_functions
            , self.split_internal_classes
            #, self.split_internal_member_variables
        ]
 
    def split_class_impl( self, class_creator):
        function_name = 'register_%s_class' % class_creator.alias
        file_path = os.path.join( self.directory_path, class_creator.alias )
        # Write the .h file...
        header_name = file_path + self.HEADER_EXT
        self.write_file( header_name
                         , self.create_header( class_creator.alias
                                               , self.create_function_code( function_name ) ) )
        class_wrapper = None
        decl_creators = None
        if isinstance( class_creator, code_creators.class_t ) and class_creator.wrapper:
            class_wrapper = class_creator.wrapper
            decl_creators = [ class_creator.wrapper ]
        # Write the .cpp file...
        cpp_code = self.create_source( class_creator.alias
                                       , function_name
                                       , [class_creator]
                                       , decl_creators )
        self.write_file( file_path + self.SOURCE_EXT, cpp_code )
        if class_wrapper:
            # The wrapper has already been written above, so replace the create()
            # method with a new 'method' that just returns an empty string because
            # this method is later called again for the main source file.
            class_wrapper.create = lambda: ''
        # Replace the create() method so that only the register() method is called
        # (this is called later for the main source file).
        class_creator.create = lambda: function_name +'();'
        self.__include_creators.append( code_creators.include_t( header_name ) )
        self.split_header_names.append(header_name)
        self.split_method_names.append(function_name)

    def write_wrapper( self, class_creator ):
        code = ''
        if class_creator.wrapper:
            code = class_creator.wrapper.create()
            class_creator.wrapper.create = lambda: ''
        
        wrapper_code = self.create_header( class_creator.alias + '_wrapper', code ) 
        header_file = os.path.join( self.directory_path, class_creator.alias, 'wrapper' + self.HEADER_EXT )
        self.write_file( header_file, wrapper_code )
        
    def split_internal_creators( self, class_creator, creators, pattern ):
        file_path = os.path.join( self.directory_path
                                  , class_creator.alias
                                  , pattern )
                                  
        function_name = 'register_%s_%s' % ( class_creator.alias, pattern )
        
        self.write_file( file_path + self.HEADER_EXT
                         , self.create_header( pattern, self.create_function_code( function_name ) ) )

        self.write_file( file_path + self.SOURCE_EXT
                         , self.create_source( pattern
                                               , function_name
                                               , creators ))
        for index, creator in enumerate( creators ):
            if 0 == index:
                creator.create = lambda: function_name + '();'
            else:
                creator.create = lambda: ''

    def split_internal_enums( self, class_creator ):
        """Write all enumerations into a separate .h/.cpp file.
        """
        enums_creators = filter( lambda x: isinstance(x, code_creators.enum_t )
                                 , class_creator.creators )
        self.split_internal_creators( class_creator, enums_creators, 'enums' )
        return 'enums'

    def split_internal_unnamed_enums( self, class_creator ):
        creators = filter( lambda x: isinstance(x, code_creators.unnamed_enum_t )
                           , class_creator.creators )
        self.split_internal_creators( class_creator, creators, 'unnamed_enums' )
        return 'unnamed_enums'

    def split_internal_member_functions( self, class_creator ):
        creators = filter( lambda x: isinstance(x, code_creators.mem_fun_t )
                           , class_creator.creators )
        self.split_internal_creators( class_creator, creators, 'memfuns' )
        return 'memfuns'

    def split_internal_classes( self, class_creator ):
        class_types = ( code_creators.class_t, code_creators.class_declaration_t )
        creators = filter( lambda x: isinstance(x, class_types ), class_creator.creators )
        self.split_internal_creators( class_creator, creators, 'classes' )
        return 'classes'

    def split_internal_member_variables( self, class_creator ):
        creators = filter( lambda x: isinstance(x, code_creators.member_variable_base_t)
                           , class_creator.creators )
        self.split_internal_creators( class_creator, creators, 'memvars' )
        return 'memvars'
        
    def split_class_impl( self, class_creator):
        if not class_creator.declaration in self.huge_classes:
            return super( class_multiple_files_t, self ).split_class_impl( class_creator )
        
        extmodule = class_creator.top_parent
        
        self.create_dir( os.path.join( self.directory_path, class_creator.alias ) )
        
        function_name = 'register_%s_class' % class_creator.alias
        file_path = os.path.join( self.directory_path, class_creator.alias )
        # Write the .h file...
        header_name = file_path + self.HEADER_EXT
        self.write_file( header_name
                         , self.create_header( class_creator.alias
                                               , self.create_function_code( function_name ) ) )
            
        self.write_wrapper( class_creator )
        wrapper_include = code_creators.include_t( os.path.join( class_creator.alias, 'wrapper' + self.HEADER_EXT ) )
        
        extmodule.adopt_include( wrapper_include )

        include_creators = [ wrapper_include ]
        splitter_includes = []
        for splitter in self.internal_splitters:
            pattern = splitter( class_creator )
            include_creator = code_creators.include_t( os.path.join( class_creator.alias, pattern + self.HEADER_EXT ) )
            splitter_includes.append( include_creator )
        
        for creator in splitter_includes:
            extmodule.adopt_include( creator )

        # Write the .cpp file...
        cpp_code = self.create_source( class_creator.alias
                                       , function_name
                                       , [class_creator] )
                                       
        self.write_file( file_path + self.SOURCE_EXT, cpp_code )                                       
        
        extmodule.remove_creator( wrapper_include )
        for creator in splitter_includes:
            extmodule.remove_creator( creator )
        # Replace the create() method so that only the register() method is called
        # (this is called later for the main source file).
        class_creator.create = lambda: function_name +'();'
        self.include_creators.append( code_creators.include_t( header_name ) )
        self.split_header_names.append(header_name)
        self.split_method_names.append(function_name)
