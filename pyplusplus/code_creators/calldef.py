# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import algorithm
import declaration_based
import class_declaration
from pygccxml import declarations

class function_t( declaration_based.declaration_based_t):
    """
    Creates boost.python code needed to expose free/member function.
    """
    _PARAM_SEPARATOR = ', '
    def __init__(self, function, wrapper=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=function
                                                        , parent=parent )
        self._wrapper = wrapper
        
    def _get_call_policies(self):
        return self.declaration.call_policies
    def _set_call_policies(self, call_policies):
        self.declaration.call_policies = call_policies
    call_policies = property( _get_call_policies, _set_call_policies )

    def _get_use_keywords(self):
        return self.declaration.use_keywords
    def _set_use_keywords(self, use_keywords):
        self.declaration.use_keywords = use_keywords
    use_keywords = property( _get_use_keywords, _set_use_keywords )

    def _get_create_with_signature(self):
        return self.declaration.create_with_signature
    def _set_create_with_signature(self, create_with_signature):
        self.declaration.create_with_signature = create_with_signature
    create_with_signature = property( _get_create_with_signature, _set_create_with_signature)

    def _get_use_default_arguments(self):
        return self.declaration.use_default_arguments
    def _set_use_default_arguments(self, use_default_arguments):
        self.declaration.use_default_arguments = use_default_arguments
    use_default_arguments = property( _get_use_default_arguments, _set_use_default_arguments )
    
    def _get_wrapper( self ):
        return self._wrapper
    def _set_wrapper( self, new_wrapper ):
        self._wrapper = new_wrapper
    wrapper = property( _get_wrapper, _set_wrapper )
    
    def _keywords_args(self):
        boost_arg = algorithm.create_identifier( self, '::boost::python::arg' )
        boost_obj = algorithm.create_identifier( self, '::boost::python::object' )
        result = ['( ']
        for arg in self.declaration.arguments:
            if 1 < len( result ):
                result.append( self._PARAM_SEPARATOR )
            result.append( boost_arg )
            result.append( '("%s")' % arg.name )
            if self.use_default_arguments and arg.default_value:
                if not declarations.is_pointer( arg.type ) or arg.default_value != '0':
                    result.append( '=%s' % arg.default_value )
                else:
                    result.append( '=%s()' % boost_obj )
        result.append( ' )' )
        return ''.join( result )

    def is_class_function(self):
        return isinstance( self.parent, class_declaration.class_t )
    
    def _generate_functions_ref( self ):
        result = []    

        virtuality = None
        access_type = None
        if isinstance( self.declaration, declarations.member_calldef_t ):
            virtuality = self.declaration.virtuality
            access_type = self.declaration.parent.find_out_member_access_type( self.declaration )
        create_with_signature = bool( self.declaration.overloads ) or self.create_with_signature
        
        fdname = algorithm.create_identifier( self
                                              , declarations.full_name( self.declaration ) ) 
        
        if virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            pure_virtual = algorithm.create_identifier( self
                                                        , '::boost::python::pure_virtual' )
            if create_with_signature:
                if self.wrapper and access_type != declarations.ACCESS_TYPES.PUBLIC:
                    result.append( '%s( (%s)(&%s) )'
                                   % ( pure_virtual
                                       , self.wrapper.function_type()
                                       , self.wrapper.full_name() ) )
                else:
                    result.append( '%s( (%s)(&%s) )'
                                   % ( pure_virtual
                                       , self.declaration.function_type().decl_string
                                       , declarations.full_name( self.declaration ) ) )
            else:
                if self.wrapper and access_type != declarations.ACCESS_TYPES.PUBLIC:
                    result.append( '%s( &%s )'
                                   % ( pure_virtual, self.wrapper.full_name() ) )
                else:
                    result.append( '%s( &%s )'
                                   % ( pure_virtual, declarations.full_name( self.declaration ) ) )
        else:
            if isinstance( self.declaration, declarations.member_function_t ) \
               and self.declaration.has_static:
                if self.wrapper:
                    result.append( '(%s)(&%s)' 
                                    % ( self.wrapper.static_function_type(), self.wrapper.static_full_name() ) )
                else:
                    result.append( '(%s)(&%s)' % ( self.declaration.decl_string, fdname ) )

            else: 
                if create_with_signature:
                    if access_type == declarations.ACCESS_TYPES.PROTECTED:
                        result.append( '(%s)(&%s)' % ( self.wrapper.function_type(), self.wrapper.full_name() ) )
                    else:
                        result.append( '(%s)(&%s)' % ( self.declaration.decl_string, fdname ) )
                else:
                    if access_type == declarations.ACCESS_TYPES.PROTECTED:
                        result.append( '&%s' % self.wrapper.full_name() )
                    else:
                        result.append( '&%s' % fdname )
                if self.wrapper and access_type != declarations.ACCESS_TYPES.PROTECTED:
                    result.append( self._PARAM_SEPARATOR )
                    if create_with_signature:
                        result.append( '(%s)(&%s)' 
                                       % ( self.wrapper.default_function_type(), self.wrapper.default_full_name() ) )
                    else:
                        result.append( '&%s' % self.wrapper.default_full_name() )
        return result
    
    def _generate_def_code(self):
        indent_param = os.linesep + self.indent( self.indent( self._PARAM_SEPARATOR ) )
        result = []    
        if self.is_class_function():
            result.append( 'def' )
        else:
            result.append( algorithm.create_identifier( self, '::boost::python::def' ) )
        result.append( '( ' )
        result.append( '"%s"' % self.alias )
        result.append( indent_param )
        result.extend( self._generate_functions_ref() )
        if self.declaration.arguments and self.use_keywords:
            result.append( indent_param )            
            result.append( self._keywords_args() )
        if self.call_policies:
            result.append( indent_param )            
            result.append( self.call_policies.create( self ) )
        else:
            result.append( '/*, undefined call policies */' )            
        result.append( ' )' )
        return ''.join( result )
        
    def _create_impl( self ):
        code = self._generate_def_code() 
        if not self.is_class_function():
            code = code + ';'
        return code

class function_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that builds wrapper arround exposed function. There are 
    usecases when more then one function is created, for example virtual function.
    """
    def __init__( self, function, parent=None ):
        declaration_based.declaration_based_t.__init__( self, declaration=function, parent=parent )
        if self._is_call_operator():
            self.default_function_name = 'default_call'
        elif self._is_index_operator():
            self.default_function_name = 'default_get_item'
        else:
            self.default_function_name = 'default_' + self.declaration.name            
        self._wrapped_class_inst_name = 'inst'

    def _is_call_operator(self):
        return isinstance( self.declaration, declarations.member_operator_t ) \
               and self.declaration.symbol == '()'
    
    def _is_index_operator(self):
        return isinstance( self.declaration, declarations.member_operator_t ) \
               and self.declaration.symbol == '[]'
        
    def _get_default_function_name(self):
        return self._default_function_name
    def _set_default_function_name( self, new_name ):
        self._default_function_name = new_name
    default_function_name = property( _get_default_function_name, _set_default_function_name )

    def function_type(self):
        return declarations.member_function_type_t.create_decl_string(
                return_type=self.declaration.return_type
                , class_decl_string=self.parent.full_name
                , arguments_types=map( lambda arg: arg.type, self.declaration.arguments )
                , has_const=self.declaration.has_const )

    def static_function_type(self):
        arg_types = map( lambda arg: arg.type, self.declaration.arguments )
        return declarations.free_function_type_t.create_decl_string( 
                return_type=self.declaration.return_type
                , arguments_types=arg_types)

    def default_function_type( self ):
        return self.function_type()

    def full_name(self):
        return self.parent.full_name + '::' + self.declaration.name
    
    def default_full_name(self):
        return self.parent.full_name + '::' + self.default_function_name

    def static_full_name(self):
        return self.parent.full_name + '::' + self.declaration.name

    def _argument_name( self, index ):
        arg = self.declaration.arguments[ index ]
        if arg.name:
            return arg.name
        else:
            return 'p%d' % index

    def _create_declaration_impl(self, name): 
        template = 'virtual %(return_type)s %(name)s( %(args)s )%(constness)s'
        
        args = []
        for index, arg in enumerate( self.declaration.arguments ):
            args.append( arg.type.decl_string + ' ' + self._argument_name(index) )

        constness = ''
        if self.declaration.has_const:
            constness = ' const '
        
        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : name
            , 'args' : ', '.join( args )
            , 'constness' : constness
        }        
    
    def _create_declaration(self):
        return self._create_declaration_impl( self.declaration.name )
    
    def _create_default_declaration(self):
        return self._create_declaration_impl( self.default_function_name )
    
    def _create_static_declaration( self ):
        template = 'static %(return_type)s %(name)s( %(args)s )'

        args = []
        for index, arg in enumerate( self.declaration.arguments ):
            args.append( arg.type.decl_string + ' ' + self._argument_name(index) )

        args_str = ', '.join( args )
            
        return template % {
            'return_type' : self.declaration.return_type.decl_string
            , 'name' : self.declaration.name
            , 'args' : args_str
        }

    def _create_args_list( self ):
        params = []
        for index in range( len( self.declaration.arguments ) ):
            arg_type = declarations.remove_alias( self.declaration.arguments[index].type )
            arg_base_type = declarations.base_type( arg_type )
            if declarations.is_fundamental( arg_base_type ):
                params.append( self._argument_name( index ) )
            elif declarations.is_reference( arg_type ) \
                 and not declarations.is_const( arg_type ) \
                 and not declarations.is_enum( arg_base_type ):
                params.append( 'boost::ref(%s)' % self._argument_name( index ) )
            elif declarations.is_pointer( arg_type ) \
                 and not declarations.is_fundamental( arg_type.base ) \
                 and not declarations.is_enum( arg_base_type ):
                params.append( 'boost::python::ptr(%s)' % self._argument_name( index ) )
            else:
                params.append( self._argument_name( index ) )
        answer = ', '.join( params )
        if params:
            answer = answer + ' '
        return answer
    
    def _create_function_call( self ):
        answer = [ self.declaration.name ]
        answer.append( '( ' )
        answer.append( self._create_args_list() )
        answer.append( ');' )
        return ''.join( answer )
    
    def _create_virtual_body(self):
        template = []
        template.append( 'if( %(override)s %(variable_name)s = this->get_override( "%(name)s" ) )' )
        template.append( self.indent('%(return_)s%(variable_name)s( %(args)s );') )
        template.append( 'else' )
        template.append( self.indent('%(return_)s%(wrapped_class)s::%(original_name)s( %(args)s );') )
        template = os.linesep.join( template )
        
        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '
        if self._is_call_operator():
            name = '__call__'
            variable_name = 'call'
        elif self._is_index_operator():
            name = '__getitem__'
            variable_name = 'getitem'
        else:
            name = self.declaration.name      
            variable_name = self.declaration.name      
            
        return template % {
            'override' : algorithm.create_identifier( self, '::boost::python::override' )
            , 'name' : name
            , 'variable_name' : variable_name
            , 'original_name' : self.declaration.name
            , 'return_' : return_
            , 'args' : self._create_args_list()
            , 'wrapped_class' : algorithm.create_identifier( self, self.declaration.parent.decl_string )
        }
        
    def _create_pure_virtual_body(self):
        if declarations.is_reference( self.declaration.return_type ):
            return 'throw std::logic_error("Function, that returns reference to some object, could not be overriden from Python.");'
        
        template = []
        template.append( '%(override)s %(variable_name)s = this->get_override( "%(name)s" );' )
        template.append( '%(return_)s%(variable_name)s( %(args)s );')
        template = os.linesep.join( template )
        
        return_ = ''
        if not declarations.is_void( self.declaration.return_type ):
            return_ = 'return '
        
        if self._is_call_operator():
            name = '__call__'
            variable_name = 'call'
        elif self._is_index_operator():
            name = '__getitem__'
            variable_name = 'getitem'
        else:
            name = self.declaration.name            
            variable_name = self.declaration.name            
        return template % {
            'override' : algorithm.create_identifier( self, '::boost::python::override' )
            , 'name' : name
            , 'variable_name' : variable_name
            , 'return_' : return_
            , 'args' : self._create_args_list()
        }

    def _create_default_body(self):
        function_call = self._create_function_call()
        wrapped_class_name = algorithm.create_identifier( self, self.declaration.parent.decl_string )
        body = 'this->' + wrapped_class_name + '::' + function_call
        if not declarations.is_void( self.declaration.return_type ):
            body = 'return ' + body
        return body

    def _create_non_virtual_body(self):
        function_call = self._create_function_call()
        wrapped_class_name = algorithm.create_identifier( self, self.declaration.parent.decl_string )
        body = 'this->' + wrapped_class_name + '::' + function_call
        if not declarations.is_void( self.declaration.return_type ):
            body = 'return ' + body
        return body

    def _create_static_body(self):
        assert isinstance( self.declaration, declarations.member_function_t )
        fcall = '%s( %s );' % ( declarations.full_name( self.declaration ) 
                                , self._create_args_list() )
        if not declarations.is_same( self.declaration.return_type, declarations.void_t() ):
            fcall = 'return ' + fcall
        return fcall

    def _create_function(self):
        answer = [ self._create_declaration() + '{' ]
        if self.declaration.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
            answer.append( self.indent( self._create_pure_virtual_body() ) )
        elif self.declaration.virtuality == declarations.VIRTUALITY_TYPES.VIRTUAL:
            answer.append( self.indent( self._create_virtual_body() ) )
        else:
            answer.append( self.indent( self._create_non_virtual_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )
    
    def _create_default_function( self ):
        answer = [ self._create_default_declaration() + '{' ]
        answer.append( self.indent( self._create_default_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )
    
    def _create_static_function(self):
        answer = []
        answer.append( self._create_static_declaration() + '{' )
        answer.append( self.indent( self._create_static_body() ) )
        answer.append( '}' )
        return os.linesep.join( answer )
    
    def _create_impl(self):
        if self.declaration.name == 'invert_sign':
            i = 0
        answer = []
        if self.declaration.has_static:
            #we will come here only in case the function is protected
            answer.append( self._create_static_function() )
        else:
            answer.append( self._create_function() )
                
            if self.declaration.virtuality == declarations.VIRTUALITY_TYPES.VIRTUAL:
                answer.append('')
                answer.append( self._create_default_function() )
        return os.linesep.join( answer )

class constructor_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to expose constructor.
    """
    def __init__(self, constructor, wrapper=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=constructor
                                                        , parent=parent )
        self._wrapper = wrapper
        
    def _get_wrapper( self ):
        return self._wrapper
    def _set_wrapper( self, new_wrapper ):
        self._wrapper = new_wrapper
    wrapper = property( _get_wrapper, _set_wrapper )
        
    def _get_call_policies(self):
        return self.declaration.call_policies
    def _set_call_policies(self, call_policies):
        self.declaration.call_policies = call_policies
    call_policies = property( _get_call_policies, _set_call_policies )

    def _get_use_keywords(self):
        return self.declaration.use_keywords
    def _set_use_keywords(self, use_keywords):
        self.declaration.use_keywords = use_keywords
    use_keywords = property( _get_use_keywords, _set_use_keywords )

    def _get_use_default_arguments(self):
        return self.declaration.use_default_arguments
    def _set_use_default_arguments(self, use_default_arguments):
        self.declaration.use_default_arguments = use_default_arguments
    use_default_arguments = property( _get_use_default_arguments, _set_use_default_arguments )
        
    def _keywords_args(self):
        if not self.declaration.arguments:
            return ''        
        boost_arg = algorithm.create_identifier( self, '::boost::python::arg' )
        boost_obj = algorithm.create_identifier( self, '::boost::python::object' )
        result = ['( ']
        for arg in self.declaration.arguments:
            if 1 < len( result ):
                result.append( ', ' )
            result.append( boost_arg )
            result.append( '("%s")' % arg.name )
            if self.use_default_arguments and arg.default_value:
                if not declarations.is_pointer( arg.type ) or arg.default_value != '0':
                    result.append( '=%s' % arg.default_value )
                else:
                    result.append( '=%s()' % boost_obj )
        result.append( ' )' )
        return ''.join( result )        
        
    def _create_arg_code( self, arg ):
        temp = arg.type
        if declarations.is_const( temp ):
            #By David Abrahams:
            #Function parameters declared consts are ignored by C++
            #except for the purpose of function definitions
            temp = declarations.remove_const( temp )
        return algorithm.create_identifier( self, temp.decl_string )
    
    def _generate_definition_args(self):
        answer = []
        optionals = []
        for arg in self.declaration.arguments:
            if arg.default_value or optionals:
                optionals.append( self._create_arg_code( arg ) )
            else:
                answer.append( self._create_arg_code( arg ) )
        
        optionals_str = ''
        if optionals:
            optionals_str = algorithm.create_identifier( self, '::boost::python::optional' )
            optionals_str = optionals_str + '< ' + ', '.join( optionals ) + ' >'
            answer.append( optionals_str )
        return ', '.join( answer )

    
    def create_init_code(self):
        init_identifier = algorithm.create_identifier( self, '::boost::python::init' )
        args = [ self._generate_definition_args() ]
        answer = [ '%s' % declarations.templates.join( init_identifier, args ) ]
        if self.use_keywords:
            answer.append( '(%s)' % self._keywords_args() )
        else:
            answer.append( '()' )
        if self.call_policies:
            answer.append('[%s]' % self.call_policies.create( self ) )
        #I think it better not to print next line
        #else:
        #    answer.append( '/*[ undefined call policies ]*/' )
        return ''.join( answer )
    
    def _create_impl( self ):
        return 'def( %s )' % self.create_init_code()

class static_method_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code that expose member function as static function.
    """
    def __init__(self, function, function_code_creator=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=function
                                                        , parent=parent )

        self._function_code_creator = function_code_creator
        
    def _get_function_code_creator(self):
        return self._function_code_creator
    def _set_function_code_creator(self, new_function_code_creator ):
        self._function_code_creator = new_function_code_creator
    function_code_creator = property( _get_function_code_creator, _set_function_code_creator )
        
    def _create_impl( self ):
        return 'staticmethod( "%s" )' % self.function_code_creator.alias
    
class constructor_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that builds wrapper arround exposed constructor.
    """

    def __init__( self, constructor, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=constructor
                                                        , parent=parent )

    def _argument_name( self, index ):
        arg = self.declaration.arguments[ index ]
        if arg.name:
            return arg.name
        else:
            return 'p%d' % index
        
    def _create_declaration(self):
        result = []
        result.append( self.parent.wrapper_alias )
        result.append( '(' )
        args = []
        if self.parent.held_type and not self.target_configuration.boost_python_has_wrapper_held_type:
            args.append( 'PyObject*' )
        for index, arg in enumerate( self.declaration.arguments ):
            arg_text = arg.type.decl_string + ' ' + self._argument_name(index)
            if arg.default_value:
                arg_text = arg_text + '=%s' % arg.default_value
            args.append( arg_text )
        result.append( ', '.join( args ) )
        result.append( ' )' )
        return ''.join( result )
    
    def _create_constructor_call( self ):
        answer = [ algorithm.create_identifier( self, self.parent.declaration.decl_string ) ]
        answer.append( '( ' )
        params = []
        for index in range( len( self.declaration.arguments ) ):
            params.append( self._argument_name( index ) )
        answer.append( ', '.join( params ) )
        if params:
            answer.append(' ')
        answer.append( ')' )
        return ''.join( answer )
    
    def _create_impl(self):
        answer = [ self._create_declaration() ]
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '()' )
        answer.append( '{}' )
        return os.linesep.join( answer )

#There is something I don't understand
#There are usecases when boost.python requeres
#constructor for wrapper class from exposed class
#I should understand this more
class special_constructor_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates wrapper class constructor from wrapped class instance.
    """
    def __init__( self, class_inst, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=class_inst
                                                        , parent=parent )

    def _create_declaration(self):
        result = []
        result.append( self.parent.wrapper_alias )
        result.append( '(' )
        if self.parent.held_type and not self.target_configuration.boost_python_has_wrapper_held_type:
            result.append( 'PyObject*, ' )
        declarated = declarations.declarated_t( self.declaration )
        const_decl = declarations.const_t( declarated )
        const_ref_decl = declarations.reference_t( const_decl )
        identifier = algorithm.create_identifier( self, const_ref_decl.decl_string )
        result.append( identifier + ' arg' )
        result.append( ' )' )
        return ''.join( result )
    
    def _create_constructor_call( self ):
        answer = [ algorithm.create_identifier( self, self.parent.declaration.decl_string ) ]
        answer.append( '( arg )' )
        return ''.join( answer )
    
    def _create_impl(self):
        answer = [ self._create_declaration() ]
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '()' )
        answer.append( '{}' )
        return os.linesep.join( answer )

class trivial_constructor_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates trivial wrapper class constructor.
    """    
    def __init__( self, class_inst, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=class_inst
                                                        , parent=parent )

    def _create_constructor_call( self ):
        return algorithm.create_identifier( self, self.parent.declaration.decl_string ) + '()'
    
    def _create_impl(self):
        answer = [ self.parent.wrapper_alias + '(' ]
        if self.parent.held_type and not self.target_configuration.boost_python_has_wrapper_held_type:
            answer[0] = answer[0] + 'PyObject*'
        answer[0] = answer[0] + ')'
        answer.append( ': ' + self._create_constructor_call() )
        answer.append( '  , ' +  self.parent.boost_wrapper_identifier + '()' )
        answer.append( '{}' )
        return os.linesep.join( answer )

#in python all operators are members of class, while in C++
#you can define operators that are not.
class operator_t( declaration_based.declaration_based_t ):    
    """
    Creates boost.python code needed to expose supported subset of C++ operators.
    """
    class SELF_POSITION:
        FIRST = 'first'
        SECOND = 'second'
        BOTH = 'both'
        
    class supported:
        inplace = [ '+=', '-=', '*=', '/=',  '%=', '>>=', '<<=', '&=', '^=', '|=' ]
        comparison = [ '==', '!=', '<', '>', '<=', '>=' ]
        non_member = [ '+', '-', '*', '/', '%', '&', '^', '|' ] #'>>', '<<', not implemented
        unary = [ '!', '~', '+', '-' ]
        
        all = inplace + comparison + non_member + unary
        
        def is_supported( oper ):
            if oper.symbol == '*' and len( oper.arguments ) == 0:
                #dereference does not make sense
                return False
            return oper.symbol in operator_t.supported.all
        is_supported = staticmethod( is_supported )
        
    def __init__(self, operator, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=operator
                                                        , parent=parent )
    
    def _call_type_constructor( self, type ):
        x = declarations.remove_reference( type )
        x = declarations.remove_cv( x )
        other = algorithm.create_identifier( self, '::boost::python::other' )
        type_ = algorithm.create_identifier( self, x.decl_string )
        return declarations.templates.join( other, [ type_ ] ) + '()'

    def _findout_self_position(self):
        assert not declarations.is_unary_operator( self.declaration )
        decompose_type = declarations.decompose_type
        parent_decl_string = self.parent.declaration.decl_string
        arg0 = decompose_type( self.declaration.arguments[0].type )[-1].decl_string 
        if isinstance( self.declaration, declarations.member_operator_t ):
            if parent_decl_string == arg0:
                return self.SELF_POSITION.BOTH
            else:
                return self.SELF_POSITION.FIRST #may be wrong in case ++, --, but any way boost.python does not expose them
        #now we deal with non global operators
        arg1 = decompose_type( self.declaration.arguments[1].type )[-1].decl_string
        if arg0 == arg1:
            assert parent_decl_string == arg0 #in this case I have bug in module creator
            return operator_t.SELF_POSITION.BOTH
        elif arg0 != arg1 and arg0 == parent_decl_string:
            return operator_t.SELF_POSITION.FIRST
        elif arg0 != arg1 and arg1 == parent_decl_string:
            return operator_t.SELF_POSITION.SECOND
        else:
            assert 0 #I have bug some where

    def _create_binary_operator(self):
        answer = [ None, self.declaration.symbol, None ]
        self_identifier = algorithm.create_identifier( self, '::boost::python::self' )
        self_position = self._findout_self_position()
        if self_position == self.SELF_POSITION.FIRST:
            answer[0] = self_identifier
            type_ = None
            if len( self.declaration.arguments ) == 2:
                type_ = self.declaration.arguments[1].type
            else:
                type_ = self.declaration.arguments[0].type
            answer[2] = self._call_type_constructor( type_ )
        elif self_position == self.SELF_POSITION.SECOND:
            answer[0] = self._call_type_constructor(self.declaration.arguments[0].type )
            answer[2] = self_identifier
        else:
            answer[0] = self_identifier
            answer[2] = self_identifier  
        return ' '.join( answer )

    def _create_unary_operator(self):
        return self.declaration.symbol + algorithm.create_identifier( self, '::boost::python::self' )
    
    def _create_impl( self ):
        code = None
        if declarations.is_binary_operator( self.declaration ):
            code = self._create_binary_operator()
        else:
            code = self._create_unary_operator()
        return 'def( %s )' % code

class casting_operator_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register type conversions( implicitly_convertible )
    """
    def __init__( self, operator, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=operator
                                                        , parent=parent )

    def _create_impl(self):
        #TODO add comment in case of non const operator
        implicitly_convertible = algorithm.create_identifier( self, '::boost::python::implicitly_convertible' )
        from_arg = algorithm.create_identifier( self
                                                , declarations.full_name( self.declaration.parent ) )
        
        to_arg = algorithm.create_identifier( self
                                              , self.declaration.return_type.decl_string )
        return declarations.templates.join(implicitly_convertible
                                           , [ from_arg , to_arg ] )  \
               + '();'

class casting_member_operator_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register casting operators. For some 
    operators Pythonic name is given: __int__, __long__, __float__, __str__
    """
   
    def prepare_special_cases():
        special_cases = {}
        const_t = declarations.const_t
        pointer_t = declarations.pointer_t
        for type_ in declarations.FUNDAMENTAL_TYPES.values():
            alias = None
            if declarations.is_same( type_, declarations.bool_t() ):
                alias = '__int__'
            elif declarations.is_integral( type_ ):
                if 'long' in type_.decl_string:
                    alias = '__long__'
                else:
                    alias = '__int__'
            elif declarations.is_floating_point( type_ ):
                alias = '__float__'
            else: 
                continue #void 
            if alias:
                special_cases[ type_ ] = alias
                special_cases[ const_t( type_ ) ] = alias
        special_cases[ pointer_t( const_t( declarations.char_t() ) ) ] = '__str__'
        std_string = '::std::basic_string<char,std::char_traits<char>,std::allocator<char> >'
        std_wstring = '::std::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t> >'
        special_cases[ std_string ] = '__str__'
        special_cases[ std_wstring ] = '__str__'
        special_cases[ '::std::string' ] = '__str__'
        special_cases[ '::std::wstring' ] = '__str__'
        
        #TODO: add 
        #          std::complex<SomeType> some type should be converted to double
        return special_cases
    SPECIAL_CASES = prepare_special_cases()
    #casting_member_operator_t.prepare_special_cases()
    
    def __init__( self, operator, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=operator
                                                        , parent=parent )
        self._call_policies = None
        self.alias = self._find_out_alias()

    def _find_out_alias( self ):
        return_type = declarations.remove_alias( self.declaration.return_type )
        decl_string = return_type.decl_string
        for type_, alias in self.SPECIAL_CASES.items():
            if isinstance( type_, declarations.type_t ):
                if declarations.is_same( return_type, type_ ):
                    return alias
            else:
                if decl_string == type_:
                    return alias
        else:
            return 'as_' + self._generate_valid_name(self.declaration.return_type.decl_string) 
        
    def _get_call_policies(self):
        return self.declaration.call_policies
    def _set_call_policies(self, call_policies):
        self.declaration.call_policies = call_policies
    call_policies = property( _get_call_policies, _set_call_policies )    

    def _create_impl(self):
        template = 'def( "%(function_name)s", &%(class_name)s::operator %(destination_type)s %(call_policies)s )'
        
        class_name = algorithm.create_identifier( self
                                                , declarations.full_name( self.declaration.parent ) )
        
        policies = '/*, undefined call policies */' 
        if self.call_policies:
            policies = ',' + self.call_policies.create( self )
        
        return template % { 'function_name' : self.alias
                            , 'class_name' : class_name
                            , 'destination_type' : self.declaration.return_type.decl_string
                            , 'call_policies' : policies
               }

class casting_constructor_t( declaration_based.declaration_based_t ):
    """
    Creates boost.python code needed to register type conversions( implicitly_convertible ).
    This case treat situation when class has public non explicit constuctor from
    another type.
    """
    def __init__( self, constructor, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , declaration=constructor
                                                        , parent=parent )

    def _create_impl(self):
        implicitly_convertible = algorithm.create_identifier( self, '::boost::python::implicitly_convertible' )
        from_arg = algorithm.create_identifier( self
                                                ,  self.declaration.arguments[0].type.decl_string)
        
        to_arg = algorithm.create_identifier( self
                                              , declarations.full_name( self.declaration.parent ) )
        return declarations.templates.join(implicitly_convertible
                                           , [ from_arg , to_arg ] )  \
               + '();'



