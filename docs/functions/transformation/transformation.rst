=======================
Function transformation
=======================

------------
Introduction
------------

During the development of `Python`_ bindings for some C++ library, it might get
necessary to write custom wrapper code for a particular function in order to
make that function usable from `Python`_.

An often mentioned example that demonstrates the problem is the ``get_size()``
member function of a fictitious image class:

.. code-block:: c++

  void get_size(int& width, int& height);

This member function cannot be exposed with standard `Boost.Python`_ mechanisms.
The main reasons for this is that ``int`` is immutable type in `Python`_.
An instance of immutable type could not be changed after construction. The only
way to expose this function to `Python`_ is to create small wrapper, which will
return a tuple. In `Python`_, the above function would instead be invoked like this:

.. code-block:: python

  width, height = img.get_size()

and the wrapper could look like this:

.. code-block:: c++

  boost::python::tuple get_size( const image_t& img ){
      int width;
      int height;
      img.get_size( width, height );
      return boost::python::make_tuple( width, height );
  }

As you can see this function is simply invokes the original ``get_size()`` member
function and return the output values as a tuple.

Unfortunately, C++ source code cannot describe the semantics of an argument so
there is no way for a code generator tool such as :doc:`Py++ <../../index>` to know whether an
argument that has a reference type is actually an output argument, an input
argument or an input/output argument. That's why the user will always have to
"enhance" the C++ code and tell the code generator tool about the missing
information.

Note: C++ fundamental types, enumerations and string are all mapped to `Python`_
immutable types.

Instead of forcing you to write the entire wrapper function, :doc:`Py++ <../../index>` allows you
to provide the semantics of an argument(s) and then it will take care of
producing the correct code:

.. code-block:: python

   from pyplusplus import module_builder
   from pyplusplus import function_transformers as FT

   mb = module_builder.module_builder_t( ... )
   get_size = mb.mem_fun( 'image_t::get_size' )
   get_size.add_transformation( FT.output(0), FT.output(1) )
   #the following line has same effect
   get_size.add_transformation( FT.output('width'), FT.output('height') )

:doc:`Py++ <../../index>` will generate a code, very similar to one found in
``boost::python::tuple get_size( const image_t& img )`` function.

---------
Thanks to
---------

A thanks goes to Matthias Baas for his efforts and hard work. He did a research,
implemented the initial working version and wrote a lot of documentation.

---------------------
Transformers contents
---------------------

:doc:`Py++ <../../index>` comes with few predefined transformers:

.. toctree::

   terminology.rst
   Generated functions name <name_mangling.rst>
   output.rst
   input.rst
   inout.rst
   modify_type.rst
   input_static_array.rst
   output_static_array.rst
   inout_static_array.rst
   transfer_ownership.rst
   input_c_buffer.rst
   from_address.rst
   input_static_matrix.rst
   output_static_matrix.rst
   inout_static_matrix.rst



The set doesn't cover all common use cases, but it will grow with every new
version of :doc:`Py++ <../../index>`. If you created your own transformer consider to contribute
it to the project.

I suggest you to start reading :doc:`output <output>` transformer. It is pretty simple and
well explained.

All built-in transformers could be applied on any function, except constructors
and pure virtual functions. The support for them be added in future releases.

You don't have to worry about call policies. You can set the call policy and
:doc:`Py++ <../../index>` will generate the correct code.

You don't have to worry about the number of arguments, transformers or return
value. :doc:`Py++ <../../index>` handles pretty well such use cases.


.. _`Boost.Python`: http://www.boost.org/libs/python/doc/index.html
.. _`Python`: http://www.python.org
.. _`GCC-XML`: http://www.gccxml.org

