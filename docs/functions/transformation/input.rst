======================
``input`` transformer
======================

----------
Definition
----------

"input" transformer removes a "reference" type from the function argument.

"input" transformer takes as argument name or index of the original function
argument. The argument should have "reference" type. Support for "pointer" type
will be added pretty soon.

-------
Example
-------

.. code-block:: c++

  #include <string>

  inline void hello_world( std::string& hw ){
      hw = "hello world!";
  }

Lets say that you need to expose ``hello_world`` function. As you know
``std::string`` is mapped to `Python`_ string, which is immutable type, so you
have to create small wrapper for the function. The following :doc:`Py++ <../../index>` code does it for you:

  .. code-block:: python

     from pyplusplus import module_builder
     from pyplusplus import function_transformers as FT

     mb = module_builder.module_builder_t( ... )
     hw = mb.mem_fun( 'hello_world' )
     hw.add_transformation( FT.input(0) )

What you see below is the relevant pieces of generated code:

  .. code-block:: c++

     namespace bp = boost::python;

     static void hello_world_a3478182294a057b61508c30b1361318( ::std::string hw ){
         ::hello_world(hw);
     }

     BOOST_PYTHON_MODULE(...){
         ...
         bp::def( "hello_world", &hello_world_a3478182294a057b61508c30b1361318 );
     }

.. _`Boost.Python`: http://www.boost.org/libs/python/doc/index.html
.. _`Python`: http://www.python.org
.. _`GCC-XML`: http://www.gccxml.org

