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

struct derived_ptr_t : public smart_ptr_t< derived_t >{

    derived_ptr_t()
    : smart_ptr_t< derived_t >()
    {}

    explicit derived_ptr_t(derived_t* rep)
    : smart_ptr_t<derived_t>(rep)
    {}

    derived_ptr_t(const derived_ptr_t& r)
    : smart_ptr_t<derived_t>(r) {}

    derived_ptr_t( const smart_ptr_t< base_i >& r)
    : smart_ptr_t<derived_t>()
    {
        pRep = static_cast<derived_t*>(r.getPointer());
        pUseCount = r.useCountPointer();
        if (pUseCount)
        {
            ++(*pUseCount);
        }
    }

    derived_ptr_t& operator=(const smart_ptr_t< base_i >& r)
    {
        if (pRep == static_cast<derived_t*>(r.getPointer()))
            return *this;
        release();
        pRep = static_cast<derived_t*>(r.getPointer());
        pUseCount = r.useCountPointer();
        if (pUseCount)
        {
            ++(*pUseCount);
        }

        return *this;
    }
};


derived_ptr_t create_derived(){
    return derived_ptr_t( new derived_t() );
}

smart_ptr_t< base_i > create_base(){
    return smart_ptr_t< base_i >( new derived_t() );
}


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
