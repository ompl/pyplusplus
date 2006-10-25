# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


"""This module contains the class L{function_transformation_t}.
"""


class function_transformation_t:   
    def __init__(self, transformers):
        """Constructor.
        """
        self.__transformers = list(transformers)

    @property
    def transformers( self ):
        return self.__transformers
