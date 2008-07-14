# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This file contains C++ code needed to export one dimensional static arrays.
"""


namespace = "pyplusplus::convenience"

file_name = "__ctypes_integration.pypp.hpp"

code = \
"""// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __ctypes_integration_pyplusplus_hpp__
#define __ctypes_integration_pyplusplus_hpp__

#include "boost/python.hpp"
#include "boost/utility/addressof.hpp"
#include "boost/mpl/vector.hpp"
#include "boost/function.hpp"
#include "boost/cstdint.hpp"
#include "boost/bind.hpp"


namespace pyplusplus{ namespace convenience{

template< typename TType, typename TMemVarType >
boost::uintmax_t
addressof( const TType &inst, const TMemVarType TType::* offset){
    return boost::uintmax_t( boost::addressof( inst.*offset ) );
}

template< typename TType, typename TMemVarType >
boost::python::object
make_addressof_getter( const TMemVarType TType::* offset ){
    namespace bpl = boost::python;
    namespace pyppc = pyplusplus::convenience;
    return bpl::make_function( boost::bind( &pyppc::addressof< TType, TMemVarType >, _1, offset )
                               , bpl::default_call_policies()
                               , boost::mpl::vector< boost::uintmax_t, const TType& >() );
}

} /*pyplusplus*/ } /*convenience*/

namespace pyplus_conv = pyplusplus::convenience;

#endif//__ctypes_integration_pyplusplus_hpp__

"""

