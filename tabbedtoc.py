# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import FormPanel

from java.awt import BorderLayout

import sourceorder
reload(sourceorder)

from sourceorder import setTreeAsSourceOrder
from org.gvsig.fmap.mapcontext.events.listeners import ViewPortListener

#
# http://desktop.arcgis.com/es/arcmap/10.3/map/working-with-arcmap/using-the-table-of-contents.htm
#

from org.gvsig.tools.swing.api import Component

from visibilityorder import setTreeAsVisibilityOrder

class TabbedToC(FormPanel,Component,ViewPortListener):
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
    
  def install(self):
    viewDoc = gvsig.currentView()
    viewPanel = viewDoc.getWindowOfView()
    self.pnlDrawingOrder.setLayout(BorderLayout())
    self.pnlDrawingOrder.add(viewPanel.getTOC(),BorderLayout.CENTER)
    viewPanel.getViewInformationArea().add(self,"TOC", 0, "ToC", None, "Table of contents")
    
    self.__mapContext = viewDoc.getMapContext()
    # TAB Source Order
    setTreeAsSourceOrder(self.treeSourceOrder, self.__mapContext)
    # TAB Visibility 
    setTreeAsVisibilityOrder(self.treeVisibilityOrder, self.__mapContext)
    # TAB Selection
    
    # Agregamos listener al ViewPort
    self.__mapContext.getViewPort().addViewPortListener(self)

    
  # Metodo obligatorio de ViewPortListener
  def backColorChanged(self,*args):
      pass

  # Metodo obligatorio de ViewPortListener
  def extentChanged(self,*args):
      setTreeAsVisibilityOrder(self.treeVisibilityOrder, self.__mapContext)

  # Metodo obligatorio de ViewPortListener
  def projectionChanged(self,*args):
      pass
            
def main(*args):
    panel = TabbedToC()
    panel.install()
    #panel.showWindow("ToC")
