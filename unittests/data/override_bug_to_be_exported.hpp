// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#ifndef __final_classes_to_be_exported_hpp__
#define __final_classes_to_be_exported_hpp__

#include <string>

namespace override_bug{

class A
{
  public:
   virtual void foo() const {}
   virtual ~A(){}
};

class B: public A
{
};

inline void invoke_foo( const A& a ){
    a.foo();
};
} 

#endif//__final_classes_to_be_exported_hpp__

