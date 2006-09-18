#include "boost/python.hpp"

struct vector{
    vector(){}
    vector( double ){}
    vector( const vector& ){}
};

struct float_vector{
    float_vector(){}
    float_vector( const float_vector& ){}
    float_vector( const vector& ){}
    float_vector( float ){}
};

namespace bp = boost::python;

BOOST_PYTHON_MODULE( ic_ext ){

    bp::class_< float_vector >( "float_vector" )
        .def( bp::init< >() )
        .def( bp::init< vector const & >() )
        .def( bp::init< float >() )
        .def( bp::init< const float_vector& >() );

    bp::implicitly_convertible< vector const &, float_vector >();

    bp::implicitly_convertible< float, float_vector >();

    bp::class_< vector >( "vector" )
        .def( bp::init< >() )
        .def( bp::init< double >() );

    bp::implicitly_convertible< double, vector >();

}
