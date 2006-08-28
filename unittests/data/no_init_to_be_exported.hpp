// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __no_init_to_be_exported_hpp__
#define __no_init_to_be_exported_hpp__

#include "boost/shared_ptr.hpp"

namespace no_init_ns{

class controller_i{
public:
    virtual ~controller_i() { }
    virtual bool get_value(void) const = 0;
    virtual void set_value(bool value) = 0;
};

inline int
get_value( const boost::shared_ptr< controller_i >& controller ){
    if( controller ){
        return controller->get_value() ? 1 : 0;
    }
    else{
        return -1;
    }
}

}

#endif//__no_init_to_be_exported_hpp__
