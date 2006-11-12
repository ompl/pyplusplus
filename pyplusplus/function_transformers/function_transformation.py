# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


"""This module contains the class L{function_transformation_t}.
"""


class function_transformation_t:   
    def __init__(self, function, transformer_creator, **keywd):
        """Constructor. """
        self.__function = function
        self.__transformers = map( lambda tr_creator: tr_creator( function ), transformer_creator )
        self.__thread_safe = keywd.get( 'thread_safe', False )
        
    @property
    def transformers( self ):
        return self.__transformers

    def required_headers( self ):
        headers = []
        map( lambda transformer: headers.extend( transformer.required_headers() )
             , self.transformers )
        return headers

    @property
    def thread_safe( self ):
        return self.__thread_safe
