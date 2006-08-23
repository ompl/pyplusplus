# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#
# Authors:
#   Allen Bierbaum
#
import pygccxml.declarations as pd
from pyplusplus.module_builder.call_policies import *
import pygccxml.declarations.type_traits as tt
import pygccxml.declarations.cpptypes as cpptypes
import pyplusplus.code_creators as code_creators
import pyplusplus.decl_wrappers as decl_wrappers


def set_recursive_default(val):
    pd.scopedef_t.RECURSIVE_DEFAULT = val

#[Roman]The better way is to turn virtuality from virtual to non virtual
def finalize(cls):
    """ Attempt to finalize a class by not exposing virtual methods.
            Still exposes in the case of pure virtuals otherwise the class
            could not be instantiated.
    """
    members = cls.decls( pd.virtuality_type_matcher( pd.VIRTUALITY_TYPES.VIRTUAL )
                         , decl_type=pd.member_calldef_t
                         , allow_empty=True)
    members.set_virtuality( pd.VIRTUALITY_TYPES.NOT_VIRTUAL ) 


def add_member_function(cls, methodName, newMethod):
    """ Add a member function to the class. """
    cls.add_registration_code('def("%s",%s)'%(methodName, newMethod), True)

def wrap_method(cls, methodName, newMethod):
    """ Wrap a class method with a new method.
            ex: c.wrapmethod(c,"doSomething","doSomethingWrapper")
    """
    cls[methodName].exclude()
    add_member_function(cls, methodName, newMethod)

def add_method(moduleBuilder, methodName, method):
    """  Add a method to the module builder. """
    code_text = 'boost::python::def("%s",%s);'%(methodName, method)
    moduleBuilder.code_creator.body.adopt_creator( code_creators.custom_text_t( code_text ), 0 )
    #[Roman]moduleBuilder.add_registration_code( ... ), see relevant documentation
    #This will add have exactly same effect as a previous line, also you don't
    #have to build code creator first


def is_const_ref(type):
    """ Extra trait tester method to check if something is a const reference. """
    is_const = tt.is_const(type) or (hasattr(type,'base') and tt.is_const(type.base))
    is_ref = tt.is_reference(type) or (hasattr(type,'base') and tt.is_reference(type.base))
    return (is_ref and is_const)
    #[Roman]If you create unit tests for this code, I will add it to type traits module

def exclude_protected(cls):
    """ Exclude all protected declarations. """
    cls.decls(pd.access_type_matcher_t('protected'),allow_empty=True).exclude()

def wrap_const_ref_params(cls):
    """ Find all member functions of cls and if they take a const& to a class
            that does not have a destructor, then create a thin wrapper for them.
            This works around an issue with boost.python where it needs a destructor.
    """
    #[Roman] Obviously, this will only work, if the function does not need other
    #wrapper, I think, this is a new use case for Matthias "arguments policies"
    #functionality.
    calldefs = cls.calldefs()

    if None == calldefs:
        return

    for c in calldefs:
        # Skip constructors
        if isinstance(c, pd.constructor_t):
            continue

        # Find arguments that need replacing
        args_to_replace = []   # List of indices to args to replace with wrapping
        args = c.arguments
        for i in range(len(args)):
            arg = args[i]
            if is_const_ref(arg.type):
                naked_arg = tt.remove_cv(tt.remove_reference(arg.type))
                if tt.is_class(naked_arg):
                    class_type = naked_arg.declaration
                    if not tt.has_public_destructor(class_type):
                        print "Found indestructible const& arg: [%s]:[%s] "%(str(c), str(arg))
                        args_to_replace.append(i)

        # Now replace arguments
        if len(args_to_replace):
            if isinstance(c, pd.operator_t) and c.symbol in ["<","==","!=","="]:
                c.exclude()
                continue

            new_args = copy.copy(args)   # Make new copy of args so we don't modify the existing method
            for i in args_to_replace:
                old_arg_type = args[i].type
                if tt.is_reference(old_arg_type) and tt.is_const(old_arg_type.base):
                    new_args[i].type = cpptypes.reference_t(tt.remove_const(old_arg_type.base))
                elif tt.is_const(old_arg):
                    new_args[i].type = tt.remove_const(old_arg_type)

            new_name = "%s_const_ref_wrapper"%c.name
            args_str = [str(a) for a in new_args]
            arg_names_str = [str(a.name) for a in new_args]
            new_sig = "static %s %s(%s& self_arg, %s)"%(c.return_type,new_name,cls.name,",".join(args_str))
            new_method = """%s
            { return self_arg.%s(%s); }
            """%(new_sig,c.name,",".join(arg_names_str))

            # Add it all
            c.exclude()
            
            #[Roman] you can use cls.add_declaration_code, this could simplify the
            #wrapper ou created, because it will generate the code within the source
            #file, the class is generated
            cls.add_wrapper_code(new_method)
            
            cls.add_code('def("%s", &%s::%s);'%(c.name, cls.wrapper_alias,new_name))
