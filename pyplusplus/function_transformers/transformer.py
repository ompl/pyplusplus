# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Initial author: Matthias Baas

"""This module contains the class L{transformer_t}.
"""

import sys, os.path, copy, re, types
from pygccxml import declarations, parser

return_ = -1

class transformer_t:
    USE_1_BASED_INDEXING = False
    
    """Base class for a function transformer.

    This class specifies the interface that a user written transformer
    has to implement. It doesn't contain any actual functionality so
    a user doesn't have to derive from this class. Methods that are not
    implemented are treated as if they would do nothing and return None.

    @author: Matthias Baas
    """
    
    def __init__(self, function):
        """Constructor.
        """
        self.__function = function

    @property 
    def function( self ):
        """reference to the function, for which a wrapper will be generated"""
        return self.__function

    def required_headers( self ):
        """Returns list of header files that transformer generated code depends on."""
        return []

    def get_argument( self, reference ):
        if isinstance( reference, str ):
            found = filter( lambda arg: arg.name == reference, self.function.arguments )
            if len( found ) == 1:
                return found[0]
            raise RuntimeError( "Argument with %s was not found" % reference )
        else:
           assert isinstance( reference, int )
           if transformer_t.USE_1_BASED_INDEXING:
               reference += 1
           return self.function.arguments[ reference ]

    def get_type( self, reference ):
        global return_
        if isinstance( reference, int ) and reference == return_:
            return self.function.return_type
        else:
            return self.get_argument( reference ).type

    def configure_mem_fun( self, controller ):
        pass
    
    def configure_free_fun( self, controller ):
        pass
    
    