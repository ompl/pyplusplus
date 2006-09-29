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
    instance variables below). The final variables (such as RET_TYPE,
    FUNC_NAME, ARG_LIST, etc.) are stored as regular attributes of the
    object.    

    The functionality to perform a text substitution (using the
    substitution() method) is inherited
    from the class L{subst_t}.

    @ivar class_name: The name of the class of which the generated function is a member. A value of None or an empty string is used for free functions. This attribute is used for creating the CLASS_SPEC variable.
    @type class_name: str
    @ivar ret_type: Return type. The value may be any object where str(obj) is valid C++ code. The value None corresponds to void. This will be the value of the variable RET_TYPE.
    @type ret_type: str
    @ivar arg_list: The argument list. The items are pygccxml argument_t objects. This list will appear in the variables ARG_LIST, ARG_LIST_DEF and ARG_LIST_TYPES.
    @type arg_list: list of L{argument_t<pygccxml.declarations.calldef.argument_t>}
    @ivar input_params: A list of strings that contain the input parameter for the function call. This list is used for the INPUT_PARAMS variable.
    @type input_params: list of str
    @ivar result_var: The name of the variable that will receive the result of the function call. If None, the return value is ignored. This attribute will be used for the variable RESULT_VAR_ASSIGNMENT.
    @type result_var: str
    @ivar result_type: The type of the variable 'result_var'
    @type result_type: str
    @ivar result_expr: A string containing the expression that will be put after the "return" statement. This expression is used for the variable RETURN_STMT.
    @type result_expr: str
    @ivar exception_handler_exit: The C++ code that is executed at the end of the main exception handler (default: "throw;").
    @type exception_handler_exit: str

    @author: Matthias Baas
    """

    def __init__(self):
        """Constructor.
        """
        subst_t.__init__(self, blockvars=["DECLARATIONS",
                                          "PRE_CALL",
                                          "POST_CALL",
                                          "EXCEPTION_HANDLER_EXIT"])

        # The name of the class of which the generated function is a member
        # (pass None or an empty string if the function is a free function)
        self.class_name = None

        # Return type (the value may be any object where str(obj) is valid
        # C++ code. The value None corresponds to "void").
        self.ret_type = None
        # The argument list. The items are argument_t objects.
        self.arg_list = []

        # A list of strings that contain the input parameter for the
        # function call
        self.input_params = []

        # The name of the variable that will receive the result of the
        # function call. If None, the return value is ignored.
        self.result_var = None

        # The type of 'result_var'
        self.result_type = "void"

        # A string containing the expression that will be put after
        # the "return" statement.
        self.result_expr = None

        # The C++ code that is executed at the end of the main
        # exception handler.
        self.exception_handler_exit = "throw;"

        # Key:Variable name / Value:1
        self._allocated_vars = {}
        # Key:Variable name / Value:(type,size,default)
        self._declared_vars = {}
        # A list with variable tuples: (name, type, size, default)
        self._local_var_list = []

        # Required header file names
        self._required_headers = []

    # require_header
    def require_header(self, include):
        """Declare an include file that is required for the code to compile.

        include is the name of the include file which may contain <> or ""
        characters around the name (which are currently ignored).
        If an include file is declared twice it will only be added once.

        @param include: The name of the include file (may contain <> or "")
        @type include: str
        """
        if include=="":
            return

        # Add apostrophes if there aren't any already
        if include[0] in '"<':
            include = include[1:-1]

        if include not in self._required_headers:
            self._required_headers.append(include)

    # get_required_headers
    def get_required_headers(self, where=None):
        """Return a list of include files required for the function.

        @return: A list of include file names
        @rtype: list of str
        """
        return self._required_headers

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
        name = self.allocate_local(name)
        self._declared_vars[name] = (type,size,default)
        self._local_var_list.append((name, type, size, default))
        return name

    # allocate_local
    def allocate_local(self, name):
        """Allocate a local variable name and return the final name.

        Allocate a variable name that is unique to the entire
        function.  The variable will not appear in the DECLARATIONS
        block. Instead, the caller has to generate the declaration
        code himself at an appropriate place.

        @param name: The desired variable name
        @type name: str
        @return: The assigned variable name (which is guaranteed to be unique)
        @rtype: str
        """
        name = self._make_name_unique(name)
        self._allocated_vars[name] = 1
        return name    

    # is_defined
    def is_defined(self, name):
        """Check if a variable name is already in use.

        The method returns True if name is the name of an argument or of
        a local variable.

        @rtype: bool
        """
        if name in self._allocated_vars:
            return True
        if filter(lambda a: a.name==name, self.arg_list):
            return True
        return False

    def local_type_str(self, name):
        """Return the type of a local variable.

        An exception is raised if a variable called name does not exist.

        @return: Returns the type of the specified local variable.
        @rtype: str
        """
        if name not in self._allocated_vars:
            raise ValueError, 'The type of local variable "%s" is unknown.'%name
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

        # CLASS_SPEC
        if (self.class_name in [None, ""]):
            self.CLASS_SPEC = ""
        else:
            self.CLASS_SPEC = "%s::"%self.class_name

        # RET_TYPE
        if self.ret_type==None:
            self.RET_TYPE = "void"
        else:
            self.RET_TYPE = str(self.ret_type)

        # ARG_LIST_DEF
        args = map(lambda a: str(a), self.arg_list)
        self.ARG_LIST_DEF = ", ".join(args)

        # ARG_LIST
        args = map(lambda s: s.split("=")[0], args)
        self.ARG_LIST = ", ".join(args)

        # ARG_LIST_TYPES
        args = map(lambda a: str(a.type), self.arg_list)
        self.ARG_LIST_TYPES = ", ".join(args)

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

        # RESULT_VAR_ASSIGNMENT
        if self.result_var!=None:
            self.RESULT_VAR_ASSIGNMENT = "%s = "%self.result_var
#            self.RESULT_VAR_ASSIGNMENT = "%s %s = "%(self.result_type, self.result_var)
        else:
            self.RESULT_VAR_ASSIGNMENT = ""

        # RESULT_TYPE
        if self.result_type!=None:
            self.RESULT_TYPE = str(self.result_type)
        else:
            self.RESULT_TYPE = ""

        # INPUT_PARAMS
        self.INPUT_PARAMS = ", ".join(self.input_params)

        # RETURN_STMT
        if self.result_expr!=None:
            self.RETURN_STMT = "return %s;"%self.result_expr
        else:
            self.RETURN_STMT = ""

        # EXCEPTION_HANDLER_EXIT
        if self.exception_handler_exit!=None:
            self.EXCEPTION_HANDLER_EXIT = self.exception_handler_exit
        else:
            self.EXCEPTION_HANDLER_EXIT = ""

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
    several values, so this class provides the extra attribute "result_exprs"
    which is a list of individual expressions. Apart from that this
    class is identical to L{code_manager_t}.

    @ivar result_exprs: Similar to result_expr but this list variable can contain more than just one result. The items can be either strings containing the variable names (or expressions) that should be returned or it can be an L{argument_t<pygccxml.declarations.calldef.argument_t>} object (usually from the argument list of the virtual function) whose name attribute will be used. This attribute only exists on the code manager for the wrapper function (the virtual function cannot return several values, use result_expr instead).
    @type result_exprs: list of str or L{argument_t<pygccxml.declarations.calldef.argument_t>}
    """

    def __init__(self):
        """Constructor.
        """
        code_manager_t.__init__(self)

        # Similar to result_expr but now there can be more than just one result
        # The items can be either strings containing the variable names (or
        # expressions) that should be returned or it can be an argument_t
        # object (usually from the argument list of the virtual function)
        # whose name attribute will be used.
        self.result_exprs = []

    def init_variables(self):
        """Initialize the substitution variables.
        """

        # Prepare the variables for RET_TYPE and RETURN_STMT...

        # Convert all items into strings
        result_exprs = []
        for re in self.result_exprs:
            # String?
            if isinstance(re, types.StringTypes):
                result_exprs.append(re)
            # argument_t
            else:
                result_exprs.append(re.name)

        if self.result_expr==None:
            # No output values?
            if len(result_exprs)==0:
                self.ret_type = None
                self.result_expr = None
            # Exactly one output value?
            elif len(result_exprs)==1:
                self.ret_type = "boost::python::object"
                self.result_expr = "boost::python::object(%s)"%result_exprs[0]
##                self.result_expr = self.result_exprs[0]
##                try:
##                    # Try to determine the type of the result expression
##                    # (assuming it's just a local variable)
##                    self.ret_type = self.local_type_str(self.result_expr)
##                except:
##                    # if the above fails, return a generic Python object
##                    self.ret_type = "boost::python::object"
##                    self.result_expr = "boost::python::object(%s)"%result_exprs[0]
            # More than one output value...
            else:
                self.ret_type = "boost::python::object"
                self.result_expr = "boost::python::make_tuple(%s)"%(", ".join(result_exprs))

        # Invoke the inherited method that sets the actual variables
        code_manager_t.init_variables(self)


