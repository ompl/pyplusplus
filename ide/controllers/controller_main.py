# -*- coding: utf-8 -*-
# Copyright 2004 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)
from threading import Timer
from Queue import Queue, Empty
import os
import wx
from views import dialog_macro
from model.settings import ProjectSettings, IdeSettings, ParameterContainer
import model.code_generator as code_generator

class MainParameter(object):
    '''
    Abstract main parameters
    '''
    def __init__(self):
        
        object.__init__(self)
        
        # Following attributes are parameters of the ide (realized as properties)
        self.max_num_recent_projects = ParameterContainer(int, 0)
        self.recent_prj_list = ParameterContainer(list, [])
        self.last_prj_path = ParameterContainer(unicode, "")
        self.last_inc_path = ParameterContainer(unicode, "")

class AsyncExecHandler(wx.EvtHandler):
    '''
    This class handles async execution. It exec the callable given in the 
    constructor. There are some callbacs for misc. issues
    '''

    def __init__(self, async_callable, args):
        wx.EvtHandler.__init__(self)        
        self._async_callable = async_callable
        self._args = args
        self._cur_timer_calls = 0
        self._ui_eventhanler = None
        self._timer_res = 100 # 100 msec
    
    def GetRunning(self):
        '''
        Return boolean if async execution is running
        '''
        return not self._thread.finished.isSet()
    
    def Start(self):
        '''
        Start async execution
        '''
        self._start_in_thread()
    
    def SetErrorOutput(self, err_cb):
        '''
        Set callback for error output
        @param err_cb: callback
        '''
        self._err_cb = err_cb
        
    def SetResultOutput(self, result_cb):
        '''
        Set callback for result
        @param result_cb: callback
        '''
        self._result_cb = result_cb
    
    def SetProgressCb(self, progress_cb, progress_tm_100msec):
        '''
        Set callback for progress. Param progress_tm_100msec defines the time
        to call the callback while async execution is running
        @param progress_cb: callback
        @param progress_tm_100msec: time in 100 msec
        '''
        assert(isinstance(progress_tm_100msec, int))
        self._progress_cb = progress_cb
        self._num_timer_calls = progress_tm_100msec
        
    def SetFinishedCb(self, finished_cb):
        '''
        Set callback, when async execution has finished
        @param finished_cb: callback
        '''
        self.finished_cb = finished_cb
    
    def _notify(self, event):
        # Read from result queue and error queue
        for que_obj, cb_obj in zip( \
                   [self._q_err, self._q_result], 
                   [self._err_cb, self._result_cb]):
            
            try:
                txt_element = que_obj.get(False)
                cb_obj(txt_element)
            except Empty:
                pass
                
        if self._thread.finished.isSet():
            self._wxtimer.Stop()
            self.finished_cb()
        else:
            pass    
                
        self._cur_timer_calls += 1
        
        # self._num_timer_calls is set in SetProgressCb
        if self._cur_timer_calls % self._num_timer_calls == 0:
            self._progress_cb()
            
        event.Skip()
        
    def _start_in_thread(self):
        # Start python thread and wx timer
        self._q_result = Queue()
        self._q_err = Queue()
        
        self._thread = Timer(0, self._async_callable, [self._args, 
                             self._q_result,  self._q_err])
        self._thread.start()
        
        self._wxtimer = wx.Timer(self)
        self._wxtimer.SetOwner(self)
        self.Bind(wx.EVT_TIMER, self._notify)
        self._wxtimer.Start(self._timer_res)

    
class MainController:
    """ Contoller class. Part of MVC
    Responsibility: Glue view and model code:
    - Handle all events from view (p.e. button) 
    """
    def __init__(self, view):
        self._view = view
        
        # Give controller object to the view
        self._view.set_controller(self)
        
        # Template file for new project
        self._prjTemplateFile = "./ProjectTemplate.xml"
        
        # Tag to appera in title of main window
        self._changedTag = " [changed]"
        
        # Dict with id's of recent projects
        self._recentPrjDict = {}
        
        # Parameters 
        self.param = MainParameter()
        
        # To access prj settings (settings are related to view)
        self._prj_settings = ProjectSettings(self._view, None)
        
        # To access ide settings (settings are related to MainParameter)
        self._ide_settings = IdeSettings(None, self.param)
        
        # To count code generation durance
        self._tm_code_gen = 0
        
        # Object to control async execution
        self._async_runner = None

        self._setup_ide_settings()
   
    def ExitIde(self):
        '''
        Exit IDE. Exit can be canceled.
        @return: False if exit is canceled else True
        '''
        if not self._check_and_save_project():
            return False
        
        if self._async_runner != None:
            if self._async_runner.GetRunning():
                self.OutputWarning("Cannot exit. "\
                                   "Ide is doing async execution ...")
                return False
        
        new_list = []
        
        # build list with max max_num_recent_projects elements
        last_idxs = self._recentPrjDict.keys()
        last_idxs.reverse() # Last added should be saved
        for idx in last_idxs:
            new_list.append(self._recentPrjDict[idx])
            if len(new_list) >= self.param.max_num_recent_projects.get():
                break
            
        self.param.recent_prj_list.set(new_list)
            
        self._ide_settings.save()
        
        self._view.Destroy()
        
        return True
        
    def OnRecentPrjLoad(self, event):
        '''
        Callback from the file menue. (Recent projects)
        @param event: wx event.
        '''
        project_file_name = self._recentPrjDict[event.GetId()]
        self._load_project(project_file_name)
        
    def DoRemoveCurInclude(self):
        '''
        Remove current selected Include item
        '''
        
        cur_num = self._view.currentItemInclude
        if None == cur_num:
            return
        self._view.listIncludes.DeleteItem(cur_num)
        self._set_settings_changed()
        
    def DoRemoveCurMacro(self):
        '''
        Remove current selected Macro item
        '''
        
        cur_num = self._view.currentItemMacro
        if None == cur_num:
            return
        self._view.listMacros.DeleteItem(cur_num)
        self._set_settings_changed()
                
    
    def CountCodeGenSec(self, reset=False):
        '''
        Count the time of code generation. Must be called once per second. 
        Update UI
        @param reset: Boolean to reset the counter
        '''
        if reset:
            self._tm_code_gen = 0
        else:
            self._tm_code_gen += 1
        self._view.statusBar.SetStatusText(number=1, text=u'Time: %d sec' % \
                                           self._tm_code_gen)
        
    def OutputError(self, err_txt):
        '''
        Print error text in output window
        @param err_txt: Text to display
        '''
        self._append_out_text(err_txt, self._text_error)
        
    def OutputWarning(self, err_txt):
        '''
        Print warning text in output window
        @param err_txt: Text to display        
        '''
        self._append_out_text(err_txt, self._text_warn)

    def OutputInfo(self, inf_txt):
        '''
        Print info text in output window
        @param inf_txt:
        '''
        self._append_out_text(inf_txt, self._text_info)
        
    def OutputCode(self, code_txt):
        '''
        Append text in the code window
        @param code_txt: Text to append
        '''
        self._view.textCode.AppendText(code_txt)
        
    def GenCodeFinished(self):
        '''
        Inform that code generation has finished
        '''
        self._enable_generation_widgets(True)
        
        
    def GenCppCode(self):
        '''
        Generate Boost.Python code
        '''
        self._enable_generation_widgets(False)
        self._view.textCode.SetValue("")
        self._append_out_text("Generation of C++ code for Boost.Python started")
        self.CountCodeGenSec(reset=True)
        
        params = self._get_gccxml_params(False)

        gen_xml_obj = AsyncExecHandler(code_generator.gen_cpp, params)
        self._start_async_exec(gen_xml_obj)        
        
    def GenPyPPCode(self):
        '''
        Generate Py++ code
        '''
        self._enable_generation_widgets(False)
        self._view.textCode.SetValue("")
        self._append_out_text("Generation of Py++ code started")
        self.CountCodeGenSec(reset=True)
        
        params = self._get_gccxml_params(False)

        gen_xml_obj = AsyncExecHandler(code_generator.gen_pypp, params)
        self._start_async_exec(gen_xml_obj)
        
    def GenXmlCode(self):
        '''
        Generate XML code
        '''
        self._enable_generation_widgets(False)
        self._append_out_text("Generation of XML code started")
        self._view.textCode.SetValue("")
        self.CountCodeGenSec(reset=True)
        
        params = self._get_gccxml_params(False)

        gen_xml_obj = AsyncExecHandler(code_generator.gen_xml, params)
        self._start_async_exec(gen_xml_obj)        
        
    def OpenDlgHeader(self):
        '''
        Open dialog to get header file
        '''
        self._open_file_dlg_text_ctrl( self._view.textHeader, 
                                           "Choose a Header file",
                                           "Header (*.h)|*.h|All Files(*)|*")
                        
    def OpenDlgGccXml(self):
        '''
        Open dialog to get GccXml executable
        '''
        
        self._open_file_dlg_text_ctrl( self._view.textGccXml, 
                                           "Choose GccXml executable",
                                           "All Files(*)|*")
    
    def OpenDlgEditCurInclude(self):
        '''
        Open dialog to edit current include
        '''
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
                self._set_settings_changed()
        finally:
            dialog.Destroy()
    
    def OpenDlgEditCurMacro(self):
        '''
        Open dialog to edit current macro
        '''
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
                self._set_settings_changed()
        finally:
            dialog.Destroy()
        
    def OpenDlgAddInclude(self):
        '''
        Open Dialog to add a include path
        '''
        dialog = wx.DirDialog(self._view, "Choose include directory", 
                              self.param.last_inc_path.get())
        try:
            if dialog.ShowModal() == wx.ID_OK:
                
                cur_num = self._view.listIncludes.GetItemCount()
                dir_path = dialog.GetPath()
                
                # Check weather path is already in list
                if not self._check_item_in_list(dir_path, 
                                               self._view.listIncludes):
                    
                    self._view.listIncludes.InsertStringItem(
                                     cur_num, dir_path)
                    self.param.last_inc_path.set(str(dir_path))
                    self._set_settings_changed()
        finally:
            dialog.Destroy()
            
    def OpenDlgAddMacro(self):
        '''
        Open dialog to add a macro
        '''
        dialog = dialog_macro.MacroDialog(self._view)
        
        if dialog.ShowModal() == wx.OK:
            
            cur_num = self._view.listMacros.GetItemCount()
            new_macro = dialog.textMacro.GetLineText(0)

            # Check weather macro is already in list
            if not self._check_item_in_list(new_macro, self._view.listMacros):      
               self._view.listMacros.InsertStringItem(cur_num, new_macro)
               self._set_settings_changed()

    def OpenDlgLoadProject(self):
        '''
        Open dialog to load a project
        '''
        from xml.parsers.expat import ExpatError
                        
        dialog = wx.FileDialog(self._view, "Load existing Py++ project", 
            self.param.last_prj_path.get(), 
            "", "Project files (*.xml)|*.xml|All Files(*)|*", wx.OPEN)
        
        try:
            if dialog.ShowModal() == wx.ID_OK:
                self.ClearUi()
                project_file_name = dialog.GetPath()
                self._load_project(project_file_name)
                
        except ExpatError:
            self._append_out_text("XML parser error in file:%s" % \
                        dialog.GetPath(), self._text_error)
            
        except Exception:
            self._append_out_text("Error loading file:%s" % \
                        dialog.GetPath(), self._text_error) 
            raise           
            
        finally:
            dialog.Destroy()        
       
    def OpenDlgSaveProject(self, new_file=False):
        '''
        Open dialog to save a project
        @param new_file: Boolean weather to use a new file
        @return: False if project save was canceled
        '''        
        # Is current file prj template?
        if self._prj_settings.get_file_name() == self._prjTemplateFile:
            project_file_name = self._open_new_prj_file()
        else:
            if new_file:
                project_file_name = self._open_new_prj_file()
            else:
                project_file_name = self._prj_settings.get_file_name()
        
        try:
            if project_file_name == None:
                return False # prior dialog skipped
            
            if not self._save_project(project_file_name):
                return False

        except Exception:
            self._append_out_text("Error saving file:%s" % \
                        project_file_name, self._text_error)
            raise
        
        return True
                
    def DoProjectNew(self):
       '''
       Open dialog for new Project
       '''
       self._load_project(self._prjTemplateFile)
       
    def ClearUi(self):
       '''
       Clear all controls of UI
       '''
       
       # Clear text ctrls
       for textCtrl in [self._view.textHeader, self._view.textGccXml, 
                        self._view.textOutput, self._view.textCode]:
           textCtrl.Clear()
       
       # clear list ctrls
       for listCtrl in [self._view.listMacros, self._view.listIncludes]:
           tot_num = listCtrl.GetItemCount()
           for cur_num in range(tot_num, 0, -1):
               listCtrl.DeleteItem(cur_num-1)
    def _cancel_if_file_exist(self, project_file_name, parent_dlg=None):
        # check for overwriting of file
        if os.path.exists(project_file_name):
            dialog = wx.MessageDialog(parent_dlg,
                "%s exists. Should it be overwritten?" % \
                (project_file_name), pos=self._view.GetPosition())
            
            if dialog.ShowModal() == wx.ID_CANCEL:
                return True
            else:
                return False

    # Return True if successfull    
    def _check_and_save_project(self):
        if self._prj_settings.get_changed():
            
            # Anyhow pos is working
            dialog = wx.MessageDialog(self._view, "Current project changed. "\
              "Should project be saved?", style = (wx.YES_NO),
              pos=self._view.GetPosition())
            
            user_input = dialog.ShowModal()
            dialog.Destroy()
            
            if user_input == wx.ID_NO:    
                return True
            elif user_input == wx.ID_YES:
                return self.OpenDlgSaveProject()
        else:
            return True

    def _load_project(self, project_file_name):
        self._check_and_save_project()
        self.ClearUi()
        self._prj_settings.load(project_file_name)
        self._set_prj_filename_in_title(project_file_name)
        
        if project_file_name != self._prjTemplateFile:
            self.param.last_prj_path.set(unicode(os.path.dirname(project_file_name)))
            
        self._add_to_prj_history(project_file_name)        
        
    def _save_project(self, project_file_name):
                
        self._prj_settings.save(project_file_name)
        self._reset_settings_changed()
        self.param.last_prj_path.set(os.path.dirname(project_file_name))
        self._set_prj_filename_in_title(project_file_name)
        self._add_to_prj_history(project_file_name)
        
        return True
        
        
    def _open_new_prj_file(self):
        
        project_file_name = None
        
        dialog = wx.FileDialog(self._view, 
           "Save Py++ project to new file",  self.param.last_prj_path.get(), "", 
           "Project files (*.xml)|*.xml|All Files(*)|*", wx.FD_SAVE)
       
        if dialog.ShowModal() == wx.ID_OK:
                
            project_file_name = dialog.GetPath()
                
            if self._cancel_if_file_exist(project_file_name, dialog):
                project_file_name = None
                
            dialog.Destroy()
        
        return project_file_name
    
    def _add_to_prj_history(self, prj_filename):
        
# This don't work, see below
#        max_num_history = self.param.max_num_recent_projects.get()
        

        if prj_filename in self._recentPrjDict.values():
            return
        
        if prj_filename == self._prjTemplateFile:
            return
        
        file_name = os.path.split(prj_filename)[1]
        
        menue = self._view.menueRecentPrj
        new_item_id = id=wx.NewId()
        new_item = wx.MenuItem(menue, help=prj_filename, 
                               id=new_item_id, 
                               kind=wx.ITEM_NORMAL, text=file_name)
        
        menue.PrependItem(new_item)
        
        self._view.Bind(wx.EVT_MENU, self.OnRecentPrjLoad,
              id=new_item_id)
    
        self._recentPrjDict[new_item_id] = prj_filename
        
# Doesn't work. Dont know why       
#        if menue.GetMenuItemCount() > max_num_history:
#            menue.Remove(max_num_history)
       
    def _open_file_dlg_text_ctrl(self, 
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
                self._set_settings_changed()
        finally:
            dialog.Destroy()
            
    def _set_settings_changed(self):
        self._prj_settings.set_changed()
        title_str = self._view.GetTitle()
        if not self._changedTag in title_str:
            title_str += self._changedTag
            self._view.SetTitle(title_str)

    def _enable_generation_widgets(self, state):
        ctrls = [self._view.butGenCpp, self._view.butGenXml, \
                 self._view.butGenPyPP]
        
        for ctrl in ctrls:
            ctrl.Enable(state)
        
    def _get_gccxml_params(self, verbose):
        
        gcc_xml = self._prj_settings.get_param('gccXmlSettings.gccXmlPath')
        inc_path_list = eval(self._prj_settings.get_param(
                'gccXmlSettings.includePathList'))
        macro_list = eval(self._prj_settings.get_param(
           'gccXmlSettings.macroList'))
        
        if verbose:
            self._append_out_text(" "+ gcc_xml)
            self._append_out_text(" "+ str(inc_path_list))
            self._append_out_text(" "+ str(macro_list))
            
        
        return (gcc_xml, inc_path_list, macro_list)
                
    def _setup_ide_settings(self):
        
        # load ide settings
        self._ide_settings.load()
        prj_list = self.param.recent_prj_list.get()
        prj_list.reverse()
        for prj in prj_list:
            self._add_to_prj_history(prj)
        
    def _set_prj_filename_in_title(self, filename):
        
        if filename == self._prjTemplateFile:
            filename = "New project"
            
        title_str = self._view.GetTitle()
        start_idx = title_str.find("(")
        end_idx = title_str.find(")")
        fnamstr = title_str[start_idx:end_idx+1]
        title_str = title_str.replace(fnamstr, "(" + filename + ")")
        self._view.SetTitle(title_str)
        
    def _reset_settings_changed(self):
        title_str = self._view.GetTitle()
        title_str = title_str.replace(self._changedTag, "")
        self._view.SetTitle(title_str)
            
    def _check_item_in_list(self, item, wx_list):
        idx = wx_list.FindItem(0, item)
        if idx == -1:
            return False
        else:
            return True
    
        
    def _append_out_text(self, text, type_of_text = 0):
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
    # Start async execution
    def _start_async_exec(self, async_runner):
        self._async_runner = async_runner
        self._async_runner.SetErrorOutput(self.OutputError)
        self._async_runner.SetResultOutput(self.OutputCode)
        self._async_runner.SetFinishedCb(self.GenCodeFinished)
        self._async_runner.SetProgressCb(self.CountCodeGenSec, 10)
        self._async_runner.Start()
    
    # levels
    _text_info = 0 # Text has informational character
    _text_warn = 1 # Text has warning character
    _text_error = 2 # Text has error character
    
        