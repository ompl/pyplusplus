// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __properties_to_be_exported_hpp__
#define __properties_to_be_exported_hpp__

namespace properties{

struct properties_tester_t{
    properties_tester_t()
    : m_count( 0 )
    {}

    int count() const
    { return m_count; }

    void set_count( int x )
    { m_count = x; }

    int m_count;
};

}


#endif//__properties_to_be_exported_hpp__
