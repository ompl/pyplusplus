# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
#TODO: find better place for it

"""
This package contains logging configuration for pyplusplus. Default log level
is DEBUG. Default log messages destination is sys.stdout.
"""

import sys
import logging

logger = logging.getLogger('pyplusplus')
__handler = logging.StreamHandler(sys.stdout)
__handler.setFormatter( logging.Formatter('%(message)s') )
logger.addHandler(__handler) 
logger.setLevel(logging.DEBUG)