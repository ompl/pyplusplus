# Copyright 2006 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# Matthias Baas is an initial author of the templates.

import os
from string import Template

# function_name - C++ function name
# function_alias - function name that Python user will see

class mem_fun: 
    body = Template( os.linesep.join([
          '$declare_variables'
        , '$pre_call'
        , '$save_return_value_stmt$function_name($input_params);'
        , '$post_call'
        , '$return_stmt'
    ]))

class mem_fun_v:    
    
    original_function_call = Template( "$return_$wrapped_class::%function_name( $args );" )

    override_body = Template( os.linesep.join([
        '$declare_variables'
        , '$declare_override_function = this->get_override( "$function_alias" );'
        , 'if( $override_function_var_name ){'
        , '    $declare_override_variables'
        , '    $override_pre_call'
        , '    ${save_override_return_value}boost::python::call<$override_return_type>( $override_function_var_name$override_input_params;'
        , '    $override_post_call'
        , '    $override_return_stmt'
        , '}'
        , 'else{'
        , '    ' + original_function_call.template
        , '}'
    ]))

    override_body_safe = Template( os.linesep.join([
        '$declare_gil_guard'
        , '$declare_variables'
        , '$lock_gil_guard'
        , '$declare_override_function = this->get_override( "$function_alias" );'
        , '$unlock_gil_guard'
        , 'if( $override_function_var_name ){'
        , '    $lock_gil_guard //release() will be called from destructor'
        , '    $declare_override_variables'
        , '    $override_pre_call'
        , '    ${save_override_return_value}boost::python::call<$override_return_type>( $override_function_var_name$override_input_params;'
        , '    $override_post_call'
        , '    $override_return_stmt'
        , '}'
        , 'else{'
        , '    ' + original_function_call.template
        , '}'
    ]))
    
    default_body = Template( os.linesep.join([
          '$declare_variables'
        , '$pre_call'
        , '$declare_wrapped_class_inst'
        , 'if( dynamic_cast< $wrapped_class* >( boost::addressof( $wrapped_class_inst_var_name ) ) ){'
        # The following call is done on an instance created in Python i.e. a 
        # wrapper instance. this call might invoke python code.
        , '    $save_return_value_stmt$wrapped_class_inst_var_name->$wrapped_class::$function_name($input_params);'
        , '}'
        , 'else{'
        # The following call is done on an instance created in C++, so it won't 
        # invoke python code.
        , '    $save_return_value_stmt$function_name($input_params);'
        , '}'
        , '$post_call'
        , '$return_stmt'
    ]))


def substitute( text, **keywd ):
    return Template( text ).substitute( **keywd )
    
