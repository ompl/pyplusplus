# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import os
import license
import include
import compound
import algorithm
import declaration_based
from pygccxml import utils

class module_t(compound.compound_t):
    """This class represents the source code for the entire extension module.

    The root of the code creator tree is always a module_t object.
    """
    def __init__(self, global_ns, code_generator_type):
        """Constructor.
        """
        compound.compound_t.__init__(self)
        self.__global_ns = global_ns
        self._code_generator = code_generator_type
        
    @property
    def global_ns(self):
        "reference to global_ns ( namespace_t ) declaration"
        return self.__global_ns

    def _get_license( self ):
        if isinstance( self.creators[0], license.license_t ):
            return self.creators[0]
        return None

    def _set_license( self, license_text ):
        if not isinstance( license_text, license.license_t ):
            license_inst = license.license_t( license_text )
        if isinstance( self.creators[0], license.license_t ):
            self.remove_creator( self.creators[0] )
        self.adopt_creator( license_inst, 0 )
    license = property( _get_license, _set_license,
                        doc="""License text.

                        The license text will always be the first children node.
                        @type: str or L{license_t}""")

    def _get_system_files_impl( self ):
        return []

    @utils.cached
    def specially_exposed_decls(self):
        """list of exposed declarations, which were not ``included``, but still
        were exposed. For example, std containers.
        """
        decls = set()
        #select all declaration based code creators
        ccs = filter( lambda cc: isinstance( cc, declaration_based.declaration_based_t )
                      , algorithm.make_flatten_list( self ) )
        #leave only "ignored"
        ccs = filter( lambda cc: cc.declaration.ignore == True, ccs )

        decls = map( lambda cc: cc.declaration, ccs )

        return set( decls )

