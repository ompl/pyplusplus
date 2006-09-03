// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __function_transformations_to_be_exported_hpp__
#define __function_transformations_to_be_exported_hpp__

namespace ft{

struct image_t{

    image_t( unsigned int& h, unsigned int& w )
    : m_height( h )
      , m_width( w )
    {}

    void get_size( unsigned int& h, unsigned int& w ){
        h = m_height;
        w = m_width;
    }

    unsigned int m_width;
    unsigned int m_height;

};

inline void
get_image_size( image_t& img, unsigned int& h, unsigned int& w ){
    img.get_size( h, w );
}

}

#endif//__function_transformations_to_be_exported_hpp__
