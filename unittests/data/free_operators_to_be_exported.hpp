// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __free_operators_to_be_exported_hpp__
#define __free_operators_to_be_exported_hpp__

namespace free_operators{

struct number{
    int i;
    
    number operator*( int ii ) const {
        number n2 = { i * ii };
        return n2;
    }
};

number operator+( const number& x, int y ){ 
    number z;
    z.i = x.i + y;
    return z;
}


bool operator!( const number& x ){
    return !x.i;
}

number operator*( const number& n,  double i ){
    number n2 = { n.i * i };
    return n2;
}

number operator*( double i, const number& n ){
    number n2 = { n.i * i };
    return n2;
}


}
    

#endif//__free_operators_to_be_exported_hpp__
