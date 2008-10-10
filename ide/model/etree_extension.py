# -*- coding: utf-8 -*-
# Copyright 2004-2008 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
from xml.etree.ElementTree import ElementTree

class ElNotFound(Exception):
    ''' 
    Exception element not found 
    '''
    pass

class AttribNotFound(Exception):
    '''
    Execption attribute not found
    '''
    pass

class XmlElFinder:
    '''
    Find a element in a Tree (xml.etree.ElementTree)
    '''
    def __init__(self, root_el):
        self._root = root_el # Must be of typ xml.etree.ElementTree
        self._finder = None
        
    def get_obj(self, element_text):
        '''
        Find and return XML element object (Element)
        @param element_text: Textual description of element to find. Hirarchie
        is seperated by '.' Ex.: 'rootNode.childNode.element'
        @return: Element object
        '''
        
        child_el = None
        self._finder = self._root
        
        for el_name in element_text.split("."):
            child_el = self._finder.find(el_name)
    
            # Child not found
            if child_el == None:
                raise ElNotFound, "Cannot find Element %s in %s" % \
                    (el_name, element_text)

            self._finder = ElementTree(child_el)
            
        return child_el
    
class XmlAttribFinder:
    '''Find a attribute in a Tree (xml.etree.ElementTree)'''
    def __init__(self, root_el):
        self._el_finder = XmlElFinder(root_el)
        
    def get_obj(self, attrib_text):
        '''
        Find and return attribute as tuple
        @param attrib_text: Textual description of attribute to find. Hirarchie
        is seperated by '.' Ex.: 'rootNode.childNode.element.attrib1'
        @return: (<allAttribDict>, <relatedAttribName>) This means a tuple 
        cintaining all attributes of parent element and name of attribute. 
        '''
        el_text = attrib_text[0 : attrib_text.rfind(".")]
        attrib_name = attrib_text[attrib_text.rfind(".") + 1 : ]
        element = self._el_finder.get_obj(el_text)
        return (element.attrib, attrib_name)        
        
    def get_val(self, attrib_text):
        '''
        Find and return attribute value 
        @param attrib_text: Textual description of attribute to find. Hirarchie
        is seperated by '.' Ex.: 'rootNode.childNode.element.attrib1'
        @return Attribute value
        '''
        attrib_value = None
        
        el_text = attrib_text[0 : attrib_text.rfind(".")]
        attrib_name = attrib_text[attrib_text.rfind(".") + 1 : ]
        element = self._el_finder.get_obj(el_text)
        
        try:
            attrib_value = element.attrib[attrib_name]
            
        except KeyError:
            raise AttribNotFound, "Cannot find attribute '%s' in element '%s'" \
                % (attrib_name, el_text)

        return attrib_value

        
        