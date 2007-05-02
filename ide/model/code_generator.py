# -*- coding: utf-8 -*-
# Copyright 2004 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

'''
Code generation is started in a own thread. To exchange data, queues
are used.
'''

import time

def gen_xml(params, q_result, q_error):
    '''
    Generate XML code
    @param params: List of parameters [gccxml,incPath,macros]
    @param q_result: python queue to put result in
    @param q_error: python queue to put error in
    @return None (isn't evaluated)
    '''

    gcc_xml = params[0]
    inc_path_list = params[1]
    macro_list = params[2]
    
    time.sleep(1)
    q_result.put("This is dummy data of gen_xml\n")
    q_error.put("This is dummy error gen_xml")
    time.sleep(4)
    q_result.put("This is dummy data of gen_xml")
    q_error.put("This is dummy error of gen_xml")
    
def gen_cpp(params, q_result, q_error):
    '''
    Generate cpp (Boost.Python) code
    @param params: List of parameters [gccxml,incPath,macros]
    @param q_result: python queue to put result in
    @param q_error: python queue to put error in
    @return None (isn't evaluated)
    '''
    pass

def gen_pypp(params, q_result, q_error):
    '''
    Generate Python (Py++) code
    @param params: List of parameters [gccxml,incPath,macros]
    @param q_result: python queue to put result in
    @param q_error: python queue to put error in
    @return None (isn't evaluated)
    '''
    pass

    