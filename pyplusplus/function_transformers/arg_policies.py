# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Initial author: Matthias Baas

"""This module contains standard argument policy objects.
"""

from pygccxml import declarations

# Output
class Output:
    """Handles a single output variable.

    The specified variable is removed from the argument list and is turned
    into a return value.

    void getValue(int& v) -> v = getValue()
    """
    
    def __init__(self, idx):
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param idx: Index of the argument that is an output value (the first arg has index 1).
        @type idx: int
        """
        self.idx = idx
        self.local_var = "<not initialized>"

    def __str__(self):
        return "Output(%d)"%(self.idx)

    def init_funcs(self, sm):
        # Remove the specified output argument from the wrapper function
        arg = sm.remove_arg(self.idx)

        # Do some sanity checking (whether the argument can actually be
        # an output argument, i.e. it has to be a reference or a pointer)
        reftype = arg.type
        if not (isinstance(reftype, declarations.reference_t) or
            isinstance(reftype, declarations.pointer_t)):
            raise ValueError, 'Output variable %d ("%s") must be a reference or a pointer (got %s)'%(self.idx, arg.name, arg.type)

        # Declare a local variable that will receive the output value
        self.local_var = sm.wrapper_func.declare_local(arg.name, str(reftype.base))
        # Append the output to the result tuple
        sm.wrapper_func.result_exprs.append(self.local_var)

        # Replace the expression in the C++ function call
        if isinstance(reftype, declarations.pointer_t):
            sm.wrapper_func.input_params[self.idx-1] = "&%s"%self.local_var
        else:
            sm.wrapper_func.input_params[self.idx-1] = self.local_var

    
    def virtual_post_call(self, sm):
        """Extract the C++ value after the call to the Python function.
        """
        arg = sm.virtual_func.arg_list[self.idx-1]
        res = "// Extract the C++ value for output argument '%s' (index: %d)\n"%(arg.name, self.idx)
        if isinstance(arg.type, declarations.pointer_t):
            res += "*"
        res += "%s = boost::python::extract<%s>(%s[%d]);"%(arg.name, arg.type.base, sm.virtual_func.result_var, sm.wrapper_func.result_exprs.index(self.local_var))
        return res


