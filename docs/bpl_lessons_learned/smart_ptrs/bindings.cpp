// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include "boost/python.hpp"
#include "classes.hpp"

namespace bp = boost::python;

namespace boost{ namespace python{

    template<class T>
    inline T * get_pointer(smart_ptr_t<T> const& p){
        return p.get();
    }

    template <class T>
    struct pointee< smart_ptr_t<T> >{
        typedef T type;
    };


    inline derived_t * get_pointer(derived_ptr_t const& p){
        return p.get();
    }

    template<>
    struct pointee< derived_ptr_t >{
        typedef derived_t type;
    };

} }


struct base_wrapper_t : base_i, bp::wrapper< base_i > {

    base_wrapper_t()
    : base_i(), bp::wrapper< base_i >()
    {}

    virtual int get_value(  ) const {
        bp::override func_get_value = this->get_override( "get_value" );
        return func_get_value(  );
    }

};

struct derived_wrapper_t : derived_t, bp::wrapper< derived_t > {

    derived_wrapper_t()
    : derived_t(), bp::wrapper< derived_t >()
    {}

    derived_wrapper_t(const derived_t& d)
    : derived_t(d), bp::wrapper< derived_t >()
    {}

    derived_wrapper_t(const derived_wrapper_t&)
    : derived_t(), bp::wrapper< derived_t >()
    {}

    virtual int get_value() const  {
        if( bp::override func_get_value = this->get_override( "get_value" ) )
            return func_get_value(  );
        else
            return derived_t::get_value(  );
    }

    int default_get_value() const  {
        return derived_t::get_value( );
    }

};

BOOST_PYTHON_MODULE( custom_sptr ){
    bp::class_< base_wrapper_t, boost::noncopyable, smart_ptr_t< base_wrapper_t > >( "base_i" )
        .def( "get_value", bp::pure_virtual( &base_i::get_value ) );

    bp::implicitly_convertible< smart_ptr_t< base_wrapper_t >, smart_ptr_t< base_i > >();
    bp::register_ptr_to_python< smart_ptr_t< base_i > >();

    bp::class_< derived_wrapper_t, bp::bases< base_i >, smart_ptr_t<derived_wrapper_t> >( "derived_t" )
        .def( "get_value", &derived_t::get_value, &derived_wrapper_t::default_get_value );

    bp::implicitly_convertible< smart_ptr_t< derived_wrapper_t >, smart_ptr_t< derived_t > >();
    bp::implicitly_convertible< smart_ptr_t< derived_t >, smart_ptr_t< base_i > >();
    bp::implicitly_convertible< derived_ptr_t, smart_ptr_t< derived_t > >();
    bp::register_ptr_to_python< derived_ptr_t >();

    bp::def( "const_ref_get_value", &::const_ref_get_value );
    bp::def( "ref_get_value", &::ref_get_value );
    bp::def( "val_get_value", &::val_get_value );
    bp::def( "create_derived", &::create_derived );
    bp::def( "create_base", &::create_base );
}
