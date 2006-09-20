# Copyright 2004 Roman Yakovenko
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
#import algorithm
#import code_creator
#import class_declaration
from pygccxml import declarations
from calldef import calldef_t, calldef_wrapper_t
import pyplusplus.function_transformers as function_transformers

######################################################################

class mem_fun_transformed_t( calldef_t ):
    """Creates code for public non-virtual member functions.
    """
    
    def __init__( self, function, wrapper=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )

    def create_function_type_alias_code( self, exported_class_alias=None  ):
        if self.wrapper==None:
            ftype = self.declaration.function_type()
        else:
            ftype = self.wrapper.function_type()
        res = 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )
        return res

    def create_function_ref_code(self, use_function_alias=False):
        if self.wrapper:
            full_name = self.wrapper.full_name()
        else:
            full_name = declarations.full_name( self.declaration )
            
        if use_function_alias:
            return '%s( &%s )' \
                   % ( self.function_type_alias, full_name )
        elif self.declaration.create_with_signature:
            if self.wrapper:
                func_type = self.wrapper.function_type()
            else:
                func_type = self.declaration.function_type().decl_string
            return '(%s)( &%s )' \
                   % ( func_type, full_name )
        else:
            return '&%s' % full_name


class mem_fun_transformed_wrapper_t( calldef_wrapper_t ):
    """Creates wrapper code for (public) non-virtual member functions.

    The generated function is either used as a static member inside the
    wrapper class (when self.parent is not None) or as a free function
    (when self.parent is None).
    """

    def __init__( self, function ):
        """Constructor.

        @param function: Function declaration
        @type function: calldef_t
        """
        calldef_wrapper_t.__init__( self, function=function )

#    def is_free_function(self):
#        """Return True if the generated function is a free function.
#
#        @rtype: bool
#        """
#        return self.parent==None

    def function_type(self):
        """Return the type of the wrapper function.

        @rtype: type_t
        """
        template = '$RET_TYPE'
        rettype = self._subst_manager.subst_wrapper(template)
        rettype = declarations.dummy_type_t(rettype)

        return declarations.free_function_type_t(
                return_type=rettype
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments ) )

        
    def full_name(self):
        """Return the full name of the wrapper function.

        The returned name also includes the class name (if there is any).

        @rtype: str
        """
        if self.parent==None:
            return '_py_' + self.declaration.alias
        else:
            return self.parent.full_name + '::_py_' + self.declaration.alias

    def create_sig_id(self):
        """Create an ID string that identifies a signature.

        @rtype: str
        """
        template = '%s($ARG_LIST_TYPES)'%self.declaration.alias
        return self._subst_manager.subst_wrapper(template)

    def create_declaration(self, name):
        """Create the function header.
        """
        template = 'static $RET_TYPE %(name)s( $ARG_LIST_DEF ) %(throw)s'

        # Substitute the $-variables
        template = self._subst_manager.subst_wrapper(template)

        return template % {
            'name' : "_py_"+name
            , 'throw' : self.throw_specifier_code()
        }

    def create_body(self):

        body = """
$DECLARATIONS

$PRE_CALL
  
$RESULT_VAR_ASSIGNMENT$CALL_FUNC_NAME($INPUT_PARAMS);
  
$POST_CALL
  
$RETURN_STMT
"""

        # Replace the $-variables
        body = self._subst_manager.subst_wrapper(body)

        return body

    def create_function(self):
#        sig_id = self.create_sig_id()
        # ...check sig here...

        answer = [70*"/"]
        answer.append("// Transformed wrapper function for:")
        answer.append("// %s"%self.declaration)
        answer.append(70*"/")
        answer.append( self.create_declaration(self.declaration.alias) + '{')
        answer.append( self.indent( self.create_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def _create_impl(self):
        # Create the substitution manager
        decl = self.declaration
        sm = function_transformers.substitution_manager_t(decl, transformers=decl.function_transformers)
        self._subst_manager = sm
    
        answer = self.create_function()

        # Replace the argument list of the declaration so that in the
        # case that keywords are created, the correct arguments will be
        # picked up (i.e. the modified argument list and not the original
        # argument list)
        self.declaration.arguments = self._subst_manager.wrapper_func.arg_list

        return answer

######################################################################

class mem_fun_v_transformed_t( calldef_t ):
    """Creates code for (public) virtual member functions.
    """
    
    def __init__( self, function, wrapper=None ):
        calldef_t.__init__( self, function=function, wrapper=wrapper )
        self.default_function_type_alias = 'default_' + self.function_type_alias

    def create_function_type_alias_code( self, exported_class_alias=None ):
        if self.wrapper==None:
            ftype = self.declaration.function_type()
        else:
            ftype = self.wrapper.function_type()

        result = []
        result.append( 'typedef %s;' % ftype.create_typedef( self.function_type_alias, exported_class_alias )  )
        return ''.join( result )

    def create_doc(self):
        return None

    def create_function_ref_code(self, use_function_alias=False):
        if self.wrapper:
            full_name = self.wrapper.default_full_name()
        else:
            full_name = declarations.full_name( self.declaration )

        result = []
        if use_function_alias:
            result.append( '%s(&%s)'
                           % ( self.function_type_alias, full_name ) )
        elif self.declaration.create_with_signature:
            if self.wrapper:
                func_type = self.wrapper.function_type()
            else:
                func_type = self.declaration.function_type().decl_string
            result.append( '(%s)(&%s)'
                           % ( func_type, full_name ) )
        else:
            result.append( '&%s' % full_name )

        return ''.join( result )


class mem_fun_v_transformed_wrapper_t( calldef_wrapper_t ):
    """Creates wrapper code for (public) virtual member functions.

    The generated code consists of two functions: the virtual function
    and the 'default' function.
    """

    def __init__( self, function ):
        """Constructor.

        @param function: Function declaration
        @type function: calldef_t
        """
        calldef_wrapper_t.__init__( self, function=function )
        
        # Stores the name of the variable that holds the override
        self._override_var = None
        # Stores the name of the 'gstate' variable
        self._gstate_var = None

    def default_name(self):
        """Return the name of the 'default' function.

        @rtype: str
        """
        return "default_" + self.declaration.alias

    def default_full_name(self):
        """Return the full name of the 'default' function.

        The returned name also includes the class name.

        @rtype: str
        """
        return self.parent.full_name + '::default_' + self.declaration.alias

    def virtual_name(self):
        """Return the name of the 'virtual' function.

        @rtype: str
        """
        return self.declaration.name

    def base_name(self):
        """Return the name of the 'base' function.

        @rtype: str
        """
        return "base_" + self.declaration.name

    def function_type(self):
        template = '$RET_TYPE'
        rettype = self._subst_manager.subst_wrapper(template)
        rettype = declarations.dummy_type_t(rettype)

        return declarations.free_function_type_t(
                return_type=rettype
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments ) )

        return declarations.member_function_type_t(
                return_type=self.declaration.return_type
                , class_inst=declarations.dummy_type_t( self.parent.full_name )
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def create_declaration(self, name, virtual=True):
        """Create the function header.

        This method is used for the virtual function (and the base_ function),
        but not for the default function.
        """
        template = '%(virtual)s$RET_TYPE %(name)s( $ARG_LIST_DEF )%(constness)s %(throw)s'

        # Substitute the $-variables
        template = self._subst_manager.subst_virtual(template)

        virtualspec = ''
        if virtual:
            virtualspec = 'virtual '

        constness = ''
        if self.declaration.has_const:
            constness = ' const '

        return template % {
            'virtual' : virtualspec
            , 'name' : name
            , 'constness' : constness
            , 'throw' : self.throw_specifier_code()
        }

    def create_base_body(self):
        body = "%(return_)s%(wrapped_class)s::%(name)s( %(args)s );"

        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '

        return body % {
              'name' : self.declaration.name
            , 'args' : self.function_call_args()
            , 'return_' : return_
            , 'wrapped_class' : self.wrapped_class_identifier()
        }

    def create_virtual_body(self):

        thread_safe = getattr(self.declaration, "thread_safe", False)
        
        if thread_safe:
            body = """
pyplusplus::gil_state_t %(gstate_var)s;

%(gstate_var)s.ensure();
boost::python::override %(override_var)s = this->get_override( "%(alias)s" );
%(gstate_var)s.release();

if( %(override_var)s )
{
  // The corresponding release() is done in the destructor of %(gstate_var)s
  %(gstate_var)s.ensure();

  $DECLARATIONS

  try {   
    $PRE_CALL
  
    ${RESULT_VAR_ASSIGNMENT}boost::python::call<$RESULT_TYPE>($INPUT_PARAMS);
  
    $POST_CALL  

    $RETURN_STMT  
  }
  catch(...)
  {
    if (PyErr_Occurred())
    {
      PyErr_Print();
    }
    
    $CLEANUP
    
    $EXCEPTION_HANDLER_EXIT
  }
}
else
{
  %(inherited)s
}
"""

        if not thread_safe:
            body = """
boost::python::override %(override_var)s = this->get_override( "%(alias)s" );

if( %(override_var)s )
{
  $DECLARATIONS
  
  $PRE_CALL

  ${RESULT_VAR_ASSIGNMENT}boost::python::call<$RESULT_TYPE>($INPUT_PARAMS);

  $POST_CALL

  $RETURN_STMT
}
else
{
  %(inherited)s
}
"""

        vf = self._subst_manager.virtual_func
        arg0 = "%s.ptr()"%self._override_var
        if vf.INPUT_PARAMS=="":
            vf.INPUT_PARAMS = arg0
        else:
            vf.INPUT_PARAMS = arg0+", "+vf.INPUT_PARAMS

        # Replace the $-variables
        body = self._subst_manager.subst_virtual(body)

#        template = []
#        template.append( 'if( %(override)s func_%(alias)s = this->get_override( "%(alias)s" ) )' )
#        template.append( self.indent('%(return_)sfunc_%(alias)s( %(args)s );') )
#        template.append( 'else' )
#        template.append( self.indent('%(return_)s%(wrapped_class)s::%(name)s( %(args)s );') )
#        template = os.linesep.join( template )

        return body % {
#            'override' : self.override_identifier()
            'override_var' : self._override_var
            , 'gstate_var' : self._gstate_var
            , 'alias' : self.declaration.alias
#            , 'func_var' : "func_"+self.declaration.alias
            , 'inherited' : self.create_base_body()
        }

    def create_default_body(self):
        cls_wrapper_type = self.parent.full_name
        cls_wrapper = self._subst_manager.wrapper_func.declare_local("cls_wrapper", cls_wrapper_type);
        # The name of the 'self' variable (i.e. first argument)
        selfname = self._subst_manager.wrapper_func.arg_list[0].name
        
        body = """$DECLARATIONS

$PRE_CALL

%(cls_wrapper_type)s* %(cls_wrapper)s = dynamic_cast<%(cls_wrapper_type)s*>(boost::addressof(%(self)s));
if (%(cls_wrapper)s==0)
{
  // The following call is done on an instance created in C++,
  // so it won't invoke Python code.
  $RESULT_VAR_ASSIGNMENT$CALL_FUNC_NAME($INPUT_PARAMS);
}
else
{
  // The following call is done on an instance created in Python,
  // i.e. a wrapper instance. This call might invoke Python code.
  $RESULT_VAR_ASSIGNMENT%(cls_wrapper)s->%(base_name)s($INPUT_PARAMS);
}

$POST_CALL

$RETURN_STMT
"""

        # Replace the $-variables
        body = self._subst_manager.subst_wrapper(body)

        # Replace the remaining parameters
        body = body%{"cls_wrapper_type" : cls_wrapper_type,
                     "cls_wrapper" : cls_wrapper,
                     "self" : selfname,
                     "base_name" : self.base_name() }
        
#        function_call = declarations.call_invocation.join( self.declaration.name
#                                                           , [ self.function_call_args() ] )
#        body = self.wrapped_class_identifier() + '::' + function_call + ';'
#        if not declarations.is_void( self.declaration.return_type ):
#            body = 'return ' + body
        return body

    def create_function(self):
        answer = [ self.create_declaration(self.declaration.name) + '{' ]
        answer.append( self.indent( self.create_virtual_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def create_base_function( self ):
        answer = [ self.create_declaration("base_"+self.declaration.name, False) + '{' ]
        body = "%(return_)s%(wrapped_class)s::%(name)s( %(args)s );"
        answer.append( self.indent( self.create_base_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )

    def create_default_function( self ):

        header = 'static $RET_TYPE %s( $ARG_LIST_DEF ) {'%self.default_name()
        header = self._subst_manager.subst_wrapper(header)
        
        answer = [ header ]
        answer.append( self.indent( self.create_default_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )
      

    def _create_impl(self):
        # Create the substitution manager
        decl = self.declaration
        sm = function_transformers.substitution_manager_t(decl, transformers=decl.function_transformers)
        self._override_var = sm.virtual_func.allocate_local(decl.alias+"_callable")
        self._gstate_var = sm.virtual_func.allocate_local("gstate")
        self._subst_manager = sm
    
        answer = [ self.create_function() ]
        answer.append( os.linesep )
        answer.append( self.create_base_function() )
        answer.append( os.linesep )
        answer.append( self.create_default_function() )
        answer = os.linesep.join( answer )

        # Replace the argument list of the declaration so that in the
        # case that keywords are created, the correct arguments will be
        # picked up (i.e. the modified argument list and not the original
        # argument list)
        self.declaration.arguments = self._subst_manager.wrapper_func.arg_list

        return answer

