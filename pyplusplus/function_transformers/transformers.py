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

#TODO: pointers should be checked for NULL

def is_ref_or_ptr( type_ ):
    return declarations.is_pointer( type_ ) or declarations.is_reference( type_ )

def is_ptr_or_array( type_ ):
    return declarations.is_pointer( type_ ) or declarations.is_array( type_ )

def remove_ref_or_ptr( type_ ):
    if declarations.is_pointer( type_ ):
        return declarations.remove_pointer( type_ )
    elif declarations.is_reference( type_ ):
        return declarations.remove_reference( type_ )
    else:
        raise TypeError( 'Type should be reference or pointer, got %s.' % type_ )
    

# output_t
class output_t( transformer.transformer_t ):
    """Handles a single output variable.

    The specified variable is removed from the argument list and is turned
    into a return value.

    void getValue(int& v) -> v = getValue()
    """

    def __init__(self, function, arg_ref):
        transformer.transformer_t.__init__( self, function )
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param arg_ref: Index of the argument that is an output value (the first arg has index 1).
        @type arg_ref: int
        """
        self.arg = self.get_argument( arg_ref )
        self.arg_index = self.function.arguments.index( self.arg )
        self.local_var = "<not initialized>"

        if not is_ref_or_ptr( self.arg.type ):
            raise ValueError( '%s\nin order to use "output" transformation, argument %s type must be a reference or a pointer (got %s).' ) \
                  % ( function, self.arg_ref.name, arg.type)

    def __str__(self):
        return "output(%d)"%(self.arg_index)

    def init_funcs(self, sm):
        # Remove the specified output argument from the wrapper function
        sm.remove_arg(self.arg_index+1)

        # Declare a local variable that will receive the output value
        self.local_var = sm.wrapper_func.declare_variable( self.arg.name, str( remove_ref_or_ptr( self.arg.type ) ) )
        # Append the output to the result tuple
        sm.wrapper_func.result_exprs.append(self.local_var)

        # Replace the expression in the C++ function call
        input_param = self.local_var
        if declarations.is_pointer( self.arg.type ):
            input_param = "&%s" % self.local_var
            
        sm.wrapper_func.input_params[self.arg_index] = input_param


    def virtual_post_call(self, sm):
        """Extract the C++ value after the call to the Python function."""
        res = []
        if declarations.is_pointer( self.arg.type ):
            res.append( "*" )
        res.append( "%s = boost::python::extract<%s>(%s);" \
                    % ( self.arg.name
                        , remove_ref_or_ptr( self.arg.type )
                        , sm.py_result_expr(self.local_var) ) )
        return ''.join( res )
        
# input_t
class input_t(transformer.transformer_t):
    """Handles a single input variable.

    The reference on the specified variable is removed.

    void setValue(int& v) -> setValue(v)
    """

    def __init__(self, function, arg_ref):
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param idx: Index of the argument that is an output value (the first arg has index 1).
        @type idx: int
        """
        transformer.transformer_t.__init__( self, function )
        self.arg = self.get_argument( arg_ref )
        self.arg_index = self.function.arguments.index( self.arg )

        if not is_ref_or_ptr( self.arg.type ):
            raise ValueError( '%s\nin order to use "input" transformation, argument %s type must be a reference or a pointer (got %s).' ) \
                  % ( function, self.arg_ref.name, arg.type)

    def __str__(self):
        return "input(%d)"%(self.idx)

    def init_funcs(self, sm):
        # Remove the specified input argument from the wrapper function
        sm.remove_arg(self.arg_index + 1)

        # Create an equivalent argument that is not a reference type
        noref_arg = self.arg.clone( type=remove_ref_or_ptr( self.arg.type ) )
        # Insert the noref argument
        sm.insert_arg(self.arg_index + 1, noref_arg, self.arg.name)

# inout_t
class inout_t(transformer.transformer_t):
    """Handles a single input/output variable.

    void foo(int& v) -> v = foo(v)
    """

    def __init__(self, function, arg_ref):
        """Constructor.

        The specified argument must be a reference or a pointer.

        @param idx: Index of the argument that is an in/out value (the first arg has index 1).
        @type idx: int
        """
        transformer.transformer_t.__init__( self, function )
        self.arg = self.get_argument( arg_ref )
        self.arg_index = self.function.arguments.index( self.arg )
        self.local_var = "<not initialized>"
        
        if not is_ref_or_ptr( self.arg.type ):
            raise ValueError( '%s\nin order to use "inout" transformation, argument %s type must be a reference or a pointer (got %s).' ) \
                  % ( function, self.arg_ref.name, arg.type)

    def __str__(self):
        return "inout(%d)"%(self.arg_index)

    def init_funcs(self, sm):
        # Remove the specified input argument from the wrapper function
        sm.remove_arg(self.arg_index + 1)

        # Create an equivalent argument that is not a reference type
        noref_arg = self.arg.clone( type=remove_ref_or_ptr( self.arg.type ) )

        # Insert the noref argument
        sm.insert_arg(self.idx+1, noref_arg, arg.name)

        # Use the input arg to also store the output
        self.local_var = noref_arg.name
        # Append the output to the result tuple
        sm.wrapper_func.result_exprs.append(self.local_var)

        # Replace the expression in the C++ function call
        input_param = self.local_var
        if declarations.is_pointer( self.arg.type ):
            input_param = "&%s" % self.local_var
            
        sm.wrapper_func.input_params[self.arg_index] = input_param

    def virtual_post_call(self, sm):
        """Extract the C++ value after the call to the Python function."""
        res = []
        if isinstance(arg.type, declarations.pointer_t):
            res.append( "*" )
        res.append( "%s = boost::python::extract<%s>(%s);" 
                    % ( self.arg.name
                        , remove_ref_or_ptr( self.arg.type )
                        , sm.py_result_expr( self.local_var ) ) )
        return ''.join( res )

# input_array_t
class input_array_t(transformer.transformer_t):
    """Handles an input array with fixed size.

    void setVec3(double* v) ->  setVec3(object v)
    # v must be a sequence of 3 floats
    """

    def __init__(self, function, arg_ref, array_size):
        """Constructor.

        @param size: The fixed size of the input array
        @type size: int
        """
        transformer.transformer_t.__init__( self, function )
        
        self.arg = self.get_argument( arg_ref )
        self.arg_index = self.function.arguments.index( self.arg )

        if not is_ptr_or_array( self.arg.type ):
            raise ValueError( '%s\nin order to use "input_array" transformation, argument %s type must be a array or a pointer (got %s).' ) \
                  % ( function, self.arg_ref.name, arg.type)

        self.array_size = array_size
        self.native_array = None
        self.pylist = None

    def __str__(self):
        return "input_array(%s,%d)"%( self.arg.name, self.array_size)

    def required_headers( self ):
        """Returns list of header files that transformer generated code depends on."""
        return [ code_repository.convenience.file_name ]

    def init_funcs(self, sm):
        # Remove the original argument...
        sm.remove_arg(self.arg_index + 1)

        # Declare a variable that will hold the Python list
        # (this will be the input of the Python call in the virtual function)
        self.pylist = sm.virtual_func.declare_variable("py_" + self.arg.name, "boost::python::list")

        # Replace the removed argument with a Python object.
        newarg = self.arg.clone( type=declarations.dummy_type_t("boost::python::object") )
        sm.insert_arg(self.arg_index+1, newarg, self.pylist)

        # Declare a variable that will hold the C array...
        self.native_array = sm.wrapper_func.declare_variable( 
              "native_" + self.arg.name
            , declarations.array_item_type( self.arg.type )
            , size=self.array_size)

        # Replace the input parameter with the C array
        sm.wrapper_func.input_params[self.arg_index] = self.native_array

    def wrapper_pre_call(self, sm):
        """Wrapper function code.
        """
        tmpl = []
        tmpl.append( '%(pypp_con)s::ensure_uniform_sequence< %(type)s >( %(pylist)s, %(array_size)d );' )
        tmpl.append( '%(pypp_con)s::copy_sequence( %(pylist)s, %(pypp_con)s::array_inserter( %(native_array)s, %(array_size)d ) );' )
        return os.linesep.join( tmpl ) % {
                  'type' : declarations.array_item_type( self.arg.type )
                , 'pypp_con' : 'pyplusplus::convenience'
                , 'pylist' : self.arg.name
                , 'array_size' : self.array_size
                , 'native_array' : self.native_array
        }

    def virtual_pre_call(self, sm):
        """Virtual function code."""
        tmpl = '%(pypp_con)s::copy_container( %(native_array)s, %(native_array)s + %(array_size)d, %(pypp_con)s::list_inserter( %(pylist)s ) );'
        return tmpl % { 
              'pypp_con' : 'pyplusplus::convenience'
            , 'native_array' : self.arg.name
            , 'array_size' : self.array_size
            , 'pylist' : self.pylist
        }


# output_array_t
class output_array_t(transformer.transformer_t):
    """Handles an output array of a fixed size.

    void getVec3(double* v) -> v = getVec3()
    # v will be a list with 3 floats
    """

    def __init__(self, function, arg_ref, size):
        """Constructor.

        @param idx: Index of the argument that is an output array (the first arg has index 1).
        @type idx: int
        @param size: The fixed size of the output array
        @type size: int
        """
        transformer.transformer_t.__init__( self, function )
        self.arg = self.get_argument( arg_ref )
        self.arg_index = self.function.arguments.index( self.arg )

        if not is_ptr_or_array( self.arg.type ):
            raise ValueError( '%s\nin order to use "input_array" transformation, argument %s type must be a array or a pointer (got %s).' ) \
                  % ( function, self.arg_ref.name, arg.type)

        self.array_size = size
        self.native_array = None
        self.pylist = None

    def __str__(self):
        return "output_array(%s,%d)"%( self.arg.name, self.array_size)

    def required_headers( self ):
        """Returns list of header files that transformer generated code depends on."""
        return [ code_repository.convenience.file_name ]

    def init_funcs(self, sm):
        # Remove the original argument...
        sm.remove_arg(self.arg_index + 1)

        # Declare a variable that will hold the C array...
        self.native_array = sm.wrapper_func.declare_variable(
              "native_" + self.arg.name
            , declarations.array_item_type( self.arg.type )
            , size=self.array_size)

        # Declare a Python list which will receive the output...
        self.pylist = sm.wrapper_func.declare_variable( 
              'py_' + self.arg.name
            , "boost::python::list" )
        
        # ...and add it to the result
        sm.wrapper_func.result_exprs.append(self.pylist)

        sm.wrapper_func.input_params[ self.arg_index ] = self.native_array

        self.virtual_pylist = sm.virtual_func.declare_variable("py_"+self.arg.name, "boost::python::object")
        
    def wrapper_post_call(self, sm):
        tmpl = '%(pypp_con)s::copy_container( %(native_array)s, %(native_array)s + %(array_size)d, %(pypp_con)s::list_inserter( %(pylist)s ) );'
        return tmpl % { 
              'pypp_con' : 'pyplusplus::convenience'
            , 'native_array' : self.native_array
            , 'array_size' : self.array_size
            , 'pylist' : self.pylist
        }

    def virtual_post_call(self, sm):
        tmpl = []
        tmpl.append( '%(pypp_con)s::ensure_uniform_sequence< %(type)s >( %(pylist)s, %(array_size)d );' )
        tmpl.append( '%(pypp_con)s::copy_sequence( %(pylist)s, %(pypp_con)s::array_inserter( %(native_array)s, %(array_size)d ) );' )
        return os.linesep.join( tmpl ) % {
                  'type' : declarations.array_item_type( self.arg.type )
                , 'pypp_con' : 'pyplusplus::convenience'
                , 'pylist' : sm.py_result_expr(self.pylist)
                , 'array_size' : self.array_size
                , 'native_array' : self.arg.name
        }
    
