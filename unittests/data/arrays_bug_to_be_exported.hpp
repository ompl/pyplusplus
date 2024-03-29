// Copyright 2004-2008 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include <boost/noncopyable.hpp>

#ifndef __arrays_bug_to_be_exported_hpp__
#define __arrays_bug_to_be_exported_hpp__

struct arrays_bug{

struct array_of_arrays{
    double* f[4];
};

struct item{ int values[10]; };

struct container{ item items[10]; };

struct const_item{ const int values[10]; };

struct const_container{ const const_item items[10]; };

struct nc_item : boost::noncopyable { int value; };

struct nc_item_container{
    nc_item items[10];
    nc_item_container()
    {
        for(unsigned i = 0; i < 10; ++i) items[i].value = i + 1;
    }
};

};

#endif//__arrays_bug_to_be_exported_hpp__
