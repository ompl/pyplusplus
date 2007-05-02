# -*- coding: utf-8 -*-
# Copyright 2004 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
'''
This module contains classes for settings and parameters
'''
from model.etree_extension import XmlAttribFinder
from shutil import copyfile
# Python 2.5
from xml.etree.ElementTree import ElementTree
import os
import wx

class BaseSettings:
    '''
    Base class for settings as a collection of parameters
    '''
    def __init__(self, ide_ui, param_obj):
        self._file_name = None # filename of settings
        self._ide_ui = ide_ui
        self._param_obj = param_obj        
        
    def set_changed(self):
        '''
        Inform, that any parameter has changed
        '''
        self._changed = True
        
    def get_changed(self):
        '''
        Access changed information
        '''
        return self._changed
    
    def get_file_name(self):
        '''
        Return file path of settings
        '''
        return self._file_name
    
    def get_param(self, xml_attrib_name):
        '''
        Return parameter as string        
        @param xml_attrib_name: Name of parameter
        '''
        
        ide_ui = self._ide_ui #@UnusedVariable
        param_obj = self._param_obj #@UnusedVariable
                
        for cur_name, rel_obj_str in self._param_list:
            if cur_name == xml_attrib_name:
                param = ParameterAccess(eval(rel_obj_str))
                return param.get_related_object_value()
                
        raise RuntimeError, "Parameter:%s not defined" % xml_attrib_name

    def _load(self, file_name):#@UnusedVariable
        '''
        Load settings from given file
        @param file_name: path of file. Format is XML.
        @param ide_ui: wxPython ctrl of ide 
        @param param_obj: object holding parameters
        '''
        self._file_name = file_name

        ide_ui = self._ide_ui #@UnusedVariable
        param_obj = self._param_obj #@UnusedVariable

        root_element = ElementTree(file=file_name).getroot()
        attrib_finder = XmlAttribFinder(root_element)
        
        # Loop through our parameter list
        for xml_attrib_name, rel_obj_str in self._param_list:
            # In eval we need ide_ui and param_obj
            # print "XML:%s obj_str:%s" % (xml_attrib_name, rel_obj_str)
            param = ParameterAccess(eval(rel_obj_str))
            attrib_val = attrib_finder.get_val(xml_attrib_name)
            param.update_related_object(attrib_val)
            
    def _save(self, file_name):
        '''
        Save settings into the given file
        @param file_name: path of file. Format is XML. 
        @param ide_ui: wxPython ctrl of ide
        @param param_obj: object holding parameters
        '''
        
        self._file_name = file_name

        ide_ui = self._ide_ui #@UnusedVariable
        param_obj = self._param_obj #@UnusedVariable
                
        etree = ElementTree(file=file_name)
        root_element = etree.getroot()
        
        attrib_finder = XmlAttribFinder(root_element)
        
        for xml_attrib_name, rel_obj_str in self._param_list:
            # In eval we need ide_ui and param_obj
            param = ParameterAccess(eval(rel_obj_str))
            attrib, attrib_key = attrib_finder.get_obj(xml_attrib_name)
            attrib[attrib_key] = param.get_related_object_value()
            
        # Write XML-File
        etree.write(file_name)
        
        self._changed = False        
        
    
class IdeSettings(BaseSettings):
    '''
    Abstracts the settings of the ide 
    '''
    def __init__(self, ide_ui, param_obj):
        
        self._param_list = [
            ('project.maxNumInMenue',
            'param_obj.max_num_recent_projects'),
            
            ('project.recentProjects',
            'param_obj.recent_prj_list'),
            
            ('project.lastPrjPath',
            'param_obj.last_prj_path'),
            
            ('project.lastIncPath',
            'param_obj.last_inc_path')
            
            ]
                
        BaseSettings.__init__(self, ide_ui, param_obj)
    
    def load(self):
        '''
        Load ide settings      
        '''
        ide_file_name = self._get_ide_file_name()
        self._load(ide_file_name)
        
    def save(self):
        '''
        Save settings 

        '''
        ide_file_name = self._get_ide_file_name()
        self._save(ide_file_name)
    
    def _get_ide_file_name(self):
        '''
        Get the file name of the ide settings filE. If the file doesen't exist 
        we copy a template fiel into the location
        @param file_path: File path to check
        '''
        try:
            home_dir = os.environ['HOME']
        except KeyError:
            home_dir = os.getcwd()
        
        file_path = os.path.join(home_dir, self._ide_file_name )
        
        if not os.path.exists(file_path):
            print "File copied !!"
            copyfile(self._ide_template_path, file_path)
            
        return file_path
    
    # Project template file
    _ide_template_path = "./IdeTemplate.xml"
    _ide_file_name = ".pyplusplus_ide"
            
class ProjectSettings(BaseSettings):
    '''
    Abstracts the settings of a project 
    '''
    def __init__(self, ide_ui, param_obj):
        
        BaseSettings.__init__(self, ide_ui, param_obj)
        
        # This list contains tuples of ui elements and the related
        # attribute of the project file
        self._param_list = [
            ('gccXmlSettings.headerPath',
            'ide_ui.textHeader'),
        
            ('gccXmlSettings.gccXmlPath',
             'ide_ui.textGccXml'),
            
            ('gccXmlSettings.includePathList',
             'ide_ui.listIncludes'),
             
             ('gccXmlSettings.macroList',
             'ide_ui.listMacros'),
             
             ('guiGeometry.size',
             'ide_ui'),
             
             ('guiGeometry.horizontalSplitter',
             'ide_ui.splitterHorizontal'),
             
             ('guiGeometry.verticalSplitter',
             'ide_ui.splitterVertical')
        ]
        
        self._changed = False
            
    def load(self, file_name):
        '''
        Load settings from given file
        @param file_name: path of file. Format is XML.
        '''
        self._load(file_name)
        
    def save(self, file_name): 
        '''
        Save settings into the given file
        @param file_name: path of file. Format is XML. 
        '''
        # Assert new prj file
        self._assert_prj_file(file_name)
        self._save(file_name)
        
    def _assert_prj_file(self, file_path):
        '''
        Assert that the given file exists. If not we copy the template
        @param file_path: File path to check
        '''
        if not os.path.exists(file_path):
            copyfile(self._prj_template_path, file_path)

    # Project template file
    _prj_template_path = "./ProjectTemplate.xml"

class ParameterContainer:
    '''
    Abstracts one parameter with  getter and setter
    '''
    def __init__(self, p_type, init_val=None):
        self._type = p_type
        self._val = init_val
    
    def set(self, val):
        '''
        Set the related parameter
        @param val: new value
        '''
        self._val = self._type(val)
        
    def get(self):
        '''
        Get the related parameter
        '''
        
        return self._val
    
    def get_type(self):
        '''
        Get the (python) type of the parameter
        '''
        return self._type
        

class ParameterAccess:
    ''' 
    Abstracts the access (setting and getting) of a parameter. This class
    has knowledge of wxPython controls (and know how to handle them). 
    Currently we support:
    - wxTextCtrl
    - wxListCtrl
    - wxFrame
    - wxSplitterWindow
    - ParameterContainer
    '''
    def __init__(self, related_object):
        self._rel_obj = related_object
    
    def update_related_object(self, param_value):
        '''
        Set the value of the related object with given param_value
        @param param_value: parameter value to use
        '''
        
        #print ">>> rel obj:", self._rel_obj, "val:", param_value
        
        # Handle wxTextCtrl
        if isinstance(self._rel_obj, wx.TextCtrl):
            # We need a string
            str_param_value = str(param_value)
            self._rel_obj.SetValue(str_param_value)

        # Handle wxListCtrl
        elif isinstance(self._rel_obj, wx.ListCtrl):
            list_param_value = eval(param_value)
            assert(isinstance(list_param_value, list))
            cur_num = 0
            for list_el in list_param_value:
                self._rel_obj.InsertStringItem(cur_num, list_el)
                cur_num += 1
                
        # Handle wxFrame
        elif isinstance(self._rel_obj, wx.Frame):
            tup_size = eval(param_value)
            assert(isinstance(tup_size, tuple))
            x = tup_size[0]
            y = tup_size[1]
            wid = tup_size[2]
            high = tup_size[3]
            self._rel_obj.SetDimensions(x, y, wid, high)
            
        # SplitterWindow
        elif isinstance(self._rel_obj, wx.SplitterWindow):
            int_sash_pos = int(param_value)
            self._rel_obj.SetSashPosition(int_sash_pos, True)
        
        # ParameterContainer 
        elif isinstance(self._rel_obj, ParameterContainer):
            if self._rel_obj.get_type() == list:
                eval_param_value = eval(param_value)
            elif self._rel_obj.get_type() == int:
                eval_param_value = eval(param_value)
            elif self._rel_obj.get_type() == str:
                eval_param_value = param_value
            elif self._rel_obj.get_type() == unicode:
                eval_param_value = unicode(param_value)
            else:
                raise RuntimeError, "Unupported typ found", \
                    self._rel_obj.get_type()
                
            cnv_param_val = self._rel_obj.get_type()(eval_param_value)
            self._rel_obj.set(cnv_param_val)

        else:
            raise RuntimeError, "Unsupported type %s" % self._rel_obj.__class__
            
    def get_related_object_value(self):
        '''
        Get value of the related object
        @return value as string
        '''
        
        #print ">>>", self._rel_obj
        
        str_param_value = "Value not specified"
        
        # Handle wxTextCtrl
        if isinstance(self._rel_obj, wx.TextCtrl):
            # We need a string
            str_param_value = self._rel_obj.GetValue()

        # Handle wxListCtrl
        elif isinstance(self._rel_obj, wx.ListCtrl):

            list_of_ctrl = []

            for cur_num in range(self._rel_obj.GetItemCount()):
                list_el = self._rel_obj.GetItemText(cur_num)
                list_of_ctrl.append(list_el)
                cur_num += 1
            str_param_value = str(list_of_ctrl)
                
        # Handle wxFrame
        elif isinstance(self._rel_obj, wx.Frame):
            x,y = self._rel_obj.GetPositionTuple()
            wid, high = self._rel_obj.GetSizeTuple()
            dim = (x,y,wid,high)
            str_param_value = str(dim)
        
        # SplitterWindow
        elif isinstance(self._rel_obj, wx.SplitterWindow):
            sash_pos = self._rel_obj.GetSashPosition()
            str_param_value = str(sash_pos)

        # Handle ParameterContainer
        elif isinstance(self._rel_obj, ParameterContainer):
            str_param_value = str(self._rel_obj.get())
                        
        else:
            raise RuntimeError, "Unsupported type %s" % self._rel_obj.__class__
        
        return str_param_value
        