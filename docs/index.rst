==============
`Py++` package
==============

Py++ is an object-oriented framework for creating a code generator for
`Boost.Python <http://www.boost.org/libs/python/doc/index.html>`_ library and
`ctypes <http://docs.python.org/library/ctypes.html>`_ package.

`Py++` uses few different programming paradigms to help you to expose C++
declarations to Python. This code generator will not stand on your way. It will
guide you through the whole process. It will raise warnings in the case you are
doing something wrong with a link to the explanation. And the most important it
will save your time - you will not have to update code generator script every
time source code is changed.

Code generation process
=======================

Code generation process, using `Py++` consists from few steps. The following
paragraphs will tell you more about every step.


*"read declarations"*
=====================

`Py++` does not reinvent the wheel. It uses `GCC C++ compiler`_ to parse C++
source files. To be more precise, the tool chain looks like this:

1. source code is passed to `GCC-XML`_
2. `GCC-XML`_ passes it to `GCC C++ compiler`_
3. `GCC-XML`_ generates an XML description of a C++ program from GCC's internal
   representation.
4. `Py++` uses `pygccxml <http://pygccxml.readthedocs.org>`_ package to read `GCC-XML`_ generated file.

The bottom line - you can be sure, that all your declarations are read correctly.

.. _`GCC C++ compiler` : http://www.gnu.org/software/gcc


*"build module"*
================

Only very small and simple projects could be exported as is. Most of the projects
still require human invocation. Basically there are 2 questions that you should
answer:

    1. which declarations should be exported
    2. how this specific declaration should be exported or, if I change a little
       a question, what code should be written in order I get access from Python
       to that functionality

Of course, `Py++` cannot answer those question, but it provides maximum help to you.

How can `Py++` help you with first question? `Py++` provides very powerful and
simple query interface. For example in one line of code you can select all free
functions that have two arguments, where the first argument has type ``int &``
and the type of the second argument is any:

.. code-block:: python

  mb = module_builder_t( ... ) #module_builder_t is the main class that
                               #will help you with code generation process
  mb.free_functions( arg_types=[ 'int &', None ] )

Another example - the developer wants to exclude all protected functions from
being exported:

.. code-block:: python

  mb = module_builder_t( ... )
  mb.calldefs( access_type_matcher_t( 'protected' ) ).exclude()

The developer can create custom criteria, for example exclude all declarations
with 'impl' ( implementation ) string within the name.

.. code-block:: python

  mb = module_builder_t( ... )
  mb.decls( lambda decl: 'impl' in decl.name ).exclude()

Note the way the queries were built. You can think about those queries as
the rules, which will continue to work even after exported C++ code was changed.
It means that you don't have to change code generator source code every time.

So far, so good what about second question? Well, by default `Py++` generates a
code that will satisfy almost all developers. `Py++` could be configured in many
ways to satisfy your needs. But sometimes this is still not enough. There are
use cases when you need full control over generated code. One of the biggest
problems, with code generators in general, is modifying generated code and
preserving changes. How many code generators did you use or know, that
allow you to put your code anywhere or to reorder generated code as you wish?
`Py++` allows you to do that.

`Py++` introduces new concept: code creator and code creators tree. You can think
about code creators tree as some kind of `AST`_. The only difference is that code
creators tree provides more specific functionality. For example ``include_t`` code
creator is responsible to create C++ ``include`` directive code. You have full
control over code creators tree, before it is written to disc. Here you
can find UML diagram of almost all code creators: `class diagram`_.

.. _`AST`: http://en.wikipedia.org/wiki/Abstract_syntax_tree
.. _`class diagram`: code_creators_uml.png

At the end of this step you have code creators tree, which is ready to be written
to disc.

*"write code to files"*
-----------------------
During this step `Py++` reads the code creators tree and writes the code to a
disc. The code generation process result should not be different from the one,
which would be achieved by human. For small project writing all code into single
file is good approach, for big ones the code should be split into multiple files.
`Py++` implements both strategies.


Features list
=============

* `Py++` supports almost all features found in `Boost.Python`_ library
* Using `Py++` you can develop few extension modules simultaneously, especially
  when they share the code.
* `Py++` generates code, which will help you:
   * to understand compiler generated error messages
   * to minimize project built time
* `Py++` has few modes of writing code into files:
  * single file
  * multiple files
  * fixed set of multiple files
  * multiple files, where single class code is split to few files
* You have full control over generated code. Your code could be inserted almost
  anywhere.
* Your license is written at the top of every generated file
* `Py++` will check the "completeness" of the bindings. It will check for you
  that the exposed declarations don't have references to unexposed ones.
* `Py++` provides enough functionality to extract source code documentation
  and write it as Python documentation string
* `Py++` provides simple and powerful framework to create a wrapper for
  functions, which could not be exposed as is to `Python`_.

License
=======

`Boost Software License`_.


Documentation contents
======================

.. toctree::
   :maxdepth: 2

   tutorials/tutorials.rst
   quotes.rst
   download.rst
   examples/examples.rst
   links.rst
   comparisons/compare_to.rst
   peps/peps_index.rst
   troubleshooting_guide/lessons_learned.rst
   history.rst
   apidocs/api

.. _`Boost.Python`: http://www.boost.org/libs/python/doc/index.html
.. _`Python`: http://www.python.org
.. _`GCC-XML`: http://www.gccxml.org
.. _`Boost Software License`: http://boost.org/more/license_info.html

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
