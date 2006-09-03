# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Initial author: Matthias Baas

"""This module contains the L{code_manager_t} and L{wrapper_code_manager_t} classes.
"""

import types
from subst import subst_t

# code_manager_t
class code_manager_t(subst_t):
    """This class manages pieces of source code for a C++ function.

    The class mainly provides the interface for the code blocks to
    manipulate a function and stores the actual substitution variables.
    Each function has its own code manager instance.

    A code block can declare a local variable using L{declare_local()}
    and it can manipulate one of the attributes that are used to
    initialize the final variables (see the documentation of the
    instance variables below). The final variables (such as RETTYPE,
    FUNCNAME, ARGLIST, etc.) are stored as regular attributes of the
    object.    

    The functionality to perform a text substitution (using the
    substitution() method) is inherited
    from the class L{subst_t}.

    @ivar classname: The name of the class of which the generated function is a member. A value of None or an empty string is used for free functions. This attribute is used for creating the CLASSSPEC variable.
    @type classname: str
    @ivar rettype: Return type. The value may be any object where str(obj) is valid C++ code. The value None corresponds to void. This will be the value of the variable RETTYPE.
    @type rettype: str
    @ivar arglist: The argument list. The items are pygccxml argument_t objects. This list will appear in the variables ARGLIST, ARGLISTDEF and ARGLISTTYPES.
    @type arglist: list of argument_t
    @ivar inputparams: A list of strings that contain the input parameter for the function call. This list is used for the INPUTPARAMS variable.
    @type inputparams: list of str
    @ivar resultvar: The name of the variable that will receive the result of the function call. If None, the return value is ignored. This attribute will be used for the variable RESULTVARASSIGNMENT.
    @type resultvar: str
    @ivar resultexpr: A string containing the expression that will be put after the "return" statement. This expression is used for the variable RETURNSTMT.
    @type resultexpr: str

    @author: Matthias Baas
    """

    def __init__(self):
        """Constructor.
        """
        subst_t.__init__(self, blockvars=["DECLARATIONS",
                                          "PRECALL",
                                          "POSTCALL"])

        # The name of the class of which the generated function is a member
        # (pass None or an empty string if the function is a free function)
        self.classname = None

        # Return type (the value may be any object where str(obj) is valid
        # C++ code. The value None corresponds to "void").
        self.rettype = None
        # The argument list. The items are argument_t objects.
        self.arglist = []

        # A list of strings that contain the input parameter for the
        # function call
        self.inputparams = []

        # The name of the variable that will receive the result of the
        # function call. If None, the return value is ignored.
        self.resultvar = None

        # A string containing the expression that will be put after
        # the "return" statement.
        self.resultexpr = None

        # Key:Variable name / Value:(type,size,default)
        self._declared_vars = {}
        # A list with variable tuples: (name, type, size, default)
        self._local_var_list = []

    # declare_local
    def declare_local(self, name, type, size=None, default=None):
        """Declare a local variable and return its final name.

        @param name: The desired variable name
        @type name: str
        @param type: The type of the variable (must be valid C++ code)
        @type type: str
        @param size: The array length or None
        @type size: int
        @param default: The default value (must be valid C++ code) or None
        @type default: str
        @return: The assigned variable name (which is guaranteed to be unique)
        @rtype: str
        """
        name = self._make_name_unique(name)
        self._declared_vars[name] = (type,size,default)
        self._local_var_list.append((name, type, size, default))
        return name

    def is_defined(self, name):
        """Check if a variable name is already in use.

        The method returns True if name is the name of an argument or of
        a local variable.

        @rtype: bool
        """
        if name in self._declared_vars:
            return True
        if filter(lambda a: a.name==name, self.arglist):
            return True
        return False

    def local_type_str(self, name):
        """Return the type of a local variable.

        An exception is raised if a variable called name does not exist.

        @return: Returns the type of the specified local variable.
        @rtype: str
        """
        if name not in self._declared_vars:
            raise ValueError, 'Local variable "%s" not found.'%name

        type,size,default = self._declared_vars[name]
        
        if size==None:
            return type
        else:
            return "*%s"%type

    def init_variables(self):
        """Initialize the substitution variables.

        Based on the (lowercase) attributes, the final (uppercase)
        variables are created. Those variables are regular string
        attributes.
        """

        # CLASSSPEC
        if (self.classname in [None, ""]):
            self.CLASSSPEC = ""
        else:
            self.CLASSSPEC = "%s::"%self.classname

        # RETTYPE
        if self.rettype==None:
            self.RETTYPE = "void"
        else:
            self.RETTYPE = str(self.rettype)

        # ARGLISTDEF
        args = map(lambda a: str(a), self.arglist)
        self.ARGLISTDEF = ", ".join(args)

        # ARGLIST
        args = map(lambda s: s.split("=")[0], args)
        self.ARGLIST = ", ".join(args)

        # ARGLISTTYPES
        args = map(lambda a: str(a.type), self.arglist)
        self.ARGLISTTYPES = ", ".join(args)

        # Create the declaration block -> DECLARATIONS
        vardecls = []
        for varname,type,size,default in self._local_var_list:
            if default==None:
                vd = "%s %s"%(type, varname)
            else:
                vd = "%s %s = %s"%(type, varname, default)
            if size!=None:
                vd += "[%d]"%size
            vardecls.append(vd+";")
        self.DECLARATIONS = "\n".join(vardecls)

        # RESULTVARASSIGNMENT
        if self.resultvar!=None:
            self.RESULTVARASSIGNMENT = "%s = "%self.resultvar

        # INPUTPARAMS
        self.INPUTPARAMS = ", ".join(self.inputparams)

        # RETURNSTMT
        if self.resultexpr!=None:
            self.RETURNSTMT = "return %s;"%self.resultexpr

    # _make_name_unique
    def _make_name_unique(self, name):
        """Make a variable name unique so that there's no clash with other names.

        @param name: The variable name that should be unique
        @type name: str
        @return: A unique name based on the input name
        @rtype: str
        """
        if not self.is_defined(name):
            return name

        n = 2
        while 1:
            newname = "%s_%d"%(name, n)
            if not self.is_defined(newname):
                return newname
            n += 1


# wrapper_code_manager_t
class wrapper_code_manager_t(code_manager_t):
    """The CodeManager class for the wrapper function.

    In contrast to a regular C++ function a Python function can return
    several values, so this class provides the extra attribute "resultexprs"
    which is a list of individual expressions. Apart from that this
    class is identical to L{code_manager_t}.

    @ivar resultexprs: Similar to resultexpr but this list variable can contain more than just one result. The items can be either strings containing the variable names (or expressions) that should be returned or it can be an argument_t object (usually from the argument list of the virtual function) whose name attribute will be used. This attribute only exists on the code manager for the wrapper function (the virtual function cannot return several values, use resultexpr instead).
    @type resultexprs: list of str or argument_t
    """

    def __init__(self):
        """Constructor.
        """
        code_manager_t.__init__(self)

        # Similar to resultexpr but now there can be more than just one result
        # The items can be either strings containing the variable names (or
        # expressions) that should be returned or it can be an argument_t
        # object (usually from the argument list of the virtual function)
        # whose name attribute will be used.
        self.resultexprs = []

    def init_variables(self):
        """Initialize the substitution variables.
        """

        # Prepare the variables for RETTYPE and RETURNSTMT...

        # Convert all items into strings
        resultexprs = []
        for re in self.resultexprs:
            # String?
            if isinstance(re, types.StringTypes):
                resultexprs.append(re)
            # argument_t
            else:
                resultexprs.append(re.name)
        
        # No output values?
        if len(resultexprs)==0:
            self.rettype = None
            self.resultexpr = None
        # Exactly one output value?
        elif len(resultexprs)==1:
            self.rettype = "boost::python::object"
            self.resultexpr = "boost::python::object(%s)"%resultexprs[0]
        # More than one output value...
        else:
            self.rettype = "boost::python::object"
            self.resultexpr = "boost::python::make_tuple(%s)"%(", ".join(resultexprs))

        # Invoke the inherited method that sets the actual variables
        code_manager_t.init_variables(self)


