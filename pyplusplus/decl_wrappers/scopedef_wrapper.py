# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import decl_wrapper

class scopedef_t(decl_wrapper.decl_wrapper_t):    
    """
    In C++ there are 2 declarations that can contain definition of other
    declarations: class and namespace. This class is used as a base class for both
    of them. 
    """
        
    def __init__(self):
        decl_wrapper.decl_wrapper_t.__init__( self )

    def exclude( self ):
        """Exclude "self" and child declarations from being exposed."""
        self.ignore = True
        map( lambda decl: decl.exclude(), self.declarations )
    
    def include( self ):
        """Include "self" and child declarations to be exposed."""
        self.ignore = False
        map( lambda decl: decl.include(), self.declarations )
