=================================================
Automatic conversion between C++ and Python types
=================================================

------------
Introduction
------------

-------
Content
-------

This example actually consist from 2 small, well documented examples.

The first one shows how to handle conversion between tuples: `boost::tuples::tuple`_
and Python tuple.

.. _`boost::tuples::tuple` : http://boost.org/libs/tuple/doc/tuple_users_guide.html

The second one shows how to add an automatic conversion from Python tuple to
some registered class. The class registration allows you to use its functionality
and enjoy from automatic conversion.

Files
-----

.. toctree::

   tuples.hpp.rst
   tuples_tester.cpp.rst
   custom_rvalue.cpp.rst
   sconstruct.rst
   test.py.rst

--------
Download
--------

:download:`automatic_conversion.zip`
