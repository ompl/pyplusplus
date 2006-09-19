#include "smart_ptr.h"

struct base_i{
public:
    virtual ~base_i() { }
    virtual int get_value() const = 0;
};


struct derived_t : base_i{
    derived_t()
    {}

    virtual int get_value() const{
        return 11;
    }
};

//Next function could be exposed, but it could not be solved
//This is the explanation David Abrahams gave:
//Naturally; there is no instance of smart_ptr_t<base_i> anywhere in the
//Python object for the reference to bind to. The rules are the same as in C++:
//
//  int f(smart_ptr_t<base_i>& x) { return 0; }
//  smart_ptr_t<base_wrapper_t> y;
//  int z = f(y);                // fails to compile

inline int
ref_get_value( smart_ptr_t< base_i >& a ){
    return a->get_value();
}

inline int
val_get_value( smart_ptr_t< base_i > a ){
    return a->get_value();
}

inline int
const_ref_get_value( const smart_ptr_t< base_i >& a ){
    return a->get_value();
}
