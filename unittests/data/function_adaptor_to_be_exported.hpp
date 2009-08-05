// Copyright 2004-2008 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __function_adaptor_to_be_exported_hpp__
#define __function_adaptor_to_be_exported_hpp__

//#include <boost/preprocessor/facilities/identity.hpp>
//I need it for BOOST_PP_IDENTITY macro

#define PYPP_IDENTITY( X ) X

struct foo_t{
    int get_zero() const{ return 0; }
    static int get_two(){ return 2; }
};

inline int get_one(){ return 1; }

#endif//__function_adaptor_to_be_exported_hpp__
