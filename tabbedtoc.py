# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from java.awt import BorderLayout

import sourceorder
reload(sourceorder)
from sourceorder import setTreeAsSourceOrder

#
# http://desktop.arcgis.com/es/arcmap/10.3/map/working-with-arcmap/using-the-table-of-contents.htm
#

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

class TabbedToC(FormPanel,Component):
  def __init__(self):
    FormPanel.__init__(self,getResource(__file__,"tabbedtoc.xml"))
    self.tabTOC.setToolTipTextAt(0,"Lista por orden de dibujo")
    self.tabTOC.setToolTipTextAt(1,"Lista por fuente")
    self.tabTOC.setToolTipTextAt(2,"Lista por visibilidad")
    self.tabTOC.setToolTipTextAt(3,unicode("Lista por selección","utf-8"))
    self.__mapContext = None
    self.setPreferredSize(300,200)

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
            
def main(*args):
    viewDoc = gvsig.currentView()
    viewPanel = viewDoc.getWindowOfView()
    panel = TabbedToC()
    panel.install(viewPanel)
