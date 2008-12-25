# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import code_creator


class library_reference_t(code_creator.code_creator_t):
    """Creates reference to a library"""

    def __init__( self, library_var_name, library_path, is_cpp_library ):
        code_creator.code_creator_t.__init__(self)
        self._library_path = library_path
        self._is_cpp_library = is_cpp_library
        self._library_var_name = library_var_name

    def _create_impl(self):
        return '%(var)s = ctypes.%(loader)s( r"%(path)s" )' \
               % dict( var=self._library_var_name
                       , loader=self.iif( self._is_cpp_library, 'CPPDLL', 'CDLL' )
                       , path=self._library_path )


    def _get_system_headers_impl( self ):
        return []

if __name__ == '__main__':
    lr = library_reference_t( 'library', r'c:\temp\x1.dll', False )
    print lr.create()
    lr = library_reference_t( 'library', r'c:\temp\x1.dll', True )
    print lr.create()
