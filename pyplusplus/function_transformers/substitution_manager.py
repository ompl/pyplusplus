# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Initial author: Matthias Baas

"""This module contains the L{substitution_manager_t} class.
"""

from pygccxml import declarations
from code_manager import code_manager_t, wrapper_code_manager_t
from function_transformer import function_transformer_t

# substitution_manager_t
class substitution_manager_t:
    """Helper class for creating C++ source code for wrapper functions.

    The class does not create the entire function source code itself
    but it maintains the individual parts that can be composed by the
    user of the class. Those individual parts are stored inside
    variables which can be used to perform text substitutions.

    Doing substitutions
    ===================

    Here is an example that demonstrates the usage of the class. The
    user creates a template string that contains the layout of the
    entire wrapper function. Such a template string may look like
    this::

      $RETTYPE $CLASSSPEC$FUNCNAME($ARGLIST)
      {
        $DECLARATIONS
        
        $PRECALL
        
        $RESULTVARASSIGNMENT$CALLFUNCNAME($INPUTPARAMS);
        
        $POSTCALL
        
        $RETURNSTMT
      }

    Any part of the function that is not fixed, i.e. that can be
    modified by argument policies, is specified via a variable. The
    substitution manager can now be used to substitute the variables with
    their actual value. There are actually two sets of identical
    variables, one for the wrapper function and one for the virtual
    function. You choose a set either by using the L{subst_wrapper()} or
    L{subst_virtual()} method for doing the substitution. For example,
    performing a "wrapper" substitution on the above template string
    might result in the following code::

      boost::python::object Spam_wrapper::foo_wrapper(Spam& self, int mode)
      {
        int result;
        int w;
        int h;
        
        result = self.foo(w, &h, mode);
        
        return boost::python::make_tuple(result, w, h);
      }

    In this example, the individual variables have the following values: 

     - RETTYPE = C{boost::python::object}
     - CLASSSPEC = C{Spam_wrapper::}
     - FUNCNAME = C{foo_wrapper}
     - ARGLIST = C{Spam& self, int mode}
     - DECLARATIONS = C{int result;\\nint w;\\nint h;}
     - PRECALL = <empty> 
     - RESULTVARASSIGNMENT = C{result =}
     - CALLFUNCNAME = C{self.foo}
     - INPUTPARAMS = C{w, &h, mode}
     - POSTCALL = <empty> 
     - RETURNSTMT = C{return boost::python::make_tuple(result, w, h);}


    Modifying the variables
    =======================

    In addition to the actual user of the class (who wants to do text
    substitutions), the class is also used by the arg policies (code blocks)
    to modify the variables.
    There are two attributes L{wrapperfunc} and L{virtualfunc} that are
    used to modify either the wrapper or the virtual function. If the
    signature of the wrapper needs modification this should be done via
    the methods L{remove_arg()} and L{insert_arg()} and not via the
    wrapperfunc or virtualfunc attributes because this affects the
    virtual function as well (because the virtual function makes a call
    to the Python function).

    Variables
    =========


     - RETTYPE: The return type (e.g. "void", "int", "boost::python::object")
 
     - CLASSSPEC: "<classname>::" or empty

     - FUNCNAME: The name of the wrapper or virtual function.

     - ARGLIST: The parameters for $FUNCNAME (including self if required)

     - ARGLISTDEF: Like ARGLIST, but including default values (if there are any)

     - ARGLISTTYPES: Like ARGLIST but the variable names are left out and only the types are listed (this can identify a particular signature).

     - DECLARATIONS: The declaration block

     - PRECALL::

         +--------------------------+
         | [try {]                  | 
         +--------------------------+
         |  Pre-call code block 1   |
         +--------------------------+
         |  Pre-call code block 2   |
         +--------------------------+
         |  ...                     |
         +--------------------------+
         |  Pre-call code block n   |
         +--------------------------+

     - RESULTVARASSIGNMENT:  "<varname> = " or empty

     - CALLFUNCNAME: The name of the function that should be invoked (self?).

     - INPUTPARAMS:  The values or variables that will be passed to $FUNCNAME,
                     e.g. "a, b" or "0.5, 1.5" etc

     - POSTCALL::

         +--------------------------+
         |  Post-call code block n  |
         +--------------------------+
         |  ...                     |
         +--------------------------+
         |  Post-call code block 2  |
         +--------------------------+
         |  Post-call code block 1  |
         +--------------------------+
         | [} catch(...) {...}]     |
         +--------------------------+

     - RETURNSTMT:  "return <varname>" or "return boost::python::make_tuple(...)"
    

    @ivar wrapperfunc: The L{code manager<code_manager_t>} object that manages the wrapper function. This is used by the arg policies to modify the wrapper function.
    @type wrapperfunc: L{wrapper_code_manager_t}
    @ivar virtualfunc: The L{code manager<code_manager_t>} object that manages the virtual function. This is used by the arg policies to modify the virtual function.
    @type virtualfunc: L{code_manager_t}
    
    @group Methods called by the user of the class: append_code_block, subst_wrapper, subst_virtual, get_includes
    @group Methods called by the arg policies: remove_arg, insert_arg, require_include

    @author: Matthias Baas
    """

    def __init__(self, decl, wrapperclass=None, transformers=None):
        """Constructor.

        @param decl: calldef declaration
        @type decl: calldef_t
        @param wrapperclass: The name of the class the generated function should belong to (or None if the generated function should be a free function)
        @type wrapperclass: str
        @param transformers: Function transformer objects
        @type transformers: list of function_transformer_t        
        """

        # Code manager for the virtual function
        self.virtualfunc = code_manager_t()
        # Code manager for the wrapper function
        self.wrapperfunc = wrapper_code_manager_t()

        # The declaration that represents the original C++ function
        self.decl = decl

        # The function transformers
        if transformers==None:
            transformers = []
        self.transformers = transformers
        
        self.wrapperclass = wrapperclass

        # A list of required include files
        self._virtual_includes = []
        self._wrapper_includes = []

        # Initialize the code managers...
        
        if str(decl.return_type)=="void":
            rettype = None
        else:
            rettype = decl.return_type
            self.wrapperfunc.resultvar = self.wrapperfunc.declare_local("result", str(rettype))
            self.wrapperfunc.resultexprs = [self.wrapperfunc.resultvar]

        self.virtualfunc.rettype = rettype
        self.virtualfunc.arglist = decl.arguments[:]
        self.virtualfunc.classname = wrapperclass
        self.virtualfunc.FUNCNAME = decl.name
        self.virtualfunc.CALLFUNCNAME = decl.name
        self.virtualfunc.inputparams = map(lambda a: a.name, decl.arguments)

        self.wrapperfunc.rettype = rettype
        self.wrapperfunc.arglist = decl.arguments[:]
        self.wrapperfunc.classname = wrapperclass
        self.wrapperfunc.FUNCNAME = "%s_wrapper"%decl.alias
        self.wrapperfunc.CALLFUNCNAME = decl.name
        self.wrapperfunc.inputparams = map(lambda a: a.name, decl.arguments)

        # Check if we're dealing with a member function...
        clsdecl = self._classDecl(decl)
        if clsdecl!=None:
            selfname = self.wrapperfunc._make_name_unique("self")
            selfarg = declarations.argument_t(selfname, "%s&"%clsdecl.name)
            self.wrapperfunc.arglist.insert(0, selfarg)
            self.wrapperfunc.CALLFUNCNAME = "%s.%s"%(selfname, self.wrapperfunc.CALLFUNCNAME)

        # Argument index map
        # Original argument index ---> Input arg index  (indices are 0-based!)
        # Initial state is the identity:  f(x) = x
        # The argument index map represents a function that maps the argument
        # index of the original C++ function to the index of the corresponding
        # parameter in the input parameter list for the Python call.
        self.argidxmap = range(len(decl.arguments))


        # Flag that is set after the functions were initialized
        self._funcs_initialized = False


    def append_transformer(self, transformer):
        """not yet implemented"""
        pass
    
    # init_funcs
    def init_funcs(self):
        """Initialize the virtual function and the wrapper function.

        After this method has been called, the substitution variables
        are ready for usage.

        It is not necessary to call this method manually, it is
        automatically called at the time a substitution is requested.
        """

        # Append the default return_virtual_result_t code modifier
        transformers = self.transformers+[return_virtual_result_t()]

        for cb in transformers:
            if hasattr(cb, "init_funcs"):
                cb.init_funcs(self)

        # Create a variable that will hold the result of the Python call
        # inside the virtual function.
        if len(self.wrapperfunc.resultexprs)>0:
            self.virtualfunc.resultvar = self.virtualfunc.declare_local("pyresult", "boost::python::object")
#            self.virtualfunc.resultexpr = self.virtualfunc.resultvar

        self.wrapperfunc.init_variables()
        self.virtualfunc.init_variables()

        self._funcs_initialized = True

        # The default method which is used when a particular method from
        # the code_base_t interface is not implemented
        defmeth = lambda x: None
        # Create the wrapper function pre-call block...
        src = map(lambda cb: getattr(cb, "wrapper_pre_call", defmeth)(self), transformers)
        src = filter(lambda x: x!=None, src)
        precall = "\n\n".join(src)
        self.wrapperfunc.PRECALL = precall

        # Create the wrapper function post-call block...
        src = map(lambda cb: getattr(cb, "wrapper_post_call", defmeth)(self), transformers)
        src = filter(lambda x: x!=None, src)
        src.reverse()
        postcall = "\n\n".join(src)
        self.wrapperfunc.POSTCALL = postcall

        # Create the virtual function pre-call block...
        src = map(lambda cb: getattr(cb, "virtual_pre_call", defmeth)(self), transformers)
        src = filter(lambda x: x!=None, src)
        precall = "\n\n".join(src)
        self.virtualfunc.PRECALL = precall

        # Create the virtual function post-call block...
        src = map(lambda cb: getattr(cb, "virtual_post_call", defmeth)(self), transformers)
        src = filter(lambda x: x!=None, src)
        src.reverse()
        postcall = "\n\n".join(src)
        self.virtualfunc.POSTCALL = postcall
            

    # remove_arg
    def remove_arg(self, idx):
        """Remove an argument from the wrapper function.

        This function can also be used to remove the original return value
        (idx=0).

        The function is supposed to be called by function transformer
        objects.

        @param idx: Argument index of the original function (may be negative)
        @type idx: int
        @returns: Returns the argument_t object that was removed (or None
          if idx is 0 and the function has no return type). You must not
          modify this object as it may still be in use on the virtual
          function.
        @rtype: argument_t
        """
        if self._funcs_initialized:
            raise ValueError, "remove_arg() may only be called before function initialization."
        if idx<0:
            idx += len(self.virtualfunc.arglist)+1
        if idx>=len(self.virtualfunc.arglist)+1:
            raise IndexError, "Index (%d) out of range."%idx

        # Remove original return type?
        if idx==0:
            if id(self.wrapperfunc.rettype)==id(self.wrapperfunc.rettype):
                self.wrapperfunc.rettype = None
            else:
                raise ValueError, 'Argument %d not found on the wrapper function'%(idx)
        # Remove argument...
        else:
            # Get the original argument...
            arg = self.virtualfunc.arglist[idx-1]
            # ...and remove it from the wrapper
            try:
                self.wrapperfunc.arglist.remove(arg)
            except ValueError:
                raise ValueError, 'Argument %d ("%s") not found on the wrapper function'%(idx, arg.name)

            # Remove the input parameter on the Python call in the
            # virtual function.
            paramidx = self.argidxmap[idx-1]
            if paramidx==None:
                raise ValueError, "Argument was already removed"
            del self.virtualfunc.inputparams[paramidx]
            self.argidxmap[idx-1] = None
            for i in range(idx,len(self.argidxmap)):
                if self.argidxmap[i]!=None:
                    self.argidxmap[i] -= 1
            
            return arg

    # insert_arg
    def insert_arg(self, idx, arg):
        """Insert a new argument into the argument list of the wrapper function.

        This function is supposed to be called by function transformer
        objects.
        
        @param idx: New argument index (may be negative)
        @type idx: int
        @param arg: New argument object
        @type arg: argument_t
        """
        if self._funcs_initialized:
            raise ValueError, "insert_arg() may only be called before function initialization."
        if idx==0:
            pass
        else:
            if idx<0:
                idx += len(self.wrapperfunc.arglist)+2
            self.wrapperfunc.arglist.insert(idx-1, arg)

            # What to insert?
            self.virtualfunc.inputparams.insert(idx-1, "???")
            # Adjust the argument index map
            for i in range(idx-1,len(self.argidxmap)):
                if self.argidxmap[i]!=None:
                    self.argidxmap[i] += 1

    # require_include
    def require_include(self, include, where=None):
        """Declare an include file that is required for the code to compile.

        This function is supposed to be called by function transformer
        objects to tell the substitution manager that they create code
        that requires a particular header file.

        include is the name of the include file which may contain <> or ""
        characters around the name. 

        @param include: The name of the include file (may contain <> or "")
        @type include: str
        @param where: "wrapper", "virtual" or None (for both)
        @type where: str
        """
        if where not in ["wrapper", "virtual", None]:
            raise ValueError, "Invalid 'where' argument: %s"%where

        if include=="":
            return

        # Add apostrophes if there aren't any already
        if include[0] not in '"<':
            include = '"%s"'%include
            
        if where=="wrapper" or where==None:
            if include not in self._wrapper_includes:
                self._wrapper_includes.append(include)
                
        if where=="virtual" or where==None:
            if include not in self._virtual_includes:
                self._virtual_includes.append(include)                
            
    # get_includes
    def get_includes(self, where=None):
        """Return a list of include files required for the wrapper and/or the virtual function.

        @param where: "wrapper", "virtual" or None (for a combined list)
        @type where: str
        @return: A list of include file names (all names contain <> or "")
        @rtype: list of str
        """
        if where not in ["wrapper", "virtual", None]:
            raise ValueError, "Invalid 'where' argument: %s"%where

        if where=="wrapper":
            return self._wrapper_includes[:]

        if where=="virtual":
            return self._virtual_includes[:]

        # Merge both lists (without duplicating names)
        res = self._virtual_includes[:]
        for inc in self._wrapper_includes:
            if inc not in res:
                res.append(inc)

        return res

    # subst_virtual
    def subst_virtual(self, template):
        """Perform a text substitution using the "virtual" variable set.

        @return: Returns the input string that has all variables substituted.
        @rtype: str
        """
        if not self._funcs_initialized:
            self.init_funcs()
        return self.virtualfunc.substitute(template)

    # subst_wrapper
    def subst_wrapper(self, template):
        """Perform a text substitution using the "wrapper" variable set.

        @return: Returns the input string that has all variables substituted.
        @rtype: str        
        """
        if not self._funcs_initialized:
            self.init_funcs()
        return self.wrapperfunc.substitute(template)

    # _classDecl
    def _classDecl(self, decl):
        """Return the class declaration that belongs to a member declaration.
        """
        while decl.parent!=None:
            parent = decl.parent
            if isinstance(parent, declarations.class_t):
                return parent
            decl = parent
        return None


# return_virtual_result_t
class return_virtual_result_t(function_transformer_t):
    """Extract and return the result value of the virtual function.

    This is an internal code block object that is automatically appended
    to the list of code blocks inside the substitution_manager_t class.
    """

    def __init__(self):
        function_transformer_t.__init__(self)
        self.resultvar = "<not initialized>"

    def __str__(self):
        return "ReturnVirtualResult()"%(self.idx)

    def init_funcs(self, sm):
        if sm.virtualfunc.rettype==None:
            return
        
        # Declare the local variable that will hold the return value
        # for the virtual function
        self.resultvar = sm.virtualfunc.declare_local("result", sm.virtualfunc.rettype)
        # Replace the result expression if there is still the default
        # result expression (which will not work anyway)
        if sm.virtualfunc.resultexpr==sm.virtualfunc.resultvar:
            sm.virtualfunc.resultexpr = self.resultvar

    def virtual_post_call(self, sm):
        # Search the result tuple of the wrapper function for the return
        # value of the C++ function call. If the value exists it is extracted
        # from the Python result tuple, converted to C++ and returned from
        # the virtual function. If it does not exist, do nothing.
        try:
            resultidx = sm.wrapperfunc.resultexprs.index(sm.wrapperfunc.resultvar)
        except ValueError:
            return
        
        res = "// Extract the C++ return value\n"
        res += "%s = boost::python::extract<%s>(%s[%d]);"%(self.resultvar, sm.virtualfunc.rettype, sm.virtualfunc.resultvar, resultidx)
        return res        


######################################################################
if __name__=="__main__":
    import pyplusplus
    from pygccxml import parser
    from arg_policies import Output
    cpp = """
    class Spam
    {
      public:
      int foo(int& w, int* h, int mode=0);
    };
    """
    parser = parser.project_reader_t(parser.config.config_t(),
                                     decl_factory=pyplusplus.decl_wrappers.dwfactory_t())
    root = parser.read_string(cpp) 
    spam = root[0].class_("Spam")
    foo = spam.member_function("foo")

    wm = substitution_manager_t(foo, transformers=[Output(1), Output(2)], wrapperclass="Spam_wrapper")

    template = '''$RETTYPE $CLASSSPEC$FUNCNAME($ARGLIST)
{
  $DECLARATIONS

  $PRECALL

  $RESULTVARASSIGNMENT$CALLFUNCNAME($INPUTPARAMS);

  $POSTCALL

  $RETURNSTMT
}
'''
    print wm.subst_virtual(template)
    print wm.subst_wrapper(template)
    print wm.get_includes()
    print wm.get_includes("virtual")
    print wm.get_includes("wrapper")
