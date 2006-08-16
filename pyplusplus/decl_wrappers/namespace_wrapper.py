# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import scopedef_wrapper
from pygccxml import declarations

class namespace_t(scopedef_wrapper.scopedef_t, declarations.namespace_t):
    def __init__(self, *arguments, **keywords):
        scopedef_wrapper.scopedef_t.__init__( self )
        declarations.namespace_t.__init__(self, *arguments, **keywords )
   