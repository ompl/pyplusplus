#! /usr/bin/python
# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import _crc_

print dir( _crc_ )

from _crc_ import crc_16_type as crc16
from _crc_ import crc_32_type as crc32
from _crc_ import crc_ccitt_type as crc_ccitt
from _crc_ import fast_crc_type as fast_crc

__optimal__ = [ crc16, crc32, crc_ccitt, fast_crc ]

from _crc_ import crc_basic_1
from _crc_ import crc_basic_16
from _crc_ import crc_basic_3
from _crc_ import crc_basic_32
from _crc_ import crc_basic_7

basic = { 
      1 : crc_basic_1
    , 3 : crc_basic_3
    , 7 : crc_basic_7
    , 16 : crc_basic_16
    , 32 : crc_basic_32
}

__basic__ = basic.values()

__all__ = __optimal__ + __basic__

def process_bytes( self, data ):
    for byte in data:
        self.process_byte( byte )

for cls in __all__:
    cls.process_bytes = process_bytes