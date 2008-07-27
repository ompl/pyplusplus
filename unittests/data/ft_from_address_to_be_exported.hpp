// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __ft_from_address_to_be_exported_hpp__
#define __ft_from_address_to_be_exported_hpp__

#include <stdexcept>

inline unsigned long
sum_matrix( unsigned int* matrix, unsigned int rows, unsigned int columns ){
    if( !matrix ){
        throw std::runtime_error( "matrix is null" );
    }
    unsigned long result = 0;
    for( unsigned int r = 0; r < rows; ++r ){
        for( unsigned int c = 0; c < columns; ++c ){
            result += *matrix;
            ++matrix;
        }
    }
    return result;
}

#endif//__ft_from_address_to_be_exported_hpp__
