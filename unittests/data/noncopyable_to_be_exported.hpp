// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __noncopyable_to_be_exported_hpp__
#define __noncopyable_to_be_exported_hpp__

#include "boost/noncopyable.hpp"

namespace noncopyables{ 

class a_t{
public:

    static char get_a(){ return 'a'; }

private:
    a_t(){};
    ~a_t(){};
};

class b_t{
    ~b_t(){}
public:
   
    static char get_b(){ return 'b'; }

};

class c_t : public boost::noncopyable{
public:  
    static char get_c(){ return 'c'; }

};

class d_t{  
private:
    d_t( const d_t& );    
public:  
    d_t(){}
    ~d_t(){}
    static char get_d(){ return 'd'; }

};

class dd_t : public d_t{
public:
    dd_t(){}
    ~dd_t(){}
    static char get_dd(){ return 'D'; }        
};

}

#endif//__noncopyable_to_be_exported_hpp__