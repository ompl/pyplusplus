#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

#############################################################################
##                                                                          #
##   ANY CHANGE IN THIS FILE MUST BE REFLECTED IN docs/tutorials DIRECTORY  #
##                                                                          #
#############################################################################

import os
from environment import settings
from pyplusplus import module_builder

mb = module_builder.module_builder_t(
        files=['hello_world.hpp']
        , gccxml_path=settings.gccxml_path #path to gccxml executable
        , working_directory=settings.working_dir ) #setting working directory for gccxml

#rename enum Color to color
Color = mb.enum( 'color' )
Color.rename('Color')

#Set call policies to animal::get_name_ptr
animal = mb.class_( 'animal' )
get_name_ptr = animal.member_function( 'get_name_ptr', recursive=False )
get_name_ptr.call_policies = module_builder.call_policies.return_internal_reference()

#next code has same effect
get_name_ptr = mb.member_function( 'get_name_ptr' )
get_name_ptr.call_policies = module_builder.call_policies.return_internal_reference()

#I want to exclude all classes with name starts with impl
impl_classes = mb.classes( lambda decl: decl.name.startswith( 'impl' ) )
impl_classes.exclude()

#I want to exclude all functions that returns pointer to int
ptr_to_int = mb.free_functions( return_type='int *' )
ptr_to_int.exclude()

#I can print declarations to see what is going on
mb.print_declarations()

#I can print single declaration
mb.print_declarations( animal )

#Now it is the time to give a name to our module
mb.build_code_creator( module_name='hw' )

#It is common requirement in software world - each file should have license
mb.code_creator.license = '//Boost Software License( http://boost.org/more/license_info.html )'

#I don't want absolute includes within code
mb.code_creator.user_defined_directories.append( settings.working_dir )

#And finally we can write code to the disk
mb.write_module( os.path.join( settings.working_dir, 'hello_world.py.cpp' ) )