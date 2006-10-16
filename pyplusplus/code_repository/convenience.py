# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This file contains C++ code needed to export one dimensional static arrays.
"""


namespace = "pyplusplus::convenience"

file_name = "__convenience.pypp.hpp"

code = \
"""// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __convenience_pyplusplus_hpp__
#define __convenience_pyplusplus_hpp__

#include "boost/python.hpp"

namespace pyplusplus{ namespace convenience{

//TODO: Replace index_type with Boost.Python defined ssize_t type.
//      This should be done by checking Python and Boost.Python version.
typedef int index_type;

inline void
raise_error( PyObject *exception, const char *message ){
   PyErr_SetString(exception, message);
   boost::python::throw_error_already_set();
}

inline void
ensure_sequence( boost::python::object seq, index_type expected_length=-1 ){
    PyObject* seq_impl = seq.ptr();

    if( !PySequence_Check( seq_impl ) ){
        raise_error( PyExc_TypeError, "Sequence expected" );
    }

    index_type length = PySequence_Length( seq_impl );
    if( expected_length != -1 && length != expected_length ){
        std::stringstream err;
        err << "Expected sequence length is " << expected_length << ". "
            << "Actual sequence length is " << length << ".";
        raise_error( PyExc_ValueError, err.str().c_str() );
    }
}

template< class ExpectedType >
void ensure_uniform_sequence( boost::python::object seq, index_type expected_length=-1 ){
    ensure_sequence( seq, expected_length );

    index_type length = boost::python::len( seq );
    for( index_type index = 0; index < length; ++index ){
        boost::python::object item = seq[index];

        boost::python::extract<ExpectedType> type_checker( item );
        if( !type_checker.check() ){
            std::string expected_type_name( boost::python::type_id<ExpectedType>().name() );

            std::string item_type_name("different");
            PyObject* item_impl = item.ptr();
            if( item_impl && item_impl->ob_type && item_impl->ob_type->tp_name ){
                item_type_name = std::string( item_impl->ob_type->tp_name );
            }

            std::stringstream err;
            err << "Sequence should contain only items with type \\"" << expected_type_name << "\\". "
                << "Item at position " << index << " has \\"" << item_type_name << "\\" type.";
            raise_error( PyExc_ValueError, err.str().c_str() );
        }
    }
}

} /*pyplusplus*/ } /*convenience*/


#endif//__convenience_pyplusplus_hpp__

"""
