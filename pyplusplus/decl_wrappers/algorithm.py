# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"""
This module is a collection of unrelated algorithms, that works on code creators
tree.
"""

import re

def creators_affect_on_me( me ):
    """This algorithm finds all code creators that can influence on code generated
    by me. Description of algorithm::
    
      [a b c d e f g]
             |
             + [k l m]
                  |
                  + [y x] <-- we are here ( x )
                  
    The answer of this algorithm is [y,l,k,d,c,b,a]
    """
    class impl:
        def __init__( self, creator):
            self._creator = creator
        
        def _get_left_siblings( self, child ):
            if not child or not child.parent:
                return []
            ids = map( id, child.parent.creators )
            child_index = ids.index( id( child ) )
            return child.parent.creators[:child_index]
        
        def _get_definition_set( self, child ):
            answer = []
            while child:
                answer.extend( self._get_left_siblings( child ) )
                child = child.parent
            return answer
        
        def affect_creators(self):
            return self._get_definition_set( self._creator )
    return impl( me ).affect_creators()

__RE_VALID_IDENTIFIER = re.compile( r"[_a-z]\w*", re.I | re.L | re.U )
def create_valid_name(name):
    """
    This function takes valid C++ class\\function name and will return valid
    Python name. I need this function in order to expose template instantiations
    """
    global __RE_VALID_IDENTIFIER
    match_found = __RE_VALID_IDENTIFIER.match(name)
    if match_found and ( match_found.end() - match_found.start() == len(name) ):
        return name
    replace_table = {
          '<'  : '_less_'
        , '>'  : '_grate_'
        , '::' : '_scope_'
        , ','  : '_comma_'
        , ' '  : '_'
        , '\t' : '_'
        , '*'  : '_ptr_'
        , '&'  : '_ref_'
        , '('  : '_obrace_'
        , ')'  : '_cbrace_'
        , '['  : '_o_sq_brace_'
        , ']'  : '_c_sq_brace_'
        , '='  : '_equal_'
        , '.'  : '_dot_'
        , '$'  : '_dollar_'
    }
    for orig, dest in replace_table.items():
        name = name.replace( orig, dest )
    return name


def create_identifier(creator, full_name ):
    from pyplusplus import code_creators
    """
    This function will find all relevant namespace aliases and will return new 
    full name that takes into account namespace aliases. 
    """
    dset = creators_affect_on_me( creator )
    dset = filter( lambda x: isinstance( x, code_creators.namespace_alias_t ), dset )
    full_name = full_name.lstrip( '::' )
    for nsalias in dset:
        fnsname = nsalias.full_namespace_name + '::'
        if full_name.startswith( fnsname ):
            new_name = nsalias.alias + '::' + full_name[ len(fnsname) :  ]
            return new_name
    else:
        return full_name
