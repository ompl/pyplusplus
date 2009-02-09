# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import time
import types
import warnings
import module_builder
import ctypes_decls_dependencies

from pygccxml import binary_parsers
from pygccxml import parser
from pygccxml import declarations as decls_package

from pyplusplus import utils
from pyplusplus import _logging_
from pyplusplus import decl_wrappers
from pyplusplus import file_writers
from pyplusplus import code_creators
from pyplusplus import creators_factory

class ctypes_module_builder_t(module_builder.module_builder_t):
    """
    This class provides users with simple and intuitive interface to `Py++`
    and/or pygccxml functionality. If this is your first attempt to use `Py++`
    consider to read tutorials. You can find them on `web site <http://www.language-binding.net>`_.
    """
    def __init__( self
                  , files
                  , exported_symbols_file
                  , gccxml_config=None
                  , optimize_queries=True
                  , encoding='ascii' ):
        """
        :param files: list of files, declarations from them you want to export
        :type files: list of strings or :class:`parser.file_configuration_t` instances

        :param gccxml_path: path to gccxml binary. If you don't pass this argument,
        pygccxml parser will try to locate it using you environment PATH variable
        :type gccxml_path: str

        :param include_paths: additional header files location. You don't have to
        specify system and standard directories.
        :type include_paths: list of strings

        :param define_symbols: list of symbols to be defined for preprocessor.
        :param define_symbols: list of strings

        :param undefine_symbols: list of symbols to be undefined for preprocessor.
        :param undefine_symbols: list of strings

        :param cflags: Raw string to be added to gccxml command line.
        """
        module_builder.module_builder_t.__init__( self, global_ns=None, encoding=encoding )

        self.global_ns = self.__parse_declarations( files, gccxml_config )
        self.global_ns.decls(recursive=True, allow_empty=True)._code_generator = decl_wrappers.CODE_GENERATOR_TYPES.CTYPES
        self.__blob2decl = binary_parsers.merge_information( self.global_ns, exported_symbols_file )

        self.__apply_defaults()

        self.__code_creator = None
        if optimize_queries:
            self.run_query_optimizer()

    def __parse_declarations( self, files, gccxml_config, compilation_mode=None, cache=None ):
        if None is gccxml_config:
            gccxml_config = parser.config_t()
        if None is compilation_mode:
            compilation_mode = parser.COMPILATION_MODE.FILE_BY_FILE
        start_time = time.clock()
        self.logger.debug( 'parsing files - started' )
        reader = parser.project_reader_t( gccxml_config, cache, decl_wrappers.dwfactory_t() )
        decls = reader.read_files( files, compilation_mode )

        self.logger.debug( 'parsing files - done( %f seconds )' % ( time.clock() - start_time ) )

        return decls_package.matcher.get_single( decls_package.namespace_matcher_t( name='::' )
                                                 , decls )

    def __include_declarations( self ):
        self.global_ns.exclude()
        #include exported declarations
        included_decls = set( self.__blob2decl.itervalues() )
        to_be_included = ctypes_decls_dependencies.find_out_dependencies( included_decls )
        to_be_included.update( included_decls )
        map( lambda d: d.include(), to_be_included )

    def __apply_defaults( self ):
        self.__include_declarations()
        anonymous_classes = self.global_ns.classes( '', recursive=True, allow_empty=True )
        anonymous_classes.alias = '_'
        #TODO: check whether the anonymous class unique or not
        #if 1 == len( anonymous.parent.classes( '', recursive=False ) ):
        anonymous_vars = self.global_ns.vars( '', recursive=True, allow_empty=True )
        anonymous_vars.alias = '_'

    def build_code_creator( self, library_path, doc_extractor=None ):
        creator = creators_factory.ctypes_creator_t( self.global_ns
                                                    , library_path
                                                    , self.__blob2decl
                                                    , doc_extractor)
        self.__code_creator = creator.create()
        return self.__code_creator

    @property
    def code_creator( self ):
        "reference to :class:`code_creators.ctypes_module_t` instance"
        if not self.__code_creator:
            raise RuntimeError( "self.module is equal to None. Did you forget to call build_code_creator function?" )
        return self.__code_creator

    def has_code_creator( self ):
        """
        Function, that will return True if build_code_creator function has been
        called and False otherwise
        """
        return not ( None is self.__code_creator )

    def write_module( self, file_name ):
        """
        Writes module to single file
        :param file_name: file name
        :type file_name: string
        """
        file_writers.write_file( self.code_creator, file_name, encoding=self.encoding )


