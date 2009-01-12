import os
import sys

import project_env

from pygccxml import utils
from pygccxml import parser
from pygccxml import declarations
from pyplusplus.module_builder import ctypes_module_builder_t


gccxml_cfg = parser.gccxml_configuration_t( gccxml_path=project_env.settings.gccxml_path )

mb = ctypes_module_builder_t( [project_env.gmp.header_file], project_env.gmp.symbols_file, gccxml_cfg )

#there is a bug in the code generator
has_varargs = lambda f: f.arguments \
                        and isinstance( f.arguments[-1].type, declarations.ellipsis_t )

mb.calldefs( has_varargs ).exclude()
mb.classes( '' ).exclude()

#gmp uses strange convention: every function name starts with __gmp and than, it
#introduces define, which aliass __gmpy to gmpy
for f in mb.calldefs( lambda x: x.name.startswith('__gmp') ):
    f.alias = f.name[2:]

#there is a bug in "include" algorithm - I need to wrote DFS
mb.class_( '_IO_FILE' ).opaque = True

#include should work as expected - include only exported function

#~ mb.print_declarations()
mb.build_code_creator( project_env.gmp.shared_library_file )
mb.write_module( os.path.join( project_env.gmp.generated_code_dir, '__init__.py' ) )

