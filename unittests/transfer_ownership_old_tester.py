# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import sys
import unittest
import fundamental_tester_base
from pyplusplus import code_creators
from pyplusplus.module_builder import call_policies
from pyplusplus import function_transformers as ft

decref_code = \
"""
virtual ~%(cls)s(){
    Py_DECREF( boost::python::detail::wrapper_base_::get_owner(*this) );
//    if (this->m_pyobj) {
//        Py_DECREF(this->m_pyobj);
//        this->m_pyobj = 0;
//    }
}
"""

incref_code = \
"""
//if( !this->m_pyobj) {
    //this->m_pyobj = boost::python::detail::wrapper_base_::get_owner(*this);
    std::cout << "py owner id: " << (int)(boost::python::detail::wrapper_base_::get_owner(*this));
    //Py_INCREF(this->m_pyobj);
//}
"""

impl_conv_code = \
"""
boost::python::implicitly_convertible< std::auto_ptr< %(from)s >, std::auto_ptr< %(to)s > >();
"""

register_sptr = \
"""
boost::python::register_ptr_to_python< %s >();
"""

class tester_t(fundamental_tester_base.fundamental_tester_base_t):
    EXTENSION_NAME = 'transfer_ownership_old'
    
    def __init__( self, *args ):
        fundamental_tester_base.fundamental_tester_base_t.__init__( 
            self
            , tester_t.EXTENSION_NAME
            , *args )

    def customize( self, mb ):
        event_clss = mb.classes( lambda cls: cls.name in ( 'event_t', 'do_nothing_t' ) )
        for cls in event_clss:
            cls.require_self_reference = True
            cls.set_constructors_body( 'Py_INCREF(self); std::cout<< "self: " << (int)(self) << "\\n" << (int)( boost::python::detail::wrapper_base_::get_owner(*this));' )
            cls.add_wrapper_code( decref_code % { 'cls' : cls.wrapper_alias } )
            #~ cls.add_wrapper_code( 'PyObject* m_pyobj;' )
            #~ cls.set_constructors_body( 'm_pyobj=0;' )
            cls.mem_fun( 'notify' ).add_override_precall_code( incref_code )
            #~ cls.mem_fun( 'notify' ).add_default_precall_code( incref_code )
        
            cls.held_type = 'std::auto_ptr< %s >' % cls.wrapper_alias
            cls.add_registration_code( register_sptr % 'std::auto_ptr< %s >' % cls.decl_string, False )
            cls.add_registration_code( register_sptr % 'std::auto_ptr< %s >' % cls.wrapper_alias, False )
            #~ cls.held_type = 'std::auto_ptr< %s >' % cls.decl_string
            cls.add_registration_code( impl_conv_code % { 'from' : cls.wrapper_alias
                                                          , 'to' : cls.decl_string }
                                       , False)
            for base in cls.recursive_bases:
                if base.access_type == 'public':
                    cls.add_registration_code( #from class to its base
                        impl_conv_code % { 'from' : cls.decl_string
                                           , 'to' : base.related_class.decl_string }
                        , False)
                        
                    cls.add_registration_code( #from wrapper to clas base class
                        impl_conv_code % { 'from' : cls.wrapper_alias
                                            , 'to' : base.related_class.decl_string }
                        , False)

        simulator = mb.class_( 'simulator_t' )
        simulator.mem_fun( 'get_event' ).call_policies \
            = call_policies.return_internal_reference()
        schedule = mb.mem_fun( 'schedule' )
        schedule.add_transformation( ft.transfer_ownership(0), alias='schedule' )
        
    def run_tests( self, module):
        class py_event_t( module.event_t ):
            def __init__( self, container ):
                module.event_t.__init__( self )
                self.container = container
                
            def notify( self ):
                print 'notify'
                self.container.append( 1 )
                
        print 'test started'
        notify_data = []
        simulator = module.simulator_t()
        print 'simulator created'
        event = py_event_t( notify_data )
        print 'py_event_t created: ', id( event )
        simulator.schedule( event )        
        print 'event was shceduled'
        print 'event refcount: ', sys.getrefcount( event )
        print 'simulator refcount: ', sys.getrefcount( simulator )
        #del event
        print 'event was deleted'
        event = simulator.get_event()
        print 'event was restored via saved reference in simulator: ', id( event )
        print 'event refcount: ', sys.getrefcount( simulator.get_event() )
        #print 'call event.notify(): ', simulator.get_event().notify()
        print 'call simulator.run()'
        simulator.run()
        self.failUnless( notify_data[0] == 1 )
        
def create_suite():
    suite = unittest.TestSuite()    
    suite.addTest( unittest.makeSuite(tester_t))
    return suite

def run_suite():
    unittest.TextTestRunner(verbosity=2).run( create_suite() )

if __name__ == "__main__":
    run_suite()
