# -*- coding: utf-8 -*-
# Copyright 2004 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

import wx
from views import dialog_macro

""" Contoller class. Part of MVC
Responsibility: Glue view and model code:
- Handle all events from view (p.e. button) """
class MainController:
    def __init__(self, view):
        self._view = view
        
        # Give controller object to the view
        self._view.set_controller(self)
    
    def DoRemoveCurInclude(self):
        """Remove current selected Include item"""
        cur_num = self._view.currentItemInclude
        if None == cur_num:
            return
        self._view.listIncludes.DeleteItem(cur_num)
        
    def DoRemoveCurMacro(self):
        """Remove current selected Macro item"""
        cur_num = self._view.currentItemMacro
        if None == cur_num:
            return
        self._view.listMacros.DeleteItem(cur_num)
        
    def GenXmlCode(self):
        """ Generate XML code"""
        self._appendOutText("Generation of XML code staretd")
        
        for i in range(0,5):
            self._view.listIncludes.InsertStringItem(i, "First Element - this is a long")
    
    def GenCppCode(self):
        """ Generate Boost.Python code"""
        self._appendOutText("Generation of C++ code for Boost.Python started")        
        
    def GenPyPPCode(self):
        """ Generate Py++ code"""
        self._appendOutText("Generation of Py++ code started")
        
    def OpenDlgHeader(self):
        """Open dialog to get header file"""
        self._openFileDlgWithRelatedWxText( self._view.textHeader, 
                                           "Choose a Header file",
                                           "Header (*.h)|*.h|All Files(*)|*")
                        
    def OpenDlgGccXml(self):
        """Open dialog to get GccXml executable"""
        self._openFileDlgWithRelatedWxText( self._view.textGccXml, 
                                           "Choose GccXml executable",
                                           "All Files(*)|*")
    
    def OpenDlgEditCurInclude(self):
        """ """
        cur_num = self._view.currentItemInclude
        if None == cur_num:
            return
        start_dir = self._view.listIncludes.GetItemText(cur_num)
        dialog = wx.DirDialog(self._view, "Edit include directory", start_dir)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self._view.listIncludes.DeleteItem(cur_num)
                self._view.listIncludes.InsertStringItem(
                                                     cur_num, dialog.GetPath())
        finally:
            dialog.Destroy()
    
    def OpenDlgEditCurMacro(self):
        """ """
        cur_num = self._view.currentItemMacro
        if None == cur_num:
            return
        macro = self._view.listMacros.GetItemText(cur_num)
        dialog = dialog_macro.MacroDialog(self._view, macro)
        try:
            if dialog.ShowModal() == wx.OK:
                self._view.listMacros.DeleteItem(cur_num)
                
                new_macro = dialog.textMacro.GetLineText(0)
                self._view.listMacros.InsertStringItem(cur_num, new_macro)
        finally:
            dialog.Destroy()
        
    def OpenDlgAddInclude(self):
        """ """
        dialog = wx.DirDialog(self._view, "Choose include directory", ".")
        try:
            if dialog.ShowModal() == wx.ID_OK:
                
                cur_num = self._view.listIncludes.GetItemCount()
                dir_path = dialog.GetPath()
                
                # Check weather path is already in list
                if not self._checkItemIsInList(dir_path, 
                                               self._view.listIncludes):
                    
                    self._view.listIncludes.InsertStringItem(
                                     cur_num, dir_path)
        finally:
            dialog.Destroy()
            
    def OpenDlgAddMacro(self):
        """ """
        dialog = dialog_macro.MacroDialog(self._view)
        
        if dialog.ShowModal() == wx.OK:
            
            cur_num = self._view.listMacros.GetItemCount()
            new_macro = dialog.textMacro.GetLineText(0)

            # Check weather macro is already in list
            if not self._checkItemIsInList(new_macro, self._view.listMacros):      
               self._view.listMacros.InsertStringItem(cur_num, new_macro)
            


    def _openFileDlgWithRelatedWxText(self, 
                                      related_wx_text,
                                      caption_txt="",
                                      file_filter="All Files(*)|*", 
                                      dir_path="."):
        """Open file open dialog and insert file in related wxText ctrl"""
        dialog = wx.FileDialog(self._view, caption_txt, 
                               dir_path, "", file_filter, wx.OPEN)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                related_wx_text.Clear()
                related_wx_text.AppendText(dialog.GetPath())
        finally:
            dialog.Destroy()
            
    def _checkItemIsInList(self, item, wx_list):
        idx = wx_list.FindItem(0, item)
        if idx == -1:
            return False
        else:
            return True
    
        
    def _appendOutText(self, text, type_of_text = 0):
        """ append text with different error level"""
        text_ctrl = self._view.textOutput
        type_txt = "INFO"
        # Error
        if type_of_text == MainController._text_error:
            type_txt = "ERROR"
            text_ctrl.SetDefaultStyle(wx.TextAttr(wx.RED))
        # Warning
        elif type_of_text == MainController._text_warn:
            type_txt = "WARN"
            # Orange
            text_ctrl.SetDefaultStyle(wx.TextAttr(wx.Color(255, 168, 7)))
        # Info
        else:
            text_ctrl.SetDefaultStyle(wx.TextAttr(wx.BLACK))
    
        text_ctrl.AppendText(type_txt + ": " + text + "\n")
    
    _text_info = 0 # Text has informational character
    _text_warn = 1 # Text has warning character
    _text_error = 2 # Text has error character
    
        