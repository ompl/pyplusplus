// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __casting_to_be_exported_hpp__
#define __casting_to_be_exported_hpp__

namespace casting{ 

struct y{};
    
struct x{
    x() 
    : value(0)
    {}
    
    explicit x( int i )
    : value( i )
    {}
    
    x( bool b )
    : value( b )
    {}
    
    operator int() const { return value; }
    
    operator y(){ return y(); }
    
    int value;
};


int identity( int z ){ return z; }

int x_value(const x& d ){ return d.value; }

}

#endif//__casting_to_be_exported_hpp__
