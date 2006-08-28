# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Authors:
#   Allen Bierbaum
#
# This file defines overrides to the standard pyplusplus behavior
#
import time

print "Using Goodie perf overrides:"

# --- Override the behavior of mdecl_wrapper ---- #
import pygccxml.declarations.type_traits

#
# Increased performance by 20%
#
def override_tt_remove_alias(tp):
    """returns type without typedefs"""
    if not tp:
        return tp
    ret_val = getattr(tp,"_cache_ra", None)
    if not ret_val:
       ret_val = pygccxml.declarations.type_traits.__remove_alias( tp, False )
       setattr(tp,"_cache_ra",ret_val)
    return ret_val

#pygccxml.declarations.type_traits.remove_alias = override_tt_remove_alias
#print "   overriding type_traits.remove_alias"

# --------------- create_identifier --------------- #
import pyplusplus.code_creators.algorithm
import pyplusplus.decl_wrappers.algorithm
import pyplusplus.code_creators
import pyplusplus.code_creators.class_declaration

def override_create_identifier(creator, full_name ):
    """
    This function will find all relevant namespace aliases and will return new 
    full name that takes into account namespace aliases. 
    Override: Temporary.  Hack that is not portable.
    """
    return full_name

pyplusplus.decl_wrappers.algorithm.create_identifier = override_create_identifier
pyplusplus.code_creators.algorithm.create_identifier = override_create_identifier

print "   overriding decl_wrapper.algorithm.create_identifier."

# -------------- MB Cache --------------- #
import pyplusplus.module_builder

from pygccxml import parser
from pygccxml import declarations as decls_package

from pyplusplus import _logging_
from pyplusplus import decl_wrappers
from pyplusplus import file_writers
from pyplusplus import code_creators
from pyplusplus import module_creator as mcreator_package

import cPickle, md5, os.path, gzip
from pygccxml.parser.declarations_cache import file_signature, configuration_signature


def mb_override__init__( self
              , files
              , gccxml_path=''
              , working_directory='.'
              , include_paths=None
              , define_symbols=None
              , undefine_symbols=None
              , start_with_declarations=None
              , compilation_mode=None
              , cache=None
              , optimize_queries=True
              , ignore_gccxml_output=False
              , indexing_suite_version=1
              , cflags=""):
    """  See standard method. """
    object.__init__( self )
    self.logger = _logging_.loggers.module_builder
    gccxml_config = parser.config_t(
        gccxml_path=gccxml_path
        , working_directory=working_directory
        , include_paths=include_paths
        , define_symbols=define_symbols
        , undefine_symbols=undefine_symbols
        , start_with_declarations=start_with_declarations
        , ignore_gccxml_output=ignore_gccxml_output
        , cflags=cflags)

    #may be in future I will add those directories to user_defined_directories
    #to self.__code_creator.
    self._module_builder_t__working_dir = os.path.abspath( working_directory )

    self._module_builder_t__parsed_files = map( decls_package.filtering.normalize_path
                               , parser.project_reader_t.get_os_file_names( files ) )
    tmp = map( lambda file_: os.path.split( file_ )[0], self._module_builder_t__parsed_files )
    self._module_builder_t__parsed_dirs = filter( None, tmp )
    
    self._module_builder_t__global_ns = None
    
    # If we have a cache filename
    # - Compute signature and check it against file
    # - If matches, load it
    if cache:
        sig = md5.new()
        sig.update(configuration_signature(gccxml_config))
        for f in files:
            sig.update(file_signature(f))
        cur_digest = sig.hexdigest()

        if os.path.exists(cache):
            self.logger.info("Attempting to loading module cache file: %s"%cache)
            cache_file = file(cache,'rb')
            cache_digest = cPickle.load(cache_file)
            if (cur_digest == cache_digest):
                load_start_time = time.time()
                self.logger.info("   Signatures matched, loading data.")
                self._module_builder_t__global_ns = cPickle.load(cache_file)
                self._module_builder_t__code_creator = None
                self.logger.info("   Loading complete. %ss"%(time.time()-load_start_time))
            else:
                self.logger.info("   Signatures did not match. Ignoring cache.")
            cache_file.close()
    
    # If didn't load global_ns from cache
    # - Parse and optimize it
    # - Then save to cache if requested
    if not self._module_builder_t__global_ns:
        self.logger.info("Parsing declarations.")
        self._module_builder_t__global_ns = self._module_builder_t__parse_declarations( files
                                                      , gccxml_config
                                                      , compilation_mode
                                                      , None
                                                      , indexing_suite_version)
        self._module_builder_t__code_creator = None
        if optimize_queries:
            self.logger.info("Running optimizer.")
            self.run_query_optimizer()
        
        if cache:
            self.logger.info("Writing module cache... ")
            cache_file = file(cache,'wb')
            cPickle.dump(cur_digest, cache_file, cPickle.HIGHEST_PROTOCOL)
            cPickle.dump(self._module_builder_t__global_ns, cache_file, cPickle.HIGHEST_PROTOCOL)
            cache_file.close()
            self.logger.info("Complete.")

    self._module_builder_t__declarations_code_head = []
    self._module_builder_t__declarations_code_tail = []

    self._module_builder_t__registrations_code_head = []
    self._module_builder_t__registrations_code_tail = []

pyplusplus.module_builder.module_builder_t.__init__ = mb_override__init__
print "   overriding module_builder.__init__ with cache."

