#include "boost/python.hpp"
#include <stdexcept>

/**
 * Content:
 *  * example, which explain how to create custom exception class, which derives
 *    from Python built-in exceptions
 *
 **/

class zero_division_error : public std::exception{
public:

    zero_division_error()
    : std::exception(), m_msg()
    {}

    zero_division_error( const std::string& msg )
    : std::exception(), m_msg( msg )
    {}

    zero_division_error( const zero_division_error& other )
    : std::exception(other), m_msg( other.m_msg )
    {}
        
    const std::string& message() const
    { return m_msg; }
    
    virtual ~zero_division_error() throw(){}
        
private:
    const std::string m_msg;
};

double devide( double x, int y ){
    if( !y ){
        throw zero_division_error( "unable to devide by 0( zero )" );
    }
    return x/y;
}

namespace bpl = boost::python;

void translate( const zero_division_error& err ){
    bpl::object this_module( bpl::handle<>( bpl::borrowed(PyImport_AddModule("my_exceptions"))));
    bpl::object zde_class = this_module.attr("zero_division_error");
    bpl::object pyerr = zde_class( err );
    PyErr_SetObject( zde_class.ptr(), bpl::incref( pyerr.ptr() ) );
}


BOOST_PYTHON_MODULE( my_exceptions ){
    
    typedef bpl::return_value_policy< bpl::copy_const_reference > return_copy_const_ref;
    bpl::class_< zero_division_error >( "_zero_division_error_" )
        .def( bpl::init<const std::string&>() )
        .def( bpl::init<const zero_division_error&>() )
        .def( "message", &zero_division_error::message, return_copy_const_ref() )
        .def( "__str__", &zero_division_error::message, return_copy_const_ref() );
    
    bpl::register_exception_translator<zero_division_error>(&translate);
    
    bpl::def( "devide", &::devide );
}

