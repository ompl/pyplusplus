// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __properties_to_be_exported_hpp__
#define __properties_to_be_exported_hpp__

namespace properties{

struct properties_tester_t{

    struct nested{
        int n;
    };

    properties_tester_t()
    : m_count( 0 )
    {}

    int count() const
    { return m_count; }

    void set_count( int x )
    { m_count = x; }

    nested& get_nested()
    { return m_nested; }

    void set_nested( nested x )
    { m_nested = x; }

    int m_count;
    nested m_nested;
};

}


#endif//__properties_to_be_exported_hpp__
