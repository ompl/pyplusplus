// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __function_transformations_to_be_exported_hpp__
#define __function_transformations_to_be_exported_hpp__

namespace ft{

struct image_t{

    image_t( unsigned int h, unsigned int w )
    : m_height( h )
      , m_width( w )
    {}

    // Made the method 'virtual' for now because func transformers
    // are currently only taken into account on virtual functions.
    virtual void get_size( unsigned int& h, unsigned int& w ){
        h = m_height;
        w = m_width;
    }

    // Return only one value
    virtual void get_one_value(unsigned int& h) {
        h = m_height;
    }

    // Like get_size() but with a return type and an additional argument
    // that has to be kept in the signature
    virtual int get_size2( unsigned int& h, unsigned int& w, int noref=0 ){
        h = m_height;
        w = m_width;
	return noref;
    }

    // A method with an input argument
    virtual int input_arg(int& in){
      return in;
    }

    // A method taking an input array of fixed size
    virtual int fixed_input_array(int v[3]) {
      return v[0]+v[1]+v[2];
    }

    // A method with a output array of fixed size
    virtual void fixed_output_array(int v[3]) {
      v[0] = 1;
      v[1] = 2;
      v[2] = 3;
    }

    unsigned int m_width;
    unsigned int m_height;

};

// Provide an instance created in C++ (i.e. this is not a wrapper instance)
image_t cpp_instance(12,13);
image_t& get_cpp_instance() {
  return cpp_instance;
}

inline void
get_image_size( image_t& img, unsigned int& h, unsigned int& w ){
    img.get_size( h, w );
}

// This is used for calling img.get_one_value() on an instance passed
// in by Python.
unsigned int get_image_one_value( image_t& img ) {
  unsigned int v;
  img.get_one_value(v);
  return v;
}

// This is used for calling img.fixed_output_array() on an instance passed
// in by Python.
int image_fixed_output_array( image_t& img) {
  int v[3];
  img.fixed_output_array(v);
  return v[0]+v[1]+v[2];
}

//////////////////////////////////////////////////////////////////////

// A class without any virtual members
struct no_virtual_members_t
{
  bool member(int& v) { v=17; return true; }
};

/*
struct ft_private_destructor_t{
	static void get_value( int& x ){ x = 21; }
private:
	~ft_private_destructor_t(){}
};
*/
}

#endif//__function_transformations_to_be_exported_hpp__
