# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import sys
import algorithm
from pyplusplus import _logging_
from pygccxml import declarations



__REPOTED_REPLACES = []
def report_msg_once( msg ):
    global __REPOTED_REPLACES
    if msg not in __REPOTED_REPLACES:
        print 'pyplusplus: ', msg
        __REPOTED_REPLACES.append( msg )

class ERROR_BEHAVIOR:
    PRINT = 'print'
    RAISE = 'raise'
    
class decl_wrapper_t(object):
    """Declaration interface.

    This class represents the interface to the declaration tree. Its
    main purpose is to "decorate" the nodes in the tree with
    information about how the binding is to be created. Instances of
    this class are never created by the user, instead they are
    returned by the API.
    """

    def __init__(self):
        object.__init__(self)
        self._alias = None
        self._ignore = False
        
    def _generate_valid_name(self, name=None):
        if name == None:
            name = self.name
        return algorithm.create_valid_name( name )
            
    def _get_alias(self):
        if not self._alias:
            if declarations.templates.is_instantiation( self.name ):
                if isinstance( self, declarations.class_t ) \
                    and 1 == len( set( map( lambda typedef: typedef.name, self.typedefs ) ) ):
                        self._alias = self.typedefs[0].name
                else:
                    self._alias = self._generate_valid_name()
            else:
                self._alias = self.name
        return self._alias

    def _set_alias(self, alias):
        self._alias = alias
    alias = property( _get_alias, _set_alias
                      , doc="Using this property you can easily change Python name of declaration" )
    
    def rename( self, new_name ):
        self.alias = new_name
    
    def _get_ignore( self ):
        return self._ignore
    def _set_ignore( self, value ):
        self._ignore = value
    ignore = property( _get_ignore, _set_ignore
                       ,doc="If you set ignore to True then this declaration will not be exported." )    
    def exclude( self ):
        """Exclude "self" and child declarations from being exposed."""
        self.ignore = True
    
    def include( self ):
        """Include "self" and child declarations to be exposed."""
        self.ignore = False

    #TODO:
    #I think that almost every declaration could have some wrapper. This is the
    #main reason why those 3 functions does not have some well defined interface.
    #def has_wrapper( self ):
        #return False
    
    #def _finalize_impl( self, error_behavior ):
        #pass
    
    #def finalize( self, error_behavior=None):
        #try:
            #self._finalize_impl( self )
        #except Exception, error:
            #if None is error_behavior or error_behavior == ERROR_BEHAVIOR.PRINT:
                #print 'Unable to finalize declaration: ', str( error )
            #else:
                #raise
    
    def readme( self ):
        """This function will returns some hints/tips/description of problems
        that applied to the declarations. For example function that has argument
        reference to some fundamental type could be exported, but could not be called
        from Python
        """
        return []
