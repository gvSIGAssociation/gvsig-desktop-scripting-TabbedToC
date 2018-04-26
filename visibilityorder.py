
# encoding: utf-8

import gvsig

# TODO soport para el viewportlistener
# http://downloads.gvsig.org/download/web/es/build/html/scripting_devel_guide/2.3/capturando_eventos.html

import os
from org.gvsig.app.project.documents.view.toc import TocItemBranch

from java.awt import Font
from java.awt.font import TextAttribute
from java.awt import Dimension
from java.awt.event import MouseAdapter
from java.awt import Color
from java.awt import FlowLayout
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing.tree import TreeCellRenderer
from javax.swing import JCheckBox
from javax.swing.border import EmptyBorder
from javax.swing import JTree
from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel

from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator


from org.gvsig.fmap.mapcontext.events.listeners import ViewPortListener
from javax.swing import SwingUtilities
from org.gvsig.app.project.documents.view import IContextMenuActionWithIcon

from javax.swing import JPopupMenu
from java.awt.event import ActionListener
from javax.swing import JMenuItem

from org.gvsig.app.project.documents.view.toc import TocItemLeaf
from org.gvsig.tools import ToolsLocator

from javax.swing.tree import TreePath

from org.gvsig.fmap.dal.feature.impl import DefaultFeatureStore
from org.gvsig.fmap.mapcontext.layers import LayerListener

from tocutils import createToCContextMenu

from tocutils import addUpdateToCListener

from javax.swing import BorderFactory

from tocutils import expandAllNodes
from tocutils import getIconFromLayer

from javax.swing.border import EtchedBorder

def setTreeAsVisibilityOrder(tree, mapContext):
  updateAll(tree,mapContext)  
  tree.setCellRenderer(VisibilityCellRenderer(tree, mapContext))
  tree.addMouseListener(VisibilityMouseAdapter(tree,mapContext))
  vportlistener = VisibilityViewPortListener(tree, mapContext)
  mapContext.getViewPort().addViewPortListener(vportlistener)
  addUpdateToCListener("VisibilityOrder", mapContext, UpdateListener(tree,mapContext))
  

def updateAll(tree,mapContext):
    #print ">>> updateAll Visibility"
    model = createTreeModel(mapContext)
    tree.setModel(model)
    tree.getModel().reload()
    expandAllNodes(tree, 0, tree.getRowCount())

class UpdateListener():
  def __init__(self, tree, mapContext):
    self.mapContext = mapContext
    self.tree = tree

  def __call__(self):
    updateAll(self.tree, self.mapContext)
        
class VisibilityViewPortListener(ViewPortListener):
  def __init__(self, tree,mapContext):
      self.mapContext = mapContext
      self.tree = tree
  # Metodo obligatorio de ViewPortListener
  def backColorChanged(self,*args):
      pass

  # Metodo obligatorio de ViewPortListener
  def extentChanged(self,*args):
    updateAll(self.tree,self.mapContext)

  # Metodo obligatorio de ViewPortListener
  def projectionChanged(self,*args):
      pass
      

class VisibilityMouseAdapter(MouseAdapter):
    def __init__(self,tree,mapContext):
        MouseAdapter.__init__(self)
        self.tree = tree
        self.mapContext = mapContext
    def mouseClicked(self, event):
        x = event.getX()
        y = event.getY()
        row = self.tree.getRowForLocation(x,y)
        path = self.tree.getPathForRow(row)
        if path == None or path.getPathCount() != 3:
            return
        node = path.getLastPathComponent()
        # exit for DataGroup objects
        if node == None or isinstance(node.getUserObject(), DataGroup):
            return
        layer = node.getUserObject().getLayer()
        #if SwingUtilities.isLeftMouseButton(event):
        #print "left mouseadapter:", x,y,row,path
        if x < 20:
            return
        #es = getExpansionState(self.tree) # save expansion tree state
        if x < 40:
            v = layer.isVisible()
            layer.setVisible(not v)
            # TODO set state model
            model = createTreeModel(self.mapContext)
            self.tree.setModel(model)
            #self.tree.getModel().reload()
            #setExpansionState(self.tree,es)
            expandAllNodes(self.tree, 0, self.tree.getRowCount())
            return
        
        # Menu popup
        self.mapContext.getLayers().setAllActives(False)
        layer.setActive(not layer.isActive())
        self.tree.getModel().reload()
        #setExpansionState(self.tree,es)
        expandAllNodes(self.tree, 0, self.tree.getRowCount())
        #setExpansionState(self.tree,es)
        if SwingUtilities.isRightMouseButton(event):
            # EVENT Right click"
            menu = createToCContextMenu(self.mapContext, layer)
            menu.show(self.tree,x,y)
            return
            
class VisibilityCellRenderer(TreeCellRenderer):
    def __init__(self,tree,mapContext):
        self.tree = tree
        self.mapContext = mapContext
        self.lblGroup = JLabel()
        self.lblGroup.setBackground(Color(222,227,233)) #.BLUE.brighter())
        self.lblGroup.setOpaque(True)
        self.lblGroup.setText("plddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        self.lblGroupPreferredSize = self.lblGroup.getPreferredSize()
        #border = BorderFactory.createEtchedBorder(EtchedBorder.LOWERED)
        #border = BorderFactory.createLineBorder(Color(222,227,233).darker(),1)
        #self.lblGroup.setBorder(border)
        #self.lblGroupPreferredSize.setSize(30,200)#self.lblGroupPreferredSize.getHeight()+4, self.lblGroupPreferredSize.getWidth())
        self.pnlLayer = JPanel()
        self.pnlLayer.setOpaque(False)
        #self.pnlLayer.setBorder(EmptyBorder(2,2,2,2))

        self.pnlLayer.setLayout(FlowLayout(FlowLayout.LEFT))
        self.chkLayerVisibility = JCheckBox()
        self.chkLayerVisibility.setOpaque(False)
        self.pnlLayer.add(self.chkLayerVisibility)
        self.lblLayerIcon = JLabel()
        self.lblLayerName = JLabel()
        self.lblLayerName.setText("plddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        
        self.tree.setRowHeight(int(self.pnlLayer.getPreferredSize().getHeight())-9) #+2
        self.pnlLayer.add(self.lblLayerIcon)
        self.pnlLayer.add(self.lblLayerName)
        
        self.lblUnknown = JLabel()
        
    def getTreeCellRendererComponent(self, tree, value, selected, expanded, leaf, row, hasFocus):
        uo = value.getUserObject()
        if isinstance(uo, DataGroup):
            self.lblGroup.setText(uo.getName())
            self.lblGroup.setPreferredSize(self.lblGroupPreferredSize)
            return self.lblGroup
        if isinstance(uo, DataLayer):
            layer = uo.getLayer()
            self.lblLayerName.setText(layer.getName())
            self.lblLayerIcon.setIcon(getIconFromLayer(layer))
            self.chkLayerVisibility.setSelected(layer.isVisible())
            if layer.isWithinScale(self.mapContext.getScaleView()): # and layer.isVisible():
                self.chkLayerVisibility.setEnabled(True)
            else:
                self.chkLayerVisibility.setEnabled(False)

                            
            self.lblLayerName.setForeground(Color.BLACK)
            
            font = self.lblLayerName.getFont()
            self.lblLayerName.setForeground(Color.BLACK)
            if layer.isEditing():
                self.lblLayerName.setForeground(Color.RED)
            if layer.isActive() and font.isBold():
                pass
            elif layer.isActive() and not font.isBold():
                self.lblLayerName.setFont(font.deriveFont(Font.BOLD))
            else:
                self.lblLayerName.setFont(font.deriveFont(-Font.BOLD))
            self.pnlLayer.repaint()
            return self.pnlLayer
        self.lblUnknown.setText("")
        self.lblUnknown.setPreferredSize(Dimension(0,0))

        return self.lblUnknown
        
        
def createTreeModel(mapContext, reducedTree=True):
    i18n = ToolsLocator.getI18nManager()
    root = DefaultMutableTreeNode(i18n.getTranslation("_Visibility"))
    
    rootWithVisibility = DefaultMutableTreeNode(DataGroup(i18n.getTranslation("_Visible")))
    rootWithoutVisibility = DefaultMutableTreeNode(DataGroup(i18n.getTranslation("_Out_of_Scale_Range")))
    rootNotVisibility = DefaultMutableTreeNode(DataGroup(i18n.getTranslation("_Not_Visible")))
    
    root.insert(rootWithVisibility, root.getChildCount())
    root.insert(rootWithoutVisibility, root.getChildCount())
    root.insert(rootNotVisibility, root.getChildCount())
    
    for layer in iter(mapContext.deepiterator()):
        if layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithVisibility.insert(newNode,0)
            
        elif not layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithoutVisibility.insert(newNode,0)

        elif layer.isVisible()==False:
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootNotVisibility.insert(newNode,0)
    
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
    import tabbedtoc
    tabbedtoc.main()
    
    
