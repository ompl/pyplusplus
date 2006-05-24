# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import algorithm
import declaration_based
from pyplusplus import code_repository
from pyplusplus.decl_wrappers import call_policies
from pygccxml import declarations

class member_variable_base_t( declaration_based.declaration_based_t ):
    """
    Base class for all member variables code creators. Mainly exists to 
    simplify file writers algorithms.
    """

    def __init__(self, variable, wrapper=None, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , parent=parent
                                                        , declaration=variable)
        self._wrapper = wrapper 

    def _get_wrapper( self ):
        return self._wrapper
    def _set_wrapper( self, new_wrapper ):
        self._wrapper = new_wrapper
    wrapper = property( _get_wrapper, _set_wrapper )
   
class member_variable_t( member_variable_base_t ):
    """
    Creates boost.python code that exposes member variable.
    """
    def __init__(self, variable, wrapper=None, parent=None ):
        member_variable_base_t.__init__( self, variable=variable, wrapper=wrapper, parent=parent)

    #>    On Wednesday, 19. April 2006 23:05, Ralf W. Grosse-Kunstleve wrote:
    #>   .add_property("p", make_function(&A::get_p, return_value_policy<reference_existing_object>()))
    def _generate_for_pointer( self ):    
        if self.declaration.type_qualifiers.has_static:
            add_property = 'add_static_property'
        else:
            add_property = 'add_property'
        answer = [ add_property ]
        answer.append( '( ' )
        answer.append('"%s"' % self.alias)
        answer.append( self.PARAM_SEPARATOR )
        
        call_pol = call_policies.return_value_policy( call_policies.reference_existing_object ).create( self )
        make_function = algorithm.create_identifier( self, '::boost::python::make_function' )

        answer.append( '%(mk_func)s( (%(getter_type)s)(&%(wfname)s), %(call_pol)s )' 
                       % { 'mk_func' : make_function
                           , 'getter_type' : self.wrapper.getter_type
                           , 'wfname' : self.wrapper.getter_full_name
                           , 'call_pol' : call_pol } )

        #don't generate setter method, right now I don't know how to do it.
        if False and self.wrapper.has_setter:
            answer.append( self.PARAM_SEPARATOR )
            if self.declaration.type_qualifiers.has_static:
                call_pol = call_policies.default_call_policies().create(self)
            else:
                call_pol = call_policies.with_custodian_and_ward_postcall( 0, 1 ).create(self)
            answer.append( '%(mk_func)s( (%(setter_type)s)(&%(wfname)s), %(call_pol)s )' 
                       % { 'mk_func' : make_function
                           , 'setter_type' : self.wrapper.setter_type
                           , 'wfname' : self.wrapper.setter_full_name
                           , 'call_pol' : call_pol } )
        answer.append( ' ) ' )
        
        code = ''.join( answer )
        if len( code ) <= self.LINE_LENGTH:
            return code
        else:
            for i in range( len( answer ) ):
                if answer[i] == self.PARAM_SEPARATOR:
                    answer[i] = os.linesep + self.indent( self.indent( self.indent( answer[i] ) ) )
            return ''.join( answer )        
        
    def _generate_for_none_pointer( self ):
        tmpl = None
        if self.declaration.type_qualifiers.has_static:
            tmpl = '%(access)s( "%(alias)s", %(name)s )'            
        else:
            tmpl = '%(access)s( "%(alias)s", &%(name)s )'
        
        access = 'def_readwrite'
        if self.is_read_only():
            access = 'def_readonly'
            
        result = tmpl % { 
                    'access' : access
                    , 'alias' : self.alias
                    , 'name' : algorithm.create_identifier( self, self.declaration.decl_string ) }
        
        return result

    def is_read_only( self ):
        type_ = declarations.remove_alias( self.declaration.type )
        if declarations.is_pointer( type_ ):
            type_ = declarations.remove_pointer( type_ )
            return isinstance( type_, declarations.const_t )
        
        if declarations.is_reference( type_ ):
            type_ = declarations.remove_reference( type_ )            

        if isinstance( type_, declarations.const_t ):
            return True
        
        if isinstance( type_, declarations.declarated_t ) \
           and isinstance( type_.declaration, declarations.class_t ) \
           and not declarations.has_public_assign( type_.declaration ):
            return True
        return False

    def _generate_variable( self ):
        if declarations.is_pointer( self.declaration.type ):
            return self._generate_for_pointer()
        else:
            return self._generate_for_none_pointer()

    def _create_impl(self):
        return self._generate_variable()

class member_variable_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that creates accessor for pointer class variables
    """
    #TODO: give user a way to set call policies
    #      treat void* pointer
    indent = declaration_based.declaration_based_t.indent
    MV_GET_TEMPLATE = os.linesep.join([
          'static %(type)s get_%(name)s(%(cls_type)s inst ){'
        , indent( 'return inst.%(name)s;' )
        , '}' 
        , ''
    ])

    MV_STATIC_GET_TEMPLATE = os.linesep.join([
          'static %(type)s get_%(name)s(){'
        , indent( 'return %(cls_type)s::%(name)s;' )
        , '}' 
        , ''
    ])

    MV_SET_TEMPLATE = os.linesep.join([
          'static void set_%(name)s( %(cls_type)s inst, %(type)s new_value ){ '
        , indent( 'inst.%(name)s = new_value;' )
        , '}' 
        , ''        
    ])

    MV_STATIC_SET_TEMPLATE = os.linesep.join([
          'static void set_%(name)s( %(type)s new_value ){ '
        , indent( '%(cls_type)s::%(name)s = new_value;' )
        , '}' 
        , ''        
    ])

    def __init__(self, variable, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , parent=parent
                                                        , declaration=variable)

    def _get_getter_full_name(self):
        return self.parent.full_name + '::' + 'get_' + self.declaration.name
    getter_full_name = property( _get_getter_full_name )

    def inst_arg_type( self, has_const ):
        inst_arg_type = declarations.declarated_t( self.declaration.parent )
        if has_const:
            inst_arg_type = declarations.const_t(inst_arg_type)
        inst_arg_type = declarations.reference_t(inst_arg_type)
        return inst_arg_type
    
    def _get_getter_type(self):
        if self.declaration.type_qualifiers.has_static:
            arguments_types=[] 
        else:
            arguments_types=[ self.inst_arg_type(True) ] 
            
        return declarations.free_function_type_t.create_decl_string(
                return_type=self.declaration.type
                , arguments_types=arguments_types )
    getter_type = property( _get_getter_type )
    
    def _get_setter_full_name(self):
        return self.parent.full_name + '::' + 'set_' + self.declaration.name
    setter_full_name = property(_get_setter_full_name)
    
    def _get_setter_type(self):
        if self.declaration.type_qualifiers.has_static:
            arguments_types=[ self.declaration.type ] 
        else:
            arguments_types=[ self.inst_arg_type(False), self.declaration.type  ] 
            
        return declarations.free_function_type_t.create_decl_string(
                return_type=declarations.void_t()
                , arguments_types=arguments_types )
    setter_type = property( _get_setter_type )

    def _get_has_setter( self ):
        return not declarations.is_const( self.declaration.type.base )
    has_setter = property( _get_has_setter )
    
    def _create_impl(self):
        answer = []
        if self.declaration.type_qualifiers.has_static:
            substitutions = {
                'type' : self.declaration.type.decl_string
                , 'name' : self.declaration.name
                , 'cls_type' : declarations.full_name( self.declaration.parent ) 
            }
            answer.append( self.MV_STATIC_GET_TEMPLATE % substitutions)
            if self.has_setter:
                answer.append( self.MV_STATIC_SET_TEMPLATE % substitutions )
        else:
            answer.append( self.MV_GET_TEMPLATE % {
                'type' : self.declaration.type.decl_string
                , 'name' : self.declaration.name
                , 'cls_type' : self.inst_arg_type( has_const=True ) })
            if self.has_setter:
                answer.append( self.MV_SET_TEMPLATE % {
                'type' : self.declaration.type.decl_string
                , 'name' : self.declaration.name
                , 'cls_type' : self.inst_arg_type( has_const=False ) })
        return os.linesep.join( answer )

class bit_field_t( member_variable_base_t ):
    """
    Creates boost.python code that exposes bit fields member variables
    """
    def __init__(self, variable, wrapper, parent=None ):
        member_variable_base_t.__init__( self
                                         , variable=variable
                                         , wrapper=wrapper
                                         , parent=parent)

    def _create_impl( self ):
        if self.declaration.type_qualifiers.has_static:
            add_property = 'add_static_property'
        else:
            add_property = 'add_property'
        answer = [ add_property ]
        answer.append( '( ' )
        answer.append('"%s"' % self.alias)
        answer.append( self.PARAM_SEPARATOR )
        answer.append( '(%s)(&%s)' 
                       % ( self.wrapper.getter_type, self.wrapper.getter_full_name ) )

        if self.wrapper.has_setter:
            answer.append( self.PARAM_SEPARATOR )
            answer.append( '(%s)(&%s)' 
                           % ( self.wrapper.setter_type, self.wrapper.setter_full_name ) )
        answer.append( ' ) ' )
        
        code = ''.join( answer )
        if len( code ) <= self.LINE_LENGTH:
            return code
        else:
            for i in range( len( answer ) ):
                if answer[i] == self.PARAM_SEPARATOR:
                    answer[i] = os.linesep + self.indent( self.indent( self.indent( answer[i] ) ) )
            return ''.join( answer )

class bit_field_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that creates accessor for bit fields
    """

    indent = declaration_based.declaration_based_t.indent
    BF_GET_TEMPLATE = os.linesep.join([
          '%(type)s get_%(name)s() const {'
        , indent( 'return %(name)s;' )
        , '}' 
        , ''
    ])
    
    BF_SET_TEMPLATE = os.linesep.join([
          'void set_%(name)s( %(type)s new_value ){ '
        , indent( '%(name)s = new_value;' )
        , '}' 
        , ''        
    ])

    def __init__(self, variable, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , parent=parent
                                                        , declaration=variable)

    def _get_getter_full_name(self):
        return self.parent.full_name + '::' + 'get_' + self.declaration.name
    getter_full_name = property( _get_getter_full_name )
    
    def _get_getter_type(self):
        return declarations.member_function_type_t.create_decl_string(
                return_type=self.declaration.type
                , class_decl_string=self.parent.full_name
                , arguments_types=[]
                , has_const=True )
    getter_type = property( _get_getter_type )
    
    def _get_setter_full_name(self):
        return self.parent.full_name + '::' + 'set_' + self.declaration.name
    setter_full_name = property(_get_setter_full_name)
    
    def _get_setter_type(self):
        return declarations.member_function_type_t.create_decl_string(
                return_type=declarations.void_t()
                , class_decl_string=self.parent.full_name
                , arguments_types=[self.declaration.type]
                , has_const=False )
    setter_type = property( _get_setter_type )

    def _get_has_setter( self ):
        return not declarations.is_const( self.declaration.type )
    has_setter = property( _get_has_setter )
    
    def _create_impl(self):
        answer = []
        substitutions = dict( type=self.declaration.type.decl_string
                              , name=self.declaration.name ) 
        answer.append( self.BF_GET_TEMPLATE % substitutions )
        if self.has_setter:
            answer.append( self.BF_SET_TEMPLATE % substitutions )
        return os.linesep.join( answer )

class array_mv_t( member_variable_base_t ):
    """
    Creates boost.python code that exposes array member variable.
    """
    def __init__(self, variable, wrapper, parent=None ):
        member_variable_base_t.__init__( self
                                         , variable=variable
                                         , wrapper=wrapper
                                         , parent=parent )
   
    def _create_impl( self ):
        assert isinstance( self.wrapper, array_mv_wrapper_t )
        if self.declaration.type_qualifiers.has_static:
            answer = [ 'add_static_property' ]
        else:
            answer = [ 'add_property' ]
        answer.append( '( ' )
        answer.append('"%s"' % self.declaration.name )
        answer.append( os.linesep + self.indent( self.PARAM_SEPARATOR ) )
        temp = [ algorithm.create_identifier( self, "::boost::python::make_function" ) ]
        temp.append( '( ' )
        temp.append( '(%s)(&%s)' 
                       % ( self.wrapper.wrapper_creator_type
                           , self.wrapper.wrapper_creator_full_name ) )
        if not self.declaration.type_qualifiers.has_static:
            temp.append( os.linesep + self.indent( self.PARAM_SEPARATOR, 4 ) )
            temp.append( call_policies.with_custodian_and_ward_postcall( 0, 1 ).create(self) )
        temp.append( ' )' )
        answer.append( ''.join( temp ) )
        answer.append( ' );' )        
        return ''.join( answer )
    
#TODO: generated fucntion should be static and take instance of the wrapped class
#as first argument.
class array_mv_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that register array class.
    """
    
    def __init__(self, variable, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , parent=parent
                                                        , declaration=variable)

    def _get_wrapper_type( self ):
        ns_name = code_repository.array_1.namespace
        if declarations.is_const( self.declaration.type ):
            class_name = 'const_array_1_t'
        else:
            class_name = 'array_1_t'
        
        decl_string = declarations.templates.join( 
              '::'.join( [ns_name, class_name] )
            , [ declarations.array_item_type( self.declaration.type ).decl_string
                , str( declarations.array_size( self.declaration.type ) )
        ])
        
        return declarations.dummy_type_t( decl_string )
    wrapper_type = property( _get_wrapper_type )
        
    def _get_wrapper_creator_type(self):
        return declarations.member_function_type_t.create_decl_string(
                return_type=self.wrapper_type
                , class_decl_string=self.parent.full_name
                , arguments_types=[]
                , has_const=False )
    wrapper_creator_type = property( _get_wrapper_creator_type )
    
    def _get_wrapper_creator_name(self):
        return '_'.join( ['pyplusplus', self.declaration.name, 'wrapper'] )
    wrapper_creator_name = property( _get_wrapper_creator_name )

    def _get_wrapper_creator_full_name(self):
        return '::'.join( [self.parent.full_name, self.wrapper_creator_name] )
    wrapper_creator_full_name = property( _get_wrapper_creator_full_name )

    def _create_impl( self ):
        answer = [self.wrapper_type.decl_string]
        answer.append( ''.join([ self.wrapper_creator_name, '(){']) )
        temp = ''.join([ 'return '
                         , self.wrapper_type.decl_string
                         , '( '
                         , self.declaration.name 
                         , ' );'])
        answer.append( self.indent( temp ) )
        answer.append('}')
        return os.linesep.join( answer )
        

class mem_var_ref_t( member_variable_base_t ):
    """
    Creates C++ code that creates accessor for class member variable, that has type reference.
    """
    def __init__(self, variable, wrapper, parent=None ):
        member_variable_base_t.__init__( self
                                         , variable=variable
                                         , wrapper=wrapper
                                         , parent=parent)
        self.param_sep = os.linesep + self.indent( self.PARAM_SEPARATOR, 2 )

    def _create_getter( self ):
        answer = ['def']
        answer.append( '( ' )
        answer.append( '"get_%s"' % self.alias)
        answer.append( self.param_sep )
        answer.append( '(%s)(&%s)' 
                       % ( self.wrapper.getter_type.decl_string, self.wrapper.getter_full_name ) )
        if self.declaration.getter_call_policies:
            answer.append( self.param_sep )            
            answer.append( self.declaration.getter_call_policies.create( self ) )
        else:
            answer.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        answer.append( ' )' )
        return ''.join( answer )
    
    def _create_setter( self ):
        answer = ['def']
        answer.append( '( ' )
        answer.append( '"set_%s"' % self.alias)
        answer.append( self.param_sep )
        answer.append( '(%s)(&%s)' 
                       % ( self.wrapper.setter_type.decl_string, self.wrapper.setter_full_name ) )
        if self.declaration.setter_call_policies:
            answer.append( self.param_sep )            
            answer.append( self.declaration.setter_call_policies.create( self ) )
        else:
            answer.append( os.linesep + self.indent( '/* undefined call policies */', 2 ) )             
        answer.append( ' )' )
        return ''.join( answer )
    
    def _create_impl( self ):
        #TODO: fix me, should not force class scope usage
        answer = []
        class_var_name = self.parent.class_var_name
        answer.append( "%s.%s;" % (class_var_name, self._create_getter() ) )
        if self.wrapper.has_setter:
            answer.append( os.linesep )
            answer.append( "%s.%s;" % (class_var_name, self._create_setter() ) )
        return ''.join( answer )
     
class mem_var_ref_wrapper_t( declaration_based.declaration_based_t ):
    """
    Creates C++ code that creates accessor for class member variable, that has type reference.
    """
    
    indent = declaration_based.declaration_based_t.indent
    GET_TEMPLATE = os.linesep.join([
          'static %(type)s get_%(name)s( %(class_type)s& inst ) {'
        , indent( 'return inst.%(name)s;' )
        , '}' 
        , ''
    ])
    
    SET_TEMPLATE = os.linesep.join([
          'static void set_%(name)s( %(class_type)s& inst, %(type)s new_value ){ '
        , indent( 'inst.%(name)s = new_value;' )
        , '}' 
        , ''        
    ])

    def __init__(self, variable, parent=None ):
        declaration_based.declaration_based_t.__init__( self
                                                        , parent=parent
                                                        , declaration=variable)

    def _get_getter_full_name(self):
        return self.parent.full_name + '::' + 'get_' + self.declaration.name
    getter_full_name = property( _get_getter_full_name )

    def _get_class_inst_type( self ):
        return declarations.declarated_t( self.declaration.parent )

    def _get_exported_var_type( self ):
        type_ = declarations.remove_reference( self.declaration.type )
        type_ = declarations.remove_const( type_ )
        if declarations.is_fundamental( type_ ) or declarations.is_enum( type_ ):
            return type_
        else:
            return self.declaration.type

    def _get_getter_type(self):
        return declarations.free_function_type_t(
                return_type=self._get_exported_var_type()
                , arguments_types=[ self._get_class_inst_type() ] )
    getter_type = property( _get_getter_type )
    
    def _get_setter_full_name(self):
        return self.parent.full_name + '::' + 'set_' + self.declaration.name
    setter_full_name = property(_get_setter_full_name)
    
    def _get_setter_type(self):
        return declarations.free_function_type_t(
                return_type=declarations.void_t()
                , arguments_types=[ self._get_class_inst_type(), self._get_exported_var_type() ] )
    setter_type = property( _get_setter_type )

    def _get_has_setter( self ):  
        if declarations.is_const( declarations.remove_reference( self.declaration.type ) ):
            return False
        elif declarations.is_fundamental( self._get_exported_var_type() ):
            return True
        elif declarations.is_enum( self._get_exported_var_type() ):
            return True
        else:
            pass
        
        no_ref = declarations.remove_reference( self.declaration.type )
        no_const = declarations.remove_const( no_ref )        
        base_type = declarations.remove_alias( no_const )
        if not isinstance( base_type, declarations.declarated_t ):
            return True #TODO ????
        decl = base_type.declaration
        if decl.is_abstract:
            return False
        if declarations.has_destructor( decl ) and not declarations.has_public_destructor( decl ): 
            return False
        if not declarations.has_trivial_copy(decl):
            return False
        return True
    has_setter = property( _get_has_setter )
    
    def _create_impl(self):
        answer = []
        cls_type = algorithm.create_identifier( self, self.declaration.parent.decl_string )
        
        substitutions = dict( type=self._get_exported_var_type().decl_string
                              , class_type=cls_type
                              , name=self.declaration.name ) 
        answer.append( self.GET_TEMPLATE % substitutions )
        if self.has_setter:
            answer.append( self.SET_TEMPLATE % substitutions )
        return os.linesep.join( answer )
