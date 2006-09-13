# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""defines few "type traits" functions related to C++ Python bindings"""

from pygccxml import declarations

def is_immutable( type_ ):
    """returns True, if type_ represents Python immutable type"""
    return declarations.is_fundamental( type_ )      \
           or declarations.is_enum( type_ )          \
           or declarations.is_std_string( type_ )    \
           or declarations.is_std_wstring( type_ )   \
           or declarations.smart_pointer_traits.is_smart_pointer( type_ )
           #todo is_complex, ...


