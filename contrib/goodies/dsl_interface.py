# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Authors: 
#   Allen Bierbaum
#

# Dictionary of this module. Useful for adding symbols
mod_dict = globals()

# Bring in the module builder and alias it
import pyplusplus.module_builder
ModuleBuilder = pyplusplus.module_builder.module_builder_t
set_logger_level = pyplusplus.module_builder.set_logger_level

# Bring in all call policy symbols
from pyplusplus.module_builder.call_policies import *

from pyplusplus.decl_wrappers import print_declarations


# Type traits
