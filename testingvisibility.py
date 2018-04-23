# encoding: utf-8

import gvsig

# TODO soport para el viewportlistener
# http://downloads.gvsig.org/download/web/es/build/html/scripting_devel_guide/2.3/capturando_eventos.html


from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel
import os
from org.gvsig.app.project.documents.view.toc import TocItemBranch

from java.awt import Color
from java.awt import FlowLayout
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing.tree import TreeCellRenderer

from javax.swing import JCheckBox

from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from java.awt import Font

from java.awt.font import TextAttribute

def setTreeAsVisibilityOrder(tree, mapContext):
  ## tree as component
  model = createTreeModel(mapContext)
  tree.setModel(model)
  tree.setCellRenderer(VisibilityCellRenderer())
  expandAllNodes(tree, 0, tree.getRowCount())

def expandAllNodes(tree, startingIndex, rowCount):
    for i in xrange(startingIndex,rowCount): 
        tree.expandRow(i)

    if tree.getRowCount()!=rowCount:
        expandAllNodes(tree, rowCount, tree.getRowCount())
        
def addLegend(nodeLayer, lyr):
    width = 300

mapContextManager = None
iconTheme = None

def getIconFromLayer(layer):
  global mapContextManager
  global iconTheme

  providerName = layer.getDataStore().getProviderName()
  if providerName != None:
    if mapContextManager == None:
      mapContextManager = MapContextLocator.getMapContextManager()
    iconName = mapContextManager.getIconLayer(providerName)
    if iconTheme == None:
      iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
    icon = iconTheme.get(iconName)
    return icon
  return None
  
class VisibilityCellRenderer(TreeCellRenderer):
    def __init__(self):
        self.lblGroup = JLabel()
        self.lblGroup.setBackground(Color.LIGHT_GRAY)
        self.lblGroup.setOpaque(True)
        self.pnlLayer = JPanel()
        self.pnlLayer.setOpaque(False)
        self.pnlLayer.setLayout(FlowLayout(FlowLayout.LEFT))
        self.chkLayerVisibility = JCheckBox()
        self.pnlLayer.add(self.chkLayerVisibility)
        self.lblLayerName = JLabel()
        self.lblLayerIcon = JLabel()
        self.pnlLayer.add(self.lblLayerIcon)
        self.pnlLayer.add(self.lblLayerName)
        self.lblUnknown = JLabel()

        
    def getTreeCellRendererComponent(self, tree, value, selected, expanded, leaf, row, hasFocus):
        uo = value.getUserObject()
        if isinstance(uo, DataGroup):
            self.lblGroup.setText(uo.getName())
            return self.lblGroup
        if isinstance(uo, DataLayer):
            self.lblLayerName.setText(uo.getName())
            self.lblLayerIcon.setIcon(getIconFromLayer(uo.getLayer()))
            self.chkLayerVisibility.setSelected(uo.getLayer().isVisible())
            if selected:
                font = self.lblLayerName.getFont()
                #font = font.deriveFont(TextAttribute.WEIGHT,font.getSize2D())
                
                self.lblLayerName.setForeground(Color.BLUE)
            else:
                font = self.lblLayerName.getFont()
                font = font.deriveFont(Font.PLAIN,font.getSize2D())
                self.lblLayerName.setForeground(Color.BLACK)
            #self.lblLayerName.setFont(font)
            return self.pnlLayer
        self.lblUnknown.setText("None")
        return self.lblUnknown
        
        
        
        
def createTreeModel(mapContext, reducedTree=True):
    root = DefaultMutableTreeNode("Visibility")
    
    rootWithVisibility = DefaultMutableTreeNode(DataGroup("Layers with Visibility"))
    rootWithoutVisibility = DefaultMutableTreeNode(DataGroup("Layers without Visibility"))
    rootNotVisibility = DefaultMutableTreeNode(DataGroup("Layers desactivated"))
    
    root.insert(rootWithVisibility, root.getChildCount())
    root.insert(rootWithoutVisibility, root.getChildCount())
    root.insert(rootNotVisibility, root.getChildCount())
    
    #yesVis = list()
    #outVis = list()
    #notVis = list()
    for layer in iter(mapContext.deepiterator()):
        if layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            #yesVis.append(layer)
            # TODO: DOINGGGGGGGGGGGGGG
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithVisibility.insert(newNode, rootWithVisibility.getChildCount())
            addLegend(newNode, layer)
            
        elif not layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            #outVis.append(layer)
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithoutVisibility.insert(newNode, rootWithoutVisibility.getChildCount())
        elif layer.isVisible()==False:
            #notVis.append(layer)
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootNotVisibility.insert(newNode,rootNotVisibility.getChildCount())
            
    model = DefaultTreeModel(root)
    return model

class DataFolder(object):
  def __init__(self,name, path, icon=None):
    self.__name = name
    self.__path = path
    self.__icon = icon
  
  def getName(self):
    return self.__name

  def __str__(self):
    return self.__name
  toString = __str__
  __repr__ = __str__

  def isLeaf(self):
    return False

class DataGroup(DataFolder):
    def __init__(self, name):
        DataFolder.__init__(self, name, None)
        
class DataLayer(object):
  def __init__(self,path,layer):
    self.__path = path
    self.__layer = layer
    self.__label = os.path.basename(self.__path)
  def getName(self):
    return self.__label
  def getLayer(self):
      return self.__layer
  
  toString = getName
  __str__ = getName
  __repr__ = getName

  def isLeaf(self):
    return True
    
def main(*args):

    layer = gvsig.currentLayer()
    print layer.getMinScale()
    print layer.getMaxScale()
    print layer.isVisible()
    mapcontext = gvsig.currentView().getMapContext()
    print layer.isWithinScale(mapcontext.getScaleView())
    
    
