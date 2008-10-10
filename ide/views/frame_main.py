#Boa:Frame:MainFrame

# Copyright 2004-2008 Roman Yakovenko.
# 2007 Alexander Eisenhuth
# Distributed under the Boost Software License, Version 1.0. (See
# accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)


""" Contains the iplementation of the main frame of the application.
Most of the code was build with BOA"""

import wx

def create(parent):
    return MainFrame(parent)

[wxID_MAINFRAMEMENUEFILEEXIT, wxID_MAINFRAMEMENUEFILEITEMS7, 
 wxID_MAINFRAMEMENUEFILENEW, wxID_MAINFRAMEMENUEFILEOPEN, 
 wxID_MAINFRAMEMENUEFILERECENT, wxID_MAINFRAMEMENUEFILESAVE, 
] = [wx.NewId() for _init_coll_menueFile_Items in range(6)]

[wxID_MAINFRAMEMENUINCLUDESADDINC, wxID_MAINFRAMEMENUINCLUDESITEMS1, 
] = [wx.NewId() for _init_coll_menuIncludes_Items in range(2)]

[wxID_MAINFRAMEMENUMACROSADDDEF, wxID_MAINFRAMEMENUMACROSREMOVEDEF, 
] = [wx.NewId() for _init_coll_menuMacros_Items in range(2)]

[wxID_MAINFRAME, wxID_MAINFRAMEBUTGCCXML, wxID_MAINFRAMEBUTGENCPP, 
 wxID_MAINFRAMEBUTGENPYPP, wxID_MAINFRAMEBUTGENXML, wxID_MAINFRAMEBUTHEADERS, 
 wxID_MAINFRAMELISTINCLUDES, wxID_MAINFRAMELISTMACROS, wxID_MAINFRAMENBLOW, 
 wxID_MAINFRAMENBUPLEFT, wxID_MAINFRAMENBUPRIGHT, wxID_MAINFRAMEPANELBUTTONS, 
 wxID_MAINFRAMEPANELMAIN, wxID_MAINFRAMEPANELNBCODE, 
 wxID_MAINFRAMEPANELNBSETTINGS, wxID_MAINFRAMEPANELSHLOW, 
 wxID_MAINFRAMEPANELSHUP, wxID_MAINFRAMEPANELUPLEFT, 
 wxID_MAINFRAMEPANELUPRIGHT, wxID_MAINFRAMESPLITTERHORIZONTAL, 
 wxID_MAINFRAMESPLITTERVERTICAL, wxID_MAINFRAMESTATICTEXT1, 
 wxID_MAINFRAMESTATICTEXT2, wxID_MAINFRAMESTATICTEXT3, 
 wxID_MAINFRAMESTATICTEXT4, wxID_MAINFRAMESTATUSBAR, wxID_MAINFRAMETEXTCODE, 
 wxID_MAINFRAMETEXTGCCXML, wxID_MAINFRAMETEXTHEADER, wxID_MAINFRAMETEXTOUTPUT, 
] = [wx.NewId() for _init_ctrls in range(30)]

class MainFrame(wx.Frame):
    """ Main frame class. Part of MVC """

    def _init_coll_bsHeader_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=5,
              flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.textHeader, 1, border=10,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.TOP)
        parent.AddWindow(self.butHeaders, 0, border=10,
              flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_bsMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.splitterHorizontal, 1, border=5,
              flag=wx.ALL | wx.EXPAND)

    def _init_coll_bsIncPath_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText3, 0, border=5,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
        parent.AddWindow(self.listIncludes, 1, border=10,
              flag=wx.RIGHT | wx.BOTTOM | wx.TOP | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_bsULSettings_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer((10, 10), border=0, flag=0)
        parent.AddSizer(self.bsHeader, 0, border=5, flag=wx.RIGHT | wx.EXPAND)
        parent.AddSizer(self.bsGccXml, 0, border=5, flag=wx.RIGHT | wx.EXPAND)
        parent.AddSizer(self.bsIncPath, 3, border=5, flag=wx.RIGHT | wx.EXPAND)
        parent.AddSizer(self.bsMacros, 2, border=5, flag=wx.RIGHT | wx.EXPAND)

    def _init_coll_bsGccXml_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText2, 0, border=5,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
        parent.AddWindow(self.textGccXml, 1, border=10,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.BOTTOM)
        parent.AddWindow(self.butGccXml, 0, border=10,
              flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_bsMacros_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText4, 0, border=5,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
        parent.AddWindow(self.listMacros, 1, border=10,
              flag=wx.RIGHT | wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

    def _init_coll_bsUpLeft_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.nbUpLeft, 1, border=0, flag=wx.ALL | wx.EXPAND)

    def _init_coll_bsURButtons_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.butGenXml, 0, border=10,
              flag=wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.butGenCpp, 0, border=10,
              flag=wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.butGenPyPP, 0, border=10,
              flag=wx.RIGHT | wx.LEFT | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_bsMainUpper_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.splitterVertical, 1, border=5,
              flag=wx.BOTTOM | wx.EXPAND)

    def _init_coll_bsMainLow_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.nbLow, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bsUpRight_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.nbUpRight, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bsURCode_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.textCode, 1, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.panelButtons, 0, border=5,
              flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL)

    def _init_coll_menuBar_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menueFile, title=u'&File')

    def _init_coll_menuIncludes_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Add new include directory for gcc',
              id=wxID_MAINFRAMEMENUINCLUDESADDINC, kind=wx.ITEM_NORMAL,
              text=u'Add ...')
        parent.Append(help=u'Remove selected include directory',
              id=wxID_MAINFRAMEMENUINCLUDESITEMS1, kind=wx.ITEM_NORMAL,
              text=u'Remove')
        self.Bind(wx.EVT_MENU, self.OnMenueIncludesAdd,
              id=wxID_MAINFRAMEMENUINCLUDESADDINC)
        self.Bind(wx.EVT_MENU, self.OnMenueIncludesRemove,
              id=wxID_MAINFRAMEMENUINCLUDESITEMS1)

    def _init_coll_menueFile_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Create new project with default settings',
              id=wxID_MAINFRAMEMENUEFILENEW, kind=wx.ITEM_NORMAL,
              text=u'&New project')
        parent.Append(help=u'Open existing project',
              id=wxID_MAINFRAMEMENUEFILEOPEN, kind=wx.ITEM_NORMAL,
              text=u'&Open  project')
        parent.Append(help=u'Save current project',
              id=wxID_MAINFRAMEMENUEFILESAVE, kind=wx.ITEM_NORMAL,
              text=u'&Save  project')
        parent.Append(help=u'Save current project under a different filename',
              id=wxID_MAINFRAMEMENUEFILEITEMS7, kind=wx.ITEM_NORMAL,
              text=u'S&ave as ...')
        parent.AppendSeparator()
        parent.AppendMenu(help=u'Open recently used project',
              id=wxID_MAINFRAMEMENUEFILERECENT, submenu=self.menueRecentPrj,
              text=u'&Recent  projects')
        parent.AppendSeparator()
        parent.Append(help=u'Exit IDE', id=wxID_MAINFRAMEMENUEFILEEXIT,
              kind=wx.ITEM_NORMAL, text=u'&Exit')
        self.Bind(wx.EVT_MENU, self.OnMenueFileNewMenu,
              id=wxID_MAINFRAMEMENUEFILENEW)
        self.Bind(wx.EVT_MENU, self.OnMenueFileOpenMenu,
              id=wxID_MAINFRAMEMENUEFILEOPEN)
        self.Bind(wx.EVT_MENU, self.OnMenueFileSaveMenu,
              id=wxID_MAINFRAMEMENUEFILESAVE)
        self.Bind(wx.EVT_MENU, self.OnMenueFileExitMenu,
              id=wxID_MAINFRAMEMENUEFILEEXIT)
        self.Bind(wx.EVT_MENU, self.OnMenueFileSaveAsMenu,
              id=wxID_MAINFRAMEMENUEFILEITEMS7)
        self.Bind(wx.EVT_MENU, self.OnMenueFileRecentMenu,
              id=wxID_MAINFRAMEMENUEFILERECENT)

    def _init_coll_menuMacros_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=u'Add new define for gcc',
              id=wxID_MAINFRAMEMENUMACROSADDDEF, kind=wx.ITEM_NORMAL,
              text=u'Add ...')
        parent.Append(help=u'Remove selected define',
              id=wxID_MAINFRAMEMENUMACROSREMOVEDEF, kind=wx.ITEM_NORMAL,
              text=u'Remove')
        self.Bind(wx.EVT_MENU, self.OnMenueMacroAddMacro,
              id=wxID_MAINFRAMEMENUMACROSADDDEF)
        self.Bind(wx.EVT_MENU, self.OnMenueMacrosRemoveMacro,
              id=wxID_MAINFRAMEMENUMACROSREMOVEDEF)

    def _init_coll_nbLow_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.textOutput, select=True,
              text=u'Output')

    def _init_coll_nbUpRight_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.panelNbCode, select=True,
              text=u'Code')

    def _init_coll_nbUpLeft_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.panelNbSettings, select=True,
              text=u'Settings')

    def _init_coll_statusBar_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(2)

        parent.SetStatusText(number=0, text=u'')
        parent.SetStatusText(number=1, text=u'')

        parent.SetStatusWidths([-1, -1])

    def _init_sizers(self):
        # generated method, don't edit
        self.bsMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.bsMainUpper = wx.BoxSizer(orient=wx.VERTICAL)

        self.bsMainLow = wx.BoxSizer(orient=wx.VERTICAL)

        self.bsUpLeft = wx.BoxSizer(orient=wx.VERTICAL)

        self.bsULSettings = wx.BoxSizer(orient=wx.VERTICAL)

        self.bsURButtons = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bsHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bsGccXml = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bsIncPath = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bsMacros = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bsUpRight = wx.BoxSizer(orient=wx.VERTICAL)

        self.bsURCode = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_bsMain_Items(self.bsMain)
        self._init_coll_bsMainUpper_Items(self.bsMainUpper)
        self._init_coll_bsMainLow_Items(self.bsMainLow)
        self._init_coll_bsUpLeft_Items(self.bsUpLeft)
        self._init_coll_bsULSettings_Items(self.bsULSettings)
        self._init_coll_bsURButtons_Items(self.bsURButtons)
        self._init_coll_bsHeader_Items(self.bsHeader)
        self._init_coll_bsGccXml_Items(self.bsGccXml)
        self._init_coll_bsIncPath_Items(self.bsIncPath)
        self._init_coll_bsMacros_Items(self.bsMacros)
        self._init_coll_bsUpRight_Items(self.bsUpRight)
        self._init_coll_bsURCode_Items(self.bsURCode)

        self.panelSHUp.SetSizer(self.bsMainUpper)
        self.panelNbCode.SetSizer(self.bsURCode)
        self.panelUpLeft.SetSizer(self.bsUpLeft)
        self.panelButtons.SetSizer(self.bsURButtons)
        self.panelSHLow.SetSizer(self.bsMainLow)
        self.panelMain.SetSizer(self.bsMain)
        self.panelUpRight.SetSizer(self.bsUpRight)
        self.panelNbSettings.SetSizer(self.bsULSettings)

    def _init_utils(self):
        # generated method, don't edit
        self.menueFile = wx.Menu(title='')

        self.menuBar = wx.MenuBar()

        self.menuIncludes = wx.Menu(title='')

        self.menuMacros = wx.Menu(title='')

        self.menueRecentPrj = wx.Menu(title=u'')

        self._init_coll_menueFile_Items(self.menueFile)
        self._init_coll_menuBar_Menus(self.menuBar)
        self._init_coll_menuIncludes_Items(self.menuIncludes)
        self._init_coll_menuMacros_Items(self.menuMacros)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_MAINFRAME, name=u'MainFrame',
              parent=prnt, pos=wx.Point(0, 0), size=wx.Size(800, 600),
              style=wx.DEFAULT_FRAME_STYLE, title=u'Py++ IDE ()')
        self._init_utils()
        self.SetClientSize(wx.Size(792, 566))
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_CLOSE, self.OnMainFrameClose)

        self.statusBar = wx.StatusBar(id=wxID_MAINFRAMESTATUSBAR,
              name=u'statusBar', parent=self, style=0)
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

        self.panelMain = wx.Panel(id=wxID_MAINFRAMEPANELMAIN, name=u'panelMain',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(792, 523),
              style=wx.TAB_TRAVERSAL)

        self.splitterHorizontal = wx.SplitterWindow(id=wxID_MAINFRAMESPLITTERHORIZONTAL,
              name=u'splitterHorizontal', parent=self.panelMain, pos=wx.Point(5,
              5), size=wx.Size(782, 513), style=0)
        self.splitterHorizontal.SetMinimumPaneSize(40)

        self.panelSHUp = wx.Panel(id=wxID_MAINFRAMEPANELSHUP, name=u'panelSHUp',
              parent=self.splitterHorizontal, pos=wx.Point(0, 0),
              size=wx.Size(782, 290), style=wx.TAB_TRAVERSAL)

        self.panelSHLow = wx.Panel(id=wxID_MAINFRAMEPANELSHLOW,
              name=u'panelSHLow', parent=self.splitterHorizontal,
              pos=wx.Point(0, 294), size=wx.Size(782, 219),
              style=wx.TAB_TRAVERSAL)
        self.splitterHorizontal.SplitHorizontally(self.panelSHUp,
              self.panelSHLow, 300)

        self.nbLow = wx.Notebook(id=wxID_MAINFRAMENBLOW, name=u'nbLow',
              parent=self.panelSHLow, pos=wx.Point(0, 0), size=wx.Size(782,
              219), style=0)
        self.nbLow.SetLabel(u'Label')

        self.textOutput = wx.TextCtrl(id=wxID_MAINFRAMETEXTOUTPUT,
              name=u'textOutput', parent=self.nbLow, pos=wx.Point(0, 0),
              size=wx.Size(774, 193),
              style=wx.TE_RICH | wx.TE_READONLY | wx.TE_MULTILINE, value=u'')

        self.splitterVertical = wx.SplitterWindow(id=wxID_MAINFRAMESPLITTERVERTICAL,
              name=u'splitterVertical', parent=self.panelSHUp, pos=wx.Point(0,
              0), size=wx.Size(782, 285), style=wx.SP_3D)
        self.splitterVertical.SetMinimumPaneSize(40)

        self.panelUpLeft = wx.Panel(id=wxID_MAINFRAMEPANELUPLEFT,
              name=u'panelUpLeft', parent=self.splitterVertical, pos=wx.Point(0,
              0), size=wx.Size(298, 285), style=wx.TAB_TRAVERSAL)

        self.panelUpRight = wx.Panel(id=wxID_MAINFRAMEPANELUPRIGHT,
              name=u'panelUpRight', parent=self.splitterVertical,
              pos=wx.Point(302, 0), size=wx.Size(480, 285),
              style=wx.TAB_TRAVERSAL)
        self.splitterVertical.SplitVertically(self.panelUpLeft,
              self.panelUpRight, 50)

        self.nbUpLeft = wx.Notebook(id=wxID_MAINFRAMENBUPLEFT, name=u'nbUpLeft',
              parent=self.panelUpLeft, pos=wx.Point(0, 0), size=wx.Size(298,
              285), style=0)
        self.nbUpLeft.SetLabel(u'Label')
        self.nbUpLeft.SetHelpText(u'')

        self.nbUpRight = wx.Notebook(id=wxID_MAINFRAMENBUPRIGHT,
              name=u'nbUpRight', parent=self.panelUpRight, pos=wx.Point(0, 0),
              size=wx.Size(480, 285), style=0)

        self.panelNbSettings = wx.Panel(id=wxID_MAINFRAMEPANELNBSETTINGS,
              name=u'panelNbSettings', parent=self.nbUpLeft, pos=wx.Point(0, 0),
              size=wx.Size(290, 259), style=wx.TAB_TRAVERSAL)
        self.panelNbSettings.Show(True)
        self.panelNbSettings.SetMinSize(wx.Size(100, 100))

        self.panelNbCode = wx.Panel(id=wxID_MAINFRAMEPANELNBCODE,
              name=u'panelNbCode', parent=self.nbUpRight, pos=wx.Point(0, 0),
              size=wx.Size(472, 259), style=wx.TAB_TRAVERSAL)

        self.textCode = wx.TextCtrl(id=wxID_MAINFRAMETEXTCODE, name=u'textCode',
              parent=self.panelNbCode, pos=wx.Point(0, 0), size=wx.Size(472,
              225),
              style=wx.VSCROLL | wx.HSCROLL | wx.TE_READONLY | wx.TE_MULTILINE,
              value=u'')
        self.textCode.SetHelpText(u'')

        self.panelButtons = wx.Panel(id=wxID_MAINFRAMEPANELBUTTONS,
              name=u'panelButtons', parent=self.panelNbCode, pos=wx.Point(27,
              230), size=wx.Size(418, 24), style=wx.TAB_TRAVERSAL)

        self.butGenXml = wx.Button(id=wxID_MAINFRAMEBUTGENXML,
              label=u'Generate XML code', name=u'butGenXml',
              parent=self.panelButtons, pos=wx.Point(10, 0), size=wx.Size(120,
              23), style=0)
        self.butGenXml.SetToolTipString(u'')
        self.butGenXml.SetHelpText(u'Help for button')
        self.butGenXml.Bind(wx.EVT_BUTTON, self.OnButGenXmlButton,
              id=wxID_MAINFRAMEBUTGENXML)

        self.butGenCpp = wx.Button(id=wxID_MAINFRAMEBUTGENCPP,
              label=u'Generate C++ code', name=u'butGenCpp',
              parent=self.panelButtons, pos=wx.Point(150, 0), size=wx.Size(120,
              24), style=0)
        self.butGenCpp.Bind(wx.EVT_BUTTON, self.OnButGenCppButton,
              id=wxID_MAINFRAMEBUTGENCPP)

        self.butGenPyPP = wx.Button(id=wxID_MAINFRAMEBUTGENPYPP,
              label=u'Generate Py++ code', name=u'butGenPyPP',
              parent=self.panelButtons, pos=wx.Point(290, 0), size=wx.Size(118,
              23), style=0)
        self.butGenPyPP.Bind(wx.EVT_BUTTON, self.OnButGenPyPPButton,
              id=wxID_MAINFRAMEBUTGENPYPP)

        self.textHeader = wx.TextCtrl(id=wxID_MAINFRAMETEXTHEADER,
              name=u'textHeader', parent=self.panelNbSettings, pos=wx.Point(56,
              20), size=wx.Size(181, 21), style=wx.TE_READONLY, value=u'')

        self.butHeaders = wx.Button(id=wxID_MAINFRAMEBUTHEADERS, label=u'...',
              name=u'butHeaders', parent=self.panelNbSettings, pos=wx.Point(247,
              19), size=wx.Size(28, 23), style=0)
        self.butHeaders.Bind(wx.EVT_BUTTON, self.OnButHeadersButton,
              id=wxID_MAINFRAMEBUTHEADERS)

        self.textGccXml = wx.TextCtrl(id=wxID_MAINFRAMETEXTGCCXML,
              name=u'textGccXml', parent=self.panelNbSettings, pos=wx.Point(56,
              61), size=wx.Size(181, 21), style=wx.TE_READONLY, value=u'')

        self.staticText1 = wx.StaticText(id=wxID_MAINFRAMESTATICTEXT1,
              label=u'Header\nFile', name='staticText1',
              parent=self.panelNbSettings, pos=wx.Point(5, 15), size=wx.Size(51,
              30), style=wx.ALIGN_CENTRE)

        self.staticText4 = wx.StaticText(id=wxID_MAINFRAMESTATICTEXT4,
              label=u'Macros', name='staticText4', parent=self.panelNbSettings,
              pos=wx.Point(5, 212), size=wx.Size(51, 25),
              style=wx.ALIGN_CENTRE)

        self.staticText2 = wx.StaticText(id=wxID_MAINFRAMESTATICTEXT2,
              label=u'GccXml', name='staticText2', parent=self.panelNbSettings,
              pos=wx.Point(5, 60), size=wx.Size(51, 23), style=wx.ALIGN_CENTRE)

        self.butGccXml = wx.Button(id=wxID_MAINFRAMEBUTGCCXML, label=u'...',
              name=u'butGccXml', parent=self.panelNbSettings, pos=wx.Point(247,
              60), size=wx.Size(28, 23), style=0)
        self.butGccXml.Bind(wx.EVT_BUTTON, self.OnButGccXmlButton,
              id=wxID_MAINFRAMEBUTGCCXML)

        self.staticText3 = wx.StaticText(id=wxID_MAINFRAMESTATICTEXT3,
              label=u'Include\nPath', name='staticText3',
              parent=self.panelNbSettings, pos=wx.Point(5, 123),
              size=wx.Size(51, 37), style=wx.ALIGN_CENTRE)

        self.listIncludes = wx.ListCtrl(id=wxID_MAINFRAMELISTINCLUDES,
              name=u'listIncludes', parent=self.panelNbSettings,
              pos=wx.Point(56, 102), size=wx.Size(219, 80),
              style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT)
        self.listIncludes.Bind(wx.EVT_RIGHT_DOWN, self.OnListIncludesRightDown)
        self.listIncludes.Bind(wx.EVT_SIZE, self.OnListIncludesSize)
        self.listIncludes.Bind(wx.EVT_LEFT_DCLICK,
              self.OnListIncludesLeftDclick)
        self.listIncludes.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnListIncludesListItemSelected,
              id=wxID_MAINFRAMELISTINCLUDES)
        self.listIncludes.Bind(wx.EVT_LIST_ITEM_DESELECTED,
              self.OnListIncludesListItemDeselected,
              id=wxID_MAINFRAMELISTINCLUDES)

        self.listMacros = wx.ListCtrl(id=wxID_MAINFRAMELISTMACROS,
              name=u'listMacros', parent=self.panelNbSettings, pos=wx.Point(56,
              202), size=wx.Size(219, 46),
              style=wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_REPORT)
        self.listMacros.Bind(wx.EVT_RIGHT_DOWN, self.OnListMacrosRightDown)
        self.listMacros.Bind(wx.EVT_SIZE, self.OnListMacrosSize)
        self.listMacros.Bind(wx.EVT_LEFT_DCLICK, self.OnListMacrosLeftDclick)
        self.listMacros.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnListMacrosListItemSelected, id=wxID_MAINFRAMELISTMACROS)
        self.listMacros.Bind(wx.EVT_LIST_ITEM_DESELECTED,
              self.OnListMacrosListItemDeselected, id=wxID_MAINFRAMELISTMACROS)

        self._init_coll_nbLow_Pages(self.nbLow)
        self._init_coll_nbUpLeft_Pages(self.nbUpLeft)
        self._init_coll_nbUpRight_Pages(self.nbUpRight)

        self._init_sizers()

    def __init__(self, parent):
                
        self.currentItemInclude = None
        self.currentItemMacro = None
        
        self._init_ctrls(parent)
        self._setup_ide_ctrls()        
        
    def OnMenueFileNewMenu(self, event):
        self._controller.DoProjectNew()
        event.Skip()

    def OnMenueFileOpenMenu(self, event):
        self._controller.OpenDlgLoadProject()
        event.Skip()

    def OnMenueFileSaveMenu(self, event):
        self._controller.OpenDlgSaveProject()
        event.Skip()
        
    def OnMenueFileSaveAsMenu(self, event):
        self._controller.OpenDlgSaveProject(new_file=True)
        event.Skip()        

    def OnMenueFileRecentMenu(self, event):
        event.Skip()

    def OnMenueFileExitMenu(self, event):
        self._controller.ExitIde()
        event.Skip()

    def OnTextGenCodeRightDown(self, event):
        event.Skip()

    def OnListIncludesRightDown(self, event):
        self.PopupMenu(self.menuIncludes)

    def OnListMacrosRightDown(self, event):
        self.PopupMenu(self.menuMacros)

    def OnButGenXmlButton(self, event):
        self._controller.GenXmlCode()

    def OnButGenCppButton(self, event):
        self._controller.GenCppCode()

    def OnButGenPyPPButton(self, event):
        self._controller.GenPyPPCode()

    def OnButHeadersButton(self, event):
        """Callback for button event"""
        self._controller.OpenDlgHeader()
        event.Skip()

    def OnButGccXmlButton(self, event):
        """Callback for button event"""
        self._controller.OpenDlgGccXml()
        event.Skip()
        
    def set_controller(self, controller):
        """Set controller of MVC"""
        self._controller = controller
        
    def _setup_ide_ctrls(self):
        """Do ide related settings in ctrls"""
        list_inc = self.listIncludes
        list_def = self.listMacros
        
        # Init list controls
        for list_ctrl in (list_inc, list_def):
            list_ctrl.InsertColumn(0, "Path")

    def OnListIncludesSize(self, event):
        """Handle resize of listIncludes"""
        list_ctrl = self.listIncludes
        list_ctrl.SetColumnWidth(0, list_ctrl.GetSize().GetWidth() - 30 )
        event.Skip()

    def OnListMacrosSize(self, event):
        """Handle resize of listMacros"""
        list_ctrl = self.listMacros
        list_ctrl.SetColumnWidth(0, list_ctrl.GetSize().GetWidth() - 30 )
        event.Skip()

    def OnMenueIncludesAdd(self, event):
        self._controller.OpenDlgAddInclude()
        event.Skip()

    def OnMenueIncludesRemove(self, event):
        self._controller.DoRemoveCurInclude()
        event.Skip()

    def OnMenueMacroAddMacro(self, event):
        self._controller.OpenDlgAddMacro()
        event.Skip()
        
    def OnMenueMacrosRemoveMacro(self, event):
        self._controller.DoRemoveCurMacro()
        event.Skip()

    def OnListIncludesLeftDclick(self, event):
        self._controller.OpenDlgEditCurInclude()
        event.Skip()

    def OnListMacrosLeftDclick(self, event):
        self._controller.OpenDlgEditCurMacro()
        event.Skip()

    def OnListIncludesListItemSelected(self, event):
        self.currentItemInclude = event.m_itemIndex
        event.Skip()

    def OnListMacrosListItemSelected(self, event):
        self.currentItemMacro = event.m_itemIndex
        event.Skip()

    def OnListIncludesListItemDeselected(self, event):
        self.currentItemInclude = None        
        event.Skip()

    def OnListMacrosListItemDeselected(self, event):
        self.currentItemMacro = None
        event.Skip()

    def OnMenueRecentPrjItems0Menu(self, event):
        print "OnMenueRecentPrjItems0Menu"
        event.Skip()

    def OnMainFrameClose(self, event):
        if not self._controller.ExitIde():
            return() # Don't close
        else:
            event.Skip()


        
        
        
    
