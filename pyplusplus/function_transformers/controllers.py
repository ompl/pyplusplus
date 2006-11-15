import string
import templates
from pygccxml import declarations

class variable_t( object ):
    def __init__( self, name, type, initialize_expr='' ):
        self.__name = name
        self.__type = type
        self.__initialize_expr = initialize_expr
        
    @property
    def name( self ):
        return self.__name
        
    @property 
    def type( self ):
        return self.__type
        
    @property 
    def initialize_expr( self ):
        return self.__initialize_expr
        
    def declare_var_string( self ):
        return templates.substitute( "$type $name$initialize_expr;"
                                     , name=self.name
                                     , type=self.type
                                     , initialize_expr=self.initialize_expr )
    
class controller_base_t( object ):
    def __init__( self, function ):
        object.__init__( self )
        self.__function = function
        self.__variables = {} #name : variable
        self.__names_in_use = set( map( lambda arg: arg.name, self.function.arguments ) )
        
    def declare_variable( self, type, name, initialize_expr='' ):
        unique_name = self.__create_unique_var_name( name )
        self.__variables[ unique_name ] = variable_t( type, unique_name, initialize_expr )
    
    def register_variable_name( self, name ):
        return self.__create_unique_var_name( name )
        
    def __create_unique_var_name( self, name ):
        n = 2
        unique_name = name
        while 1:
            if unique_name in self.__names_in_use:
                unique_name = "%s_%d" % ( name, n )
                n += 1
            else:
                self.__names_in_use.add( unique_name )
                return unique_name

class mem_fun_controller_t( controller_base_t ):
    def __init__( self, function ):
        controller_base_t.__init__( self, function )
        self.__transformed_args = function.arguments[:]
        self.__transformed_return_type = function.return_type
        
        self.__return_variables = []
        self.__pre_call = []
        self.__post_call = []
        self.__save_return_value_stmt = None
        self.__input_params = [ arg.name for arg in function.arguments ]        
        self.__return_stmt = None
        
    @property
    def transformed_args( self ):
        return self.__transformed_args
    
    def __get_transformed_return_type( self ):
        return self.__transformed_return_type        
    def __set_transformed_return_type( self, type_ ):
        if isinstane( type, types.StringTypes ):
            type_ = declarations.dummy_type_t( type_ )
        self.__transformed_return_type = type_
    transformed_return_type = property( __get_transformed_return_type, __set_transformed_return_type )
    
    def add_return_variable( self, variable_name ):
        self.__return_variables.append( name )
    
    @property
    def pre_call( self ):
        return self.__pre_call
        
    def add_pre_call_code( self, code ):
        self.__pre_call.append( code )
        
    @property
    def pos_call( self ):
        return self.__post_call
    
    def add_post_call_code( self, code ):
        self.__post_call.append( code )
       
    def __get_save_return_value_stmt( self ):
        return self.__save_return_value_stmt
    def __set_save_return_value_stmt( self, expr ):
        self.__save_return_value_stmt = expr
    save_return_value_stmt = property( __get_save_return_value_stmt, __set_save_return_value_stmt )
    
    def set_input_param( self, index, var_name_or_expr ):
        self.__input_params[ index ] = var_name_or_expr
        
    @property
    def return_stmt
    
        
