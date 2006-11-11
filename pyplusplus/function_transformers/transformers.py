# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Initial author: Matthias Baas

"""This module contains the standard argument policy objects.

The following policies are available:

 - L{output_t}
 - L{input_t}
 - L{inout_t}
 - L{input_array_t}
 - L{output_array_t}
"""
import os
import transformer
from pygccxml import declarations
from pyplusplus import code_repository

# output_t
class output_t( transformer.transformer_t ):
    """Handles a single output variable.

    The specified variable is removed from the argument list and is turned
    into a return value.

    void getValue(int& v) -> v = getValue()
    """

    def __init__(self, idx):
        transformer.transformer_t.__init__( self )
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param idx: Index of the argument that is an output value (the first arg has index 1).
        @type idx: int
        """
        self.idx = idx
        self.local_var = "<not initialized>"

    def __str__(self):
        return "output(%d)"%(self.idx)

    def init_funcs(self, sm):
        # Remove the specified output argument from the wrapper function
        arg = sm.remove_arg(self.idx)

        # Do some sanity checking (whether the argument can actually be
        # an output argument, i.e. it has to be a reference or a pointer)
        reftype = arg.type
        if not declarations.is_pointer( reftype ) and not declarations.is_reference( reftype ):
            raise ValueError, '%s\nOutput variable %d ("%s") must be a reference or a pointer (got %s)'%(sm.decl, self.idx, arg.name, arg.type)

        # Declare a local variable that will receive the output value
        self.local_var = sm.wrapper_func.declare_variable(arg.name, str(reftype.base))
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
        res += "%s = boost::python::extract<%s>(%s);"%(arg.name, arg.type.base, sm.py_result_expr(self.local_var))
        return res

# input_t
class input_t(transformer.transformer_t):
    """Handles a single input variable.

    The reference on the specified variable is removed.

    void setValue(int& v) -> setValue(v)
    """

    def __init__(self, idx):
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param idx: Index of the argument that is an output value (the first arg has index 1).
        @type idx: int
        """
        transformer.transformer_t.__init__( self )
        self.idx = idx

    def __str__(self):
        return "input(%d)"%(self.idx)

    def init_funcs(self, sm):
        # Remove the specified input argument from the wrapper function
        arg = sm.remove_arg(self.idx)

        # Do some checks (the arg has to be a reference or a pointer)
        reftype = arg.type
        if not declarations.is_pointer( reftype ) and not declarations.is_reference( reftype ):
            raise ValueError, '%s\nInput variable %d ("%s") must be a reference or a pointer (got %s)'%(sm.decl, self.idx, arg.name, arg.type)

        # Create an equivalent argument that is not a reference type
        noref_arg = declarations.argument_t(name=arg.name, type=arg.type.base, default_value=arg.default_value)
        # Insert the noref argument
        sm.insert_arg(self.idx, noref_arg, arg.name)

# inout_t
class inout_t(transformer.transformer_t):
    """Handles a single input/output variable.

    void foo(int& v) -> v = foo(v)
    """

    def __init__(self, idx):
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param idx: Index of the argument that is an in/out value (the first arg has index 1).
        @type idx: int
        """
        transformer.transformer_t.__init__( self )
        self.idx = idx
        self.local_var = "<not initialized>"

    def __str__(self):
        return "inout(%d)"%(self.idx)

    def init_funcs(self, sm):
        # Remove the specified input argument from the wrapper function
        arg = sm.remove_arg(self.idx)

        # Do some checks (the arg has to be a reference or a pointer)
        reftype = arg.type
        if not declarations.is_pointer( reftype ) and not declarations.is_reference( reftype ):
            raise ValueError, '%s\nInOut variable %d ("%s") must be a reference or a pointer (got %s)'%(sm.decl, self.idx, arg.name, arg.type)

        # Create an equivalent argument that is not a reference type
        noref_arg = declarations.argument_t(name=arg.name, type=arg.type.base, default_value=arg.default_value)
        # Insert the noref argument
        sm.insert_arg(self.idx, noref_arg, arg.name)

        # Use the input arg to also store the output
        self.local_var = noref_arg.name
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
        res = "// Extract the C++ value for in/out argument '%s' (index: %d)\n"%(arg.name, self.idx)
        if isinstance(arg.type, declarations.pointer_t):
            res += "*"
        res += "%s = boost::python::extract<%s>(%s);"%(arg.name, arg.type.base, sm.py_result_expr(self.local_var))
        return res



# input_array_t
class input_array_t(transformer.transformer_t):
    """Handles an input array with fixed size.

    void setVec3(double* v) ->  setVec3(object v)
    # v must be a sequence of 3 floats
    """

    def __init__(self, idx, size):
        """Constructor.

        @param idx: Index of the argument that is an input array (the first arg has index 1).
        @type idx: int
        @param size: The fixed size of the input array
        @type size: int
        """
        transformer.transformer_t.__init__( self )
        self.idx = idx
        self.size = size

        self.argname = None
        self.basetype = None
        self.carray = None
        self.pylist = None

    def __str__(self):
        return "InputArray(%d,%d)"%(self.idx, self.size)

    def required_headers( self ):
        """Returns list of header files that transformer generated code depends on."""
        return [ code_repository.convenience.file_name ]

    def init_funcs(self, sm):

        # Remove the original argument...
        arg = sm.remove_arg(self.idx)

        if not declarations.is_pointer( arg.type ) and not declarations.is_array( arg.type ):
            raise ValueError, "%s\nArgument %d (%s) must be a pointer."%(sm.decl, self.idx, arg.name)

        # Declare a variable that will hold the Python list
        # (this will be the input of the Python call in the virtual function)
        self.pylist = sm.virtual_func.declare_variable("py_"+arg.name, "boost::python::list")

        # Replace the removed argument with a Python object.
        newarg = declarations.argument_t(arg.name, declarations.dummy_type_t("boost::python::object"))
        sm.insert_arg(self.idx, newarg, self.pylist)

        self.argname = arg.name
        self.basetype = str(arg.type.base).replace("const", "").strip()

        # Declare a variable that will hold the C array...
        self.carray = sm.wrapper_func.declare_variable("c_"+arg.name, self.basetype, size=self.size)

        # Replace the input parameter with the C array
        sm.wrapper_func.input_params[self.idx-1] = self.carray

    def wrapper_pre_call(self, sm):
        """Wrapper function code.
        """
        tmpl = []
        tmpl.append( '%(pypp_con)s::ensure_uniform_sequence< %(type)s >( %(argname)s, %(size)d );' )
        tmpl.append( '%(pypp_con)s::copy_sequence( %(argname)s, %(pypp_con)s::array_inserter( %(array_name)s, %(size)d ) );' )
        return os.linesep.join( tmpl ) % {
                  'type' : self.basetype
                , 'pypp_con' : 'pyplusplus::convenience'
                , 'argname' : self.argname
                , 'size' : self.size
                , 'array_name' : self.carray
               }

    def virtual_pre_call(self, sm):
        """Virtual function code."""
        tmpl = '%(pypp_con)s::copy_container( %(array)s, %(array)s + %(size)d, %(pypp_con)s::list_inserter( %(pylist)s ) );'
        return tmpl % { 
              'pypp_con' : 'pyplusplus::convenience'
            , 'array' : self.argname
            , 'size' : self.size
            , 'pylist' : self.pylist
            }


# output_array_t
class output_array_t(transformer.transformer_t):
    """Handles an output array of a fixed size.

    void getVec3(double* v) -> v = getVec3()
    # v will be a list with 3 floats
    """

    def __init__(self, idx, size):
        """Constructor.

        @param idx: Index of the argument that is an output array (the first arg has index 1).
        @type idx: int
        @param size: The fixed size of the output array
        @type size: int
        """
        transformer.transformer_t.__init__( self )
        self.idx = idx
        self.size = size

        self.argname = None
        self.basetype = None
        self.pyval = None
        self.cval = None
        self.ivar = None

    def __str__(self):
        return "OutputArray(%d,%d)"%(self.idx, self.size)

    def required_headers( self ):
        """Returns list of header files that transformer generated code depends on."""
        return [ code_repository.convenience.file_name ]

    def init_funcs(self, sm):
        # Remove the original argument...
        arg = sm.remove_arg(self.idx)

        if not declarations.is_pointer( arg.type ) and not declarations.is_array( arg.type ):            
            raise ValueError, "%s\nArgument %d (%s) must be a pointer."%(sm.decl, self.idx, arg.name)

        self.argname = arg.name
        self.basetype = str(arg.type.base).replace("const", "").strip()

        # Wrapper:

        # Declare a variable that will hold the C array...
        self.wrapper_cval = sm.wrapper_func.declare_variable("c_"+self.argname, self.basetype, size=self.size)
        # Declare a Python list which will receive the output...
        self.wrapper_pyval = sm.wrapper_func.declare_variable(self.argname, "boost::python::list")
        # ...and add it to the result
        sm.wrapper_func.result_exprs.append(arg.name)

        sm.wrapper_func.input_params[self.idx-1] = self.wrapper_cval

        # Virtual:

        # Declare a variable that will receive the Python list
        self.virtual_pyval = sm.virtual_func.declare_variable("py_"+self.argname, "boost::python::object")

    def wrapper_post_call(self, sm):
        tmpl = '%(pypp_con)s::copy_container( %(array)s, %(array)s + %(size)d, %(pypp_con)s::list_inserter( %(pylist)s ) );'
        return tmpl % { 
              'pypp_con' : 'pyplusplus::convenience'
            , 'array' : self.wrapper_cval
            , 'size' : self.size
            , 'pylist' : self.wrapper_pyval
        }

    def virtual_post_call(self, sm):
        tmpl = []
        tmpl.append( '%(pypp_con)s::ensure_uniform_sequence< %(type)s >( %(argname)s, %(size)d );' )
        tmpl.append( '%(pypp_con)s::copy_sequence( %(argname)s, %(pypp_con)s::array_inserter( %(array_name)s, %(size)d ) );' )
        return os.linesep.join( tmpl ) % {
                  'type' : self.basetype
                , 'pypp_con' : 'pyplusplus::convenience'
                , 'argname' : sm.py_result_expr(self.argname)
                , 'size' : self.size
                , 'array_name' : self.argname
               }
    