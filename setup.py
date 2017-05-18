#!/usr/bin/env python
# Copyright 2015 Mark Moll
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

from setuptools import setup

setup(name = "pyplusplus",
      version = "1.8.0",
       author="Roman Yakovenko",
       author_email="roman yakovenko at gmail.com",
       maintainer="Mark Moll",
       maintainer_email="mark moll at gmail.com",
       description="Py++ is a framework of components for creating a C++ code generator using the Boost.Python library",
       url="https://bitbucket.org/ompl/pyplusplus",
       download_url="https://bitbucket.org/ompl/pyplusplus/get/1.8.0.zip",
       license="Boost",
       keywords="C++, declaration parser, python bindings",
       packages=['pyplusplus',
                 'pyplusplus.file_writers',
                 'pyplusplus.code_creators',
                 'pyplusplus.creators_factory',
                 'pyplusplus.code_repository',
                 'pyplusplus.code_repository.indexing_suite',
                 'pyplusplus.decl_wrappers',
                 'pyplusplus.module_builder',
                 'pyplusplus.utils',
                 'pyplusplus.function_transformers',
                 'pyplusplus._logging_',
                 'pyplusplus.messages'],
      install_requires=['pygccxml'],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Operating System :: MacOS :: MacOS X",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Programming Language :: Python",
          "Topic :: Software Development"]
)
