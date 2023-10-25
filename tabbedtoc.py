# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel
from org.gvsig.tools.swing.api import ToolsSwingLocator

from java.awt import BorderLayout

import tocutils
reload(tocutils)

import sourceorder
reload(sourceorder)
from sourceorder import setTreeAsSourceOrder

#
# http://desktop.arcgis.com/es/arcmap/10.3/map/working-with-arcmap/using-the-table-of-contents.htm
#
from addons.TabbedToC.patchs.fixformpanel import fixFormPanelResourceLoader
from org.gvsig.tools.swing.api import Component
import visibilityorder
reload(visibilityorder)
from visibilityorder import setTreeAsVisibilityOrder

import selectionorder
reload(selectionorder)
from selectionorder import setTreeAsSelectionOrder

from org.gvsig.app import ApplicationLocator
from org.gvsig.app.project.documents import DocumentManager
from org.gvsig.app.project.documents.view import ViewManager
from org.gvsig.tools.observer import Observer
from org.gvsig.tools import ToolsLocator

from gvsig import getResource
from java.io import File

class TabbedToC(FormPanel,Component):
  def __init__(self):
    fixFormPanelResourceLoader()
    i18nManager = ToolsLocator.getI18nManager()
    i18nManager.addResourceFamily("text",File(getResource(__file__,"i18n")))
  
    FormPanel.__init__(self,getResource(__file__,"tabbedtoc.xml"))
    self.tabTOC.setToolTipTextAt(0,"_List_By_Drawing_Order")
    self.tabTOC.setToolTipTextAt(1,"_List_By_Source")
    self.tabTOC.setToolTipTextAt(2,"_List_By_Visibility")
    self.tabTOC.setToolTipTextAt(3,"_List_By_Selection")

    iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
    self.tabTOC.setIconAt(0,iconTheme.get("tabbedtoc-drawingorder"))
    self.tabTOC.setIconAt(1,iconTheme.get("tabbedtoc-sourceorder"))
    self.tabTOC.setIconAt(2,iconTheme.get("tabbedtoc-visibilityorder"))
    self.tabTOC.setIconAt(3,iconTheme.get("tabbedtoc-selectionorder"))

    self.__mapContext = None
    self.setPreferredSize(300,200)
    self.translateUI()

  def getTab(self):
    return self.tabTOC
    
  def install(self, viewPanel):
    
    self.pnlDrawingOrder.setLayout(BorderLayout())
    self.pnlDrawingOrder.add(viewPanel.getTOC(),BorderLayout.CENTER)
    viewPanel.getViewInformationArea().add(self,"TOC", 0, "ToC", None, "Table of contents")
    
    self.__mapContext = viewPanel.getMapControl().getMapContext()
    # TAB Source Order
    setTreeAsSourceOrder(self.treeSourceOrder, self.__mapContext)
    # TAB Visibility 
    setTreeAsVisibilityOrder(self.treeVisibilityOrder, self.__mapContext)
    # TAB Selection
    setTreeAsSelectionOrder(self.treeSelectionOrder, self.__mapContext)

    self.treeSourceOrder.revalidate()
    self.treeSourceOrder.repaint()
    self.treeVisibilityOrder.revalidate()
    self.treeVisibilityOrder.repaint()
    self.treeSelectionOrder.revalidate()
    self.treeSelectionOrder.repaint()
    
  def translateUI(self):
    #manager = ToolsSwingLocator.getToolsSwingManager()
    from addons.TabbedToC.patchs.fixtranslatecomponent import TranslateComponent as manager

    components = [self.tabTOC]
    for component in components:
      manager.translate(component)
      
def main(*args):
    viewDoc = gvsig.currentView()
    viewPanel = viewDoc.getWindowOfView()
    panel = TabbedToC()
    panel.install(viewPanel)
