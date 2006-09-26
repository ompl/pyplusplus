# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"defines property_t helper class"

from pygccxml import declarations

class property_t( object ):
    def __init__( self, name, fget, fset=None, doc='', is_static=False ):
        self._name = name
        self._fget = fget
        self._fset = fset
        self._doc = doc
        self._is_static = is_static

    @property
    def name( self ):
        return self._name

    @property
    def fget( self ):
        return self._fget

    @property
    def fset( self ):
        return self._fset

    @property
    def doc( self ):
        return self._doc

    @property
    def is_static( self ):
        return self._is_static

    def __str__( self ):
        desc = []
        desc.append( 'fget=%s' % declarations.full_name( self.fget ) )
        if self.fset:
            desc.append( ', ' )
            desc.append( 'fset=%s' % declarations.full_name( self.fset ) )
        return "property [%s]"% ''.join( desc )

def find_properties( cls ):
    """this function should return a list of possible properties for the class"""
    #get* set*
    #get_* set_*
    #*, set*
    #*, set_*
    #get defined on [derived|base], set defined on [base|derived]

    raise NotImplemented()



