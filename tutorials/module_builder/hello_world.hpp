// Copyright 2004 Roman Yakovenko.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

/******************************************************************************************
 *                                                                                        *
 *   ANY CHANGE IN THIS FILE MUST BE REFLECTED IN docs/tutorials DIRECTORY                *
 *                                                                                        *
 *****************************************************************************************/

#ifndef __hello_world_hpp__
#define __hello_world_hpp__

#include <string>

//I want to rename color to Color
enum color{ red, green, blue };

struct animal{
    
    animal( const std::string& name="" )
    : m_name( name )
    {}
        
    //I need to set call policies to the function
    const std::string* get_name_ptr() const
    { return &m_name; }

    const std::string& name() const
    { return m_name; }
        
private:    
    std::string m_name;

};

//I want to exclude next declarations:
struct impl1{};
struct impl2{};

inline int* get_int_ptr(){ return 0;}    
inline int* get_int_ptr(int){ return 0;}
inline int* get_int_ptr(double){ return 0;}
    
#endif//__hello_world_hpp__

