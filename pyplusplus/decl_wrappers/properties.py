# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

"defines property_t helper class"

import algorithm
from pygccxml import declarations

class property_t( object ):
    def __init__( self, name, fget, fset=None, doc='', is_static=False ):
        self._name = name
        self._fget = fget
        self._fset = fset
        self._doc = doc
        self._is_static = is_static

    @property
    def name( self ):
        return self._name

    @property
    def fget( self ):
        return self._fget

    @property
    def fset( self ):
        return self._fset

    @property
    def doc( self ):
        return self._doc

    @property
    def is_static( self ):
        return self._is_static

    def __str__( self ):
        desc = []
        desc.append( 'fget=%s' % declarations.full_name( self.fget ) )
        if self.fset:
            desc.append( ', ' )
            desc.append( 'fset=%s' % declarations.full_name( self.fset ) )
        return "property [%s]"% ''.join( desc )


class property_recognizer_i(object):
    def __init__( self ):
        object.__init__( self )

    def create_property( self, fget, fset ):
        raise NotImplementedError()

    def create_read_only_property( sefl, fget ):
        raise NotImplementedError()

class name_based_recognizer_t( property_recognizer_i ):
    def __init__( self ):
        property_recognizer_i.__init__( self )
        self.__prefixes = (
            (  'is', 'set' )
          , ( 'get', 'set' )
          , ( 'has', 'set' )
          , (    '', 'set' ) )

    def check_prefix( self, name, prefix ):
        if len( prefix ) >= len( name ):
            return False
        if not name.startswith( prefix ):
            return False
        return True

    def check_name_compatibility( self, gname, sname, gprefix, sprefix ):
        if not self.check_prefix( gname, gprefix ):
            return False
        if not self.check_prefix( sname, sprefix ):
            return False
        if gname[ len( gprefix ): ] != sname[ len( sprefix ): ]:
            return False
        return True

    def make_std_convention( self, gprefix, sprefix ):
        convert = lambda x: x + '_'
        if gprefix:
            gprefix = convert( gprefix )
        return ( gprefix, convert( sprefix ) )

    def make_u_camel_convention( self, gprefix, sprefix ):
        convert = lambda x: x[0].upper() + x[1:]
        if gprefix:
            gprefix = convert( gprefix )
        return ( gprefix, convert( sprefix ) )

    def make_l_camel_convention( self, gprefix, sprefix ):
        convert = lambda x: x[0].lower() + x[1:]
        if gprefix:
            gprefix = convert( gprefix )
        return ( gprefix, convert( sprefix ) )

    def find_out_prefixes( self, gname, sname ):
        convention_makers = [
            self.make_std_convention #longest first
          , self.make_u_camel_convention
          , self.make_l_camel_convention ]

        for convention_maker in convention_makers:
            for g, s in self.__prefixes:
                gc, sc = convention_maker( g, s )
                if self.check_name_compatibility( gname, sname, gc, sc ):
                    return ( gc, sc )
        return None

    def find_out_ro_prefixes( self, gname ):
        convention_makers = [
            self.make_std_convention #longest first
          , self.make_u_camel_convention
          , self.make_l_camel_convention ]

        for convention_maker in convention_makers:
            for g, unused in self.__prefixes:
                if not g:
                    continue
                gc, unused = convention_maker( g, 'set' )
                if self.check_prefix( gname, gc ):
                    return gc
        return ''

    def check_type_compatibility( self, fget, fset ):
        #algorithms allows "const" differences between types
        t1 = fget.return_type
        t2 = fset.arguments[0].type

        if declarations.is_same( t1, t2 ):
            return True
        elif declarations.is_pointer( t1 ) and declarations.is_pointer( t2 ):
            t1 = declarations.remove_cv( declarations.remove_pointer( t1 ) )
            t2 = declarations.remove_cv( declarations.remove_pointer( t2 ) )
            return declarations.is_same( t1, t2 )
        elif declarations.is_reference( t1 ) and declarations.is_reference( t2 ):
            t1 = declarations.remove_cv( declarations.remove_reference( t1 ) )
            t2 = declarations.remove_cv( declarations.remove_reference( t2 ) )
            return declarations.is_same( t1, t2 )
        else:
            return False

    def find_out_property_name( self, fget, prefix ):
        if fget.name == prefix:
            #use class name for property name
            return algorithm.create_valid_name( fget.parent.name )
        else:
            return fget.name[len(prefix):]

    def create_property( self, fget, fset ):
        if not self.check_type_compatibility( fget, fset ):
            return None
        found = self.find_out_prefixes( fget.name, fset.name )
        if not found:
            return None
        return property_t( self.find_out_property_name( fget, found[0] ), fget, fset )

    def create_read_only_property( self, fget ):
        found = self.find_out_ro_prefixes( fget.name )
        if None is found:
            return None
        else:
            return property_t( self.find_out_property_name( fget, found ), fget )

class properties_finder_t:
    def __init__( self, cls, recognizer=None, exclude_accessors=False ):
        self.cls = cls
        if None is recognizer:
            recognizer = name_based_recognizer_t()
        self.recognizer = recognizer
        self.exclude_accessors = exclude_accessors
        self.getters, self.setters \
            = self.__get_accessors( cls.member_functions( recursive=False, allow_empty=True ) )

        inherted_mem_funs = []
        for hierarchy_info in cls.recursive_bases:
            if hierarchy_info.related_class.ignore: #don't scan excluded classes
                continue
            if 'public' != hierarchy_info.access_type: #don't scan non public hierarchy
                continue
            base_cls = hierarchy_info.related_class
            inherted_mem_funs.extend( base_cls.member_functions( recursive=False, allow_empty=True ) )

        self.inherited_getters, self.inherited_setters \
            = self.__get_accessors( inherted_mem_funs )

    def __is_getter( self, mem_fun ):
        if mem_fun.arguments:
            return False
        if declarations.is_void( mem_fun.return_type ):
            return False
        if not mem_fun.has_const:
            return False
        return True

    def __is_setter( self, mem_fun ):
        if len( mem_fun.arguments ) != 1:
            return False
        if not declarations.is_void( mem_fun.return_type ):
            return False
        if mem_fun.has_const:
            return False
        return True

    def __get_accessors( self, mem_funs ):
        getters = []
        setters = []
        for mem_fun in mem_funs:
            if mem_fun.ignore:
                continue
            elif mem_fun.access_type != 'public':
                continue
            elif mem_fun.has_static:
                continue #TODO: should be supported
            elif mem_fun.virtuality == declarations.VIRTUALITY_TYPES.PURE_VIRTUAL:
                continue
            elif self.__is_getter( mem_fun ):
                getters.append( mem_fun )
            elif self.__is_setter( mem_fun ):
                setters.append( mem_fun )
            else:
                continue
        return ( getters, setters )

    def find_properties( self, getters, setters, used_getters, used_setters ):
        properties = []
        for fget in getters:
            if fget in used_getters:
                continue
            for fset in setters:
                if fset in used_setters:
                    continue
                property_ = self.recognizer.create_property( fget, fset )
                if property_:
                    used_getters.add( fget )
                    used_setters.add( fset )
                    properties.append( property_ )
                    break
        return properties

    def __call__( self ):
        used_getters = set()
        used_setters = set()
        properties = []
        #this get, this set
        properties.extend(
            self.find_properties( self.getters, self.setters, used_getters, used_setters ) )
        #this get, base set
        properties.extend(
            self.find_properties( self.getters, self.inherited_setters, used_getters, used_setters ) )
        #base get, this set
        properties.extend(
            self.find_properties( self.inherited_getters, self.setters, used_getters, used_setters ) )

        for fget in self.getters:
            if fget in used_getters:
                continue
            property_ = self.recognizer.create_read_only_property( fget )
            if property_:
                used_getters.add( fget )
                properties.append( property_ )

        if self.exclude_accessors:
            map( lambda accessor: accessor.exclude(), used_getters )
            map( lambda accessor: accessor.exclude(), used_setters )

        return properties

def find_properties( cls, recognizer=None, exclude_accessors=False ):
    pf = properties_finder_t( cls, recognizer, exclude_accessors )
    properties = pf()
    return properties
