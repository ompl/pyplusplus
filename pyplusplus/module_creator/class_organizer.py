# Copyright 2004 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

from pygccxml import declarations
from sets import Set as set

class COLOR:
    WHITE = 0
    GRAY = 1
    BLACK = 2


class class_organizer_t(object):      
    def __init__( self, decls ):
        object.__init__( self )    

        self.__classes = filter( lambda x: isinstance( x, declarations.class_t )
                                 , decls )
        self.__classes.sort( lambda cls1, cls2: cmp( cls1.decl_string, cls2.decl_string ) )
        self.__dependencies_graph = self._build_graph()
        self.__time = 0
        self.__colors = dict( zip( self.__dependencies_graph.keys()
                              , [ COLOR.WHITE ] * len( self.__dependencies_graph ) ) )
        self.__class_discovered = dict( zip( self.__dependencies_graph.keys()
                                        , [ 0 ] * len( self.__dependencies_graph ) ) )
        self.__class_treated = dict( zip( self.__dependencies_graph.keys()
                                     , [ 0 ] * len( self.__dependencies_graph ) ) )

        self.__desired_order = []

        self._topological_sort()
        
    def _build_graph(self):
        full_name = declarations.full_name
        graph = {} # 
        for class_ in self.__classes:
            assert isinstance( class_, declarations.class_t )
            fname = full_name( class_ )
            graph[ fname ] = self.__find_out_class_dependencies( class_ )
        return graph

    def __find_out_class_dependencies( self, class_ ):
        full_name = declarations.full_name
        #class depends on it's base classes
        i_depend_on_them = set( [ full_name( base.related_class ) for base in class_.bases ] )
        #class depends on all classes that used in function as argument
        # types and those arguments have default value
        calldefs = filter( lambda decl: isinstance( decl, declarations.calldef_t )
                           , declarations.make_flatten( class_ ))
        for calldef in calldefs:
            for arg in calldef.arguments:
                if not arg.default_value:
                    continue
                if declarations.is_pointer( arg.type ) and arg.default_value == 0:
                    continue
                base_type = declarations.base_type( arg.type )
                if not isinstance( base_type, declarations.declarated_t ):
                    continue
                top_class_inst = self.__get_top_class_inst( base_type.declaration )
                i_depend_on_them.add( full_name( top_class_inst ) )
        
        i_depend_on_them = list( i_depend_on_them )
        i_depend_on_them.sort()
        return i_depend_on_them

    def __get_top_class_inst( self, decl ):
        curr = decl
        while isinstance( curr.parent, declarations.class_t ):
            curr = curr.parent
        return curr

    def _topological_sort(self):
        self._dfs()
    
    def _dfs( self ):
        for class_ in sorted( self.__dependencies_graph.keys() ):
            if self.__colors[class_] == COLOR.WHITE:
                self._dfs_visit(class_)
                
    def _dfs_visit(self, base):
        self.__colors[base] = COLOR.GRAY
        self.__time += 1
        self.__class_discovered[base] = self.__time
        for derived in self.__dependencies_graph[base]:
            if self.__colors.has_key( derived ) and self.__colors[derived] == COLOR.WHITE:
                self._dfs_visit( derived )
            else:
                pass
                #there is usecase where base class defined within some class
                #but his derives defined out of the class. right now pyplusplus
                #doesn't supports this situation. 

        self.__colors[base] = COLOR.BLACK
        self.__time += 1
        self.__class_treated = self.__time
        self.__desired_order.append(base)
        
    def desired_order(self):
        full_name = declarations.full_name
        fname2inst = {}
        for class_inst in self.__classes:
            fname2inst[ full_name( class_inst ) ] = class_inst
        answer = []
        for fname in self.__desired_order:
            answer.append( fname2inst[fname] )
        return answer

def findout_desired_order( decls ):
    organizer = class_organizer_t( decls )
    return organizer.desired_order()