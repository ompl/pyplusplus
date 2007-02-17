# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This file contains C++ code - custom call policies
"""


namespace = "pyplusplus::call_policies"

file_name = "__call_policies.pypp.hpp"

code = \
"""// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef call_policies_pyplusplus_hpp__
#define call_policies_pyplusplus_hpp__

#include "boost/python.hpp"
#include "boost/mpl/int.hpp"
#include "boost/function.hpp"
#include "boost/python/suite/indexing/iterator_range.hpp"
#include "boost/python/object/class_detail.hpp"
#include "boost/type_traits/is_same.hpp"
namespace pyplusplus{ namespace call_policies{

namespace bpl = boost::python;

namespace memory_managers{

    struct none{
        template< typename T>
        static void deallocate_array(T*){}
    };
    
    struct delete_{
        template< typename T>
        static void deallocate_array(T* arr){
            delete[] arr;
        }
    };    
    
}/*memory_managers*/


namespace detail{
    
struct make_value_holder{

    template <class T>
    static PyObject* execute(T* p){
        if (p == 0){
            return bpl::detail::none();
        }
        else{
            bpl::object p_value( *p );
            return bpl::incref( p_value.ptr() );
        }
    }

};

template <class R>
struct return_pointee_value_requires_a_pointer_return_type
# if defined(__GNUC__) && __GNUC__ >= 3 || defined(__EDG__)
{}
# endif
;

} //detail

struct return_pointee_value{

    template <class T>
    struct apply{
    
        BOOST_STATIC_CONSTANT( bool, ok = boost::is_pointer<T>::value );
        
        typedef typename boost::mpl::if_c<
            ok
            , bpl::to_python_indirect<T, detail::make_value_holder>
            , detail::return_pointee_value_requires_a_pointer_return_type<T>
        >::type type;
    
    };

};

template< typename CallPolicies, class T >
bpl::object make_object( T x ){
    //constructs object using CallPolicies result_converter
    typedef BOOST_DEDUCED_TYPENAME CallPolicies::result_converter:: template apply< T >::type result_converter_t;
    result_converter_t rc;
    return bpl::object( bpl::handle<>( rc( x ) ) );
}

namespace arrays{

namespace details{

template< unsigned int size, typename MemoryManager, typename CallPolicies>
struct as_tuple_impl{

    template <class U>
    inline PyObject* operator()(U const* arr) const{
        if( !arr ){
            return bpl::incref( bpl::tuple().ptr() );
        }
        bpl::list list_;
        for( unsigned int i = 0; i < size; ++i ){
            list_.append( make_object< CallPolicies>( arr[i] ) );
        }
        MemoryManager::deallocate_array( arr );
        return bpl::incref( bpl::tuple( list_ ).ptr() );
    }
};

}

template< unsigned int size, typename MemoryManager, typename MakeObjectCallPolicies=bpl::default_call_policies>
struct as_tuple{
public:

    template <class T>
    struct apply{
        BOOST_STATIC_CONSTANT( bool, ok = boost::is_pointer<T>::value );
        typedef details::as_tuple_impl<size, MemoryManager, MakeObjectCallPolicies> type;
    };
    
};

} /*arrays*/

namespace detail{  

struct return_raw_data_ref{
    
    template <class T> 
    struct apply{

        BOOST_STATIC_ASSERT( boost::is_pointer<T>::value );
        
        struct type{
            static bool convertible()
            { return true; }

            PyObject* 
            operator()( T return_value) const{ 
                if( !return_value ){
                    return bpl::detail::none();
                }
                else{
                    typedef typename boost::remove_pointer< T >::type value_type;
                    typedef typename boost::remove_const< value_type >::type non_const_value_type;
                    non_const_value_type* data = const_cast<non_const_value_type*>( return_value );
                    return PyCObject_FromVoidPtr( data, NULL ); 
                }
            }
        };

    };

};

} //detail
    
template < typename TGetSize, typename TValueType, typename TValuePolicies=bpl::default_call_policies > 
struct return_range : bpl::default_call_policies{

    typedef return_range< TGetSize, TValueType, TValuePolicies > this_type;

public:

    typedef typename detail::return_raw_data_ref result_converter;
    
    typedef TValueType value_type;
    typedef TGetSize get_size_type;
    typedef TValuePolicies value_policies_type;
    
    typedef bpl::indexing::iterator_range<value_type*> range_type;

    template <class ArgumentPackage>
    static PyObject* postcall(ArgumentPackage const& args, PyObject* result){
        if( result == bpl::detail::none() ){
            return result;
        }
        if( !PyCObject_Check( result ) ){
            throw std::runtime_error( "Internal error: expected to get PyCObject" );
        }
        value_type* raw_data = reinterpret_cast<value_type*>( PyCObject_AsVoidPtr( result ) );
        Py_DECREF(result);//we don't need result anymore
        
        PyObject* self_impl = bpl::detail::get(boost::mpl::int_<0>(),args);
        bpl::object self( bpl::handle<>( bpl::borrowed( self_impl ) ) );

        register_range_class_on_demand();
        
        get_size_type get_size;
        range_type the_range( raw_data, raw_data + get_size( self ) );
        
        bpl::object range_obj( the_range );
        
        return bpl::incref( range_obj.ptr() );
    }
private:

    static void register_range_class( boost::mpl::true_ ){
        //register range class with default call policies
        bpl::class_<range_type>( "_impl_details_range_iterator_",  bpl::init<value_type*, value_type*>() )
            .def(bpl::indexing::container_suite<range_type>() );
    }
    
    static void register_range_class( boost::mpl::false_ ){
        //register range class with non default call policies
        unsigned long const methods_mask 
            = bpl::indexing::all_methods 
              & ~( bpl::indexing::reorder_methods |  bpl::indexing::search_methods ) ;

        typedef bpl::indexing::iterator_range_suite< range_type, methods_mask > suite_type;
        bpl::class_<range_type>( "_impl_details_range_iterator_",  bpl::init<value_type*, value_type*>() )
            .def( suite_type::with_policies( value_policies_type() ) );
    }

    static void register_range_class_on_demand(){
        //Check the registry. If the class doesn't exist, register it.
        bpl::handle<> class_obj(
            bpl::objects::registered_class_object(bpl::type_id<range_type>()));
        
        if( class_obj.get() == 0 ){
            register_range_class( boost::is_same< bpl::default_call_policies, value_policies_type>() );
        }
    }

};

} /*pyplusplus*/ } /*call_policies*/


#endif//call_policies_pyplusplus_hpp__

"""
