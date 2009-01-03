import os
import sys
sys.path.append( '..' )

from environment import settings

from pygccxml import utils
from pygccxml import parser
from pyplusplus.module_builder import ctypes_module_builder_t

symbols_file = os.path.join( settings.easybmp_path, 'binaries', 'easybmp.map' )
shared_library = os.path.join( settings.easybmp_path, 'binaries', 'easybmp.dll' )

gccxml_cfg = parser.gccxml_configuration_t( working_directory=settings.working_dir
                                            , compiler=utils.native_compiler.get_gccxml_compiler()
                                            , gccxml_path=settings.gccxml_path )

mb = ctypes_module_builder_t( ['EasyBMP.h'], symbols_file, gccxml_cfg )

#~ mb.print_declarations()
mb.build_code_creator( shared_library )
mb.write_module( 'easybmp.py' )
