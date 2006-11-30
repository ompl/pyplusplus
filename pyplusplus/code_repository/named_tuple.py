# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

file_name = "named_tuple.py"

code = \
"""# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

class named_tuple(tuple):
    \"\"\"Creates tuple, which allows access to stored values by name and by index.
    
    named_tuple could be constructed exactly in the same way as Python dict.
    \"\"\"

    def __new__(cls, seq=None, **keywd):
        if seq:
            if isinstance( seq, dict ):
                return tuple.__new__( cls, seq.values() )
            else:
                return tuple.__new__( cls, [ val for name, val in seq] )
        else:
            return tuple.__new__( cls, keywd.values() )

    def __init__(self, seq=None, **keywd):
        "named_tuple could be constructed exactly in the same way as Python dict."
        tuple.__init__( self )
        if seq:
            if isinstance( seq, dict ):
                name2value = dict( seq.iteritems() )
            else:
                name2value = dict( seq )
        else:
            name2value = dict( keywd )        
        self.__dict__[ '__name2value' ] = name2value

    def __getattr__(self, name):
        try:
            return self.__dict__['__name2value'][ name ]        
        except KeyError:
            raise AttributeError( "named_tuple has no attribute '%s'" % name )

    def __setattr__(self, name, value):
        raise AttributeError( "named_tuple has no attribute '%s'" % name )

    def __getitem__( self, key ):
        #TODO: it could be nice to support slicing. So the __getitem__ in case of 
        #slicing will return new named_tuple.
        if isinstance( key, basestring ):
            return self.__dict__['__name2value'][ key ]        
        else:
            return super( named_tuple, self ).__getitem__( key )

if __name__ == '__main__':
    nt = named_tuple( a=0, b=1)
    assert nt.a == 0 and nt.b == 1
    a,b = nt
    assert a == 0 and b == 1
    assert nt[ "a" ] == 0 and nt[ "b" ] == 1
    
"""
