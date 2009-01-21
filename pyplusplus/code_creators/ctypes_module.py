# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import module
import import_
import library_reference
from pygccxml import utils

class ctypes_module_t(module.module_t):
    """This class represents the source code for the entire extension module.

    The root of the code creator tree is always a module_t object.
    """
    def __init__(self, global_ns):
        """Constructor.
        """
        module.module_t.__init__(self, global_ns, ctypes_module_t.CODE_GENERATOR_TYPES.CTYPES)

    def _create_impl(self):
        return self.create_internal_code( self.creators, indent_code=False )

    @utils.cached
    def library_var_name(self):
        for creator in self.creators:
            if isinstance( creator, library_reference.library_reference_t ):
                return creator.library_var_name
        else:
            raise RuntimeError( "Internal Error: library_reference_t creator was not created" )
