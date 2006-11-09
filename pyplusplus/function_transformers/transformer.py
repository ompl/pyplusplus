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


class transformer_t:
    """Base class for a function transformer.

    This class specifies the interface that a user written transformer
    has to implement. It doesn't contain any actual functionality so
    a user doesn't have to derive from this class. Methods that are not
    implemented are treated as if they would do nothing and return None.

    @author: Matthias Baas
    """
    
    def __init__(self):
        """Constructor.
        """
        pass

    def init_funcs(self, sm):
        """Wrapper initialization.

        This method is called before the actual wrapper source code is
        generated. This is the place where you can modify the signature
        of the C++ wrapper function or allocate local variables.

        @param sm: Substitution manager instance
        @type sm: L{substitution_manager_t}
        """
        pass

    def wrapper_pre_call(self, sm):
        """Generate the C++ code that should be executed before the actual function call.

        The code from this method will be put into the wrapper function.

        @param sm: Substitution manager instance
        @type sm: L{substitution_manager_t}
        @return: C++ code or None
        @rtype: str
        """
        pass

    def wrapper_post_call(self, sm):
        """Generate the C++ code that should be executed after the actual function call.

        The code from this method will be put into the wrapper function.

        @param sm: Substitution manager instance
        @type sm: L{substitution_manager_t}
        @return: C++ code or None
        @rtype: str
        """
        pass

    def wrapper_cleanup(self, sm):
        """Generate code that should be executed in the case of an error.

        This method has to assume that the preCall code was executed but
        the postCall code won't be executed because something went wrong.
        
        <not used yet>
        
        @param sm: Substitution manager instance
        @type sm: L{substitution_manager_t}
        @return: C++ code or None
        @rtype: str
        """
        pass

    def virtual_pre_call(self, sm):
        """Generate the C++ code that should be executed before the actual function call.

        The code from this method will be put into the virtual function.
        
        @param sm: Substitution manager instance
        @type sm: L{substitution_manager_t}
        @return: C++ code or None
        @rtype: str
        """
        pass

    def virtual_post_call(self, sm):
        """Generate the C++ code that should be executed after the actual function call.

        The code from this method will be put into the virtual function.

        @param sm: Substitution manager instance
        @type sm: L{substitution_manager_t}
        @return: C++ code or None
        @rtype: str
        """
        pass

    def virtual_cleanup(self, sm):
        pass
    
    