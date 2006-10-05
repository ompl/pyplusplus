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

//1 - dimension
namespace pyplusplus{ namespace convenience{

void raise_error( PyObject *exception, const char *message ){

   PyErr_SetString(exception, message);
   boost::python::throw_error_already_set();

}

void ensure_sequence( boost::python::object seq, Py_ssize_t expected_length=-1 ){

    PyObject* seq_impl = seq.ptr();

    if( !PySequence_Check( seq_impl ) ){
        raise_error( PyExc_TypeError, "Sequence expected" );
    }

    Py_ssize_t length = PySequence_Length( seq_impl );
    if( expected_length != -1 && length != expected_length ){
        std::stringstream err;
        err << "Expected sequence length is " << expected_length << ". "
            << "Actual sequence length is " << length << ".";
        raise_error( PyExc_ValueError, err.str().c_str() );
    }

}

template< class ExpectedType >
void ensure_uniform_sequence( boost::python::object seq, Py_ssize_t expected_length=-1 ){

    ensure_sequence( seq, expected_length );
    Py_ssize_t length = boost::python::len( seq );
    for( Py_ssize_t index = 0; index < length; ++index ){
        boost::python::object item = seq[index];
        boost::python::extract<ExpectedType> type_checker( item );
        if( type_checker.check() ){
            const boost::python::type_info expected_type_info( boost::python::type_id<ExpectedType>() );
            //TODO: How to extract type_info from PyObject?
            std::stringstream err;
            err << "Sequence should contain only items with type \"" << expected_type_info.name() << "\". "
                << "Item at position " << index << " has different type.";
            raise_error( PyExc_ValueError, err.str().c_str() );
        }
    }

}

} /*pyplusplus*/ } /*convenience*/


#endif//__convenience_pyplusplus_hpp__

"""
