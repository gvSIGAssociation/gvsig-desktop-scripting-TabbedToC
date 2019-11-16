# encoding: utf-8

import gvsig

# TODO soport para el viewportlistener
# http://downloads.gvsig.org/download/web/es/build/html/scripting_devel_guide/2.3/capturando_eventos.html
import tocutils
reload(tocutils)
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
from org.gvsig.app import ApplicationLocator

from org.gvsig.fmap.mapcontext.events.listeners import ViewPortListener
from javax.swing import SwingUtilities
from org.gvsig.app.project.documents.view import IContextMenuActionWithIcon
from org.gvsig.fmap.mapcontext.layers.operations import SingleLayer
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
#from tocutils import expandAllNodes
from tocutils import getIconFromLayer
from tocutils import getIconByName
from org.gvsig.tools import ToolsLocator
from tocutils import getExpansionState
from tocutils import setExpansionState

from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

def setTreeAsSelectionOrder(tree, mapContext):
  updateAll(tree, mapContext)
  tree.setCellRenderer(SelectionCellRenderer(tree, mapContext))
  tree.addMouseListener(SelectionMouseAdapter(tree,mapContext))
  addUpdateToCListener("SelectionOrder", mapContext, UpdateListener(tree,mapContext))
  tree.revalidate()
  tree.repaint()
  
def updateAll(tree, mapContext):
  exp = getExpansionState(tree)
  model = createTreeModel(mapContext)
  tree.setModel(model)
  tree.getModel().reload()
  #tree.revalidate()
  #tree.repaint()
  #expandAllNodes(tree, 0, tree.getRowCount())
  setExpansionState(tree, exp)
  #logger("Not able to set expansion state", LOGGER_ERROR)
  tree.revalidate()
  tree.repaint()

class UpdateListener():
  def __init__(self, tree, mapContext):
    self.mapContext = mapContext
    self.tree = tree

  def __call__(self):
    updateAll(self.tree, self.mapContext)
    
class SelectionMouseAdapter(MouseAdapter):
  def __init__(self,tree,mapContext):
    MouseAdapter.__init__(self)
    self.tree = tree
    self.mapContext = mapContext
    
  def mouseClicked(self, event):
    x = event.getX()
    y = event.getY()
    row = self.tree.getRowForLocation(x,y)
    path = self.tree.getPathForRow(row)
    if path == None: # or path.getPathCount() != 3:
      return
    node = path.getLastPathComponent()
    #print "node feature mouseadapter:", x,y,row,path

    if node == None:
      return
    if isinstance(node.getUserObject(), DataGroup):
      return
    if isinstance(node.getUserObject(), FeatureDataLayerNode):
      es = getExpansionState(self.tree)
      uo = node.getUserObject()
      feature = uo.getFeature()
      if x>42 and x<62:
        layer = node.getUserObject().getLayer()
        layer.getDataStore().getFeatureSelection().deselect(feature)
      elif x>62:
        envelope = feature.getDefaultGeometry().getEnvelope()
        self.mapContext.getViewPort().setEnvelope(envelope)
      setExpansionState(self.tree,es)
      return
    if isinstance(node.getUserObject(), DataLayer):
      layer = node.getUserObject().getLayer()
      #if SwingUtilities.isLeftMouseButton(event):
      #print "left mouseadapter:", x,y,row,path
      if x < 20:
        return
      es = getExpansionState(self.tree) # save expansion tree state
      if x < 40:
        v = layer.isVisible()
        layer.setVisible(not v)
        # TODO set state model
        model = createTreeModel(self.mapContext)
        self.tree.setModel(model)
        self.tree.getModel().reload()
        setExpansionState(self.tree,es)
        #expandAllNodes(self.tree, 0, self.tree.getRowCount())
        return
      if x < 60:
        layer.getSelection().deselectAll()
        # TODO set state model
        model = createTreeModel(self.mapContext)
        self.tree.setModel(model)
        self.tree.getModel().reload()
        #self.tree.getModel().reload()
        setExpansionState(self.tree,es)
        #expandAllNodes(self.tree, 0, self.tree.getRowCount())
        return
      
      # Menu popup
      self.mapContext.getLayers().setAllActives(False)
      layer.setActive(not layer.isActive())
      self.tree.getModel().reload()

      #expandAllNodes(self.tree, 0, self.tree.getRowCount())
      setExpansionState(self.tree,es)
      if SwingUtilities.isRightMouseButton(event):
        # EVENT Right click"
        menu = createToCContextMenu(self.mapContext, layer)
        menu.show(self.tree,x,y)
      ApplicationLocator.getApplicationManager().refreshMenusAndToolBars()
        
class SelectionCellRenderer(TreeCellRenderer):
  def __init__(self,tree,mapContext):
    self.tree = tree
    self.mapContext = mapContext
    self.lblGroup = JLabel()
    self.lblGroup.setBackground(Color(222,227,233)) #.BLUE.brighter())
    self.lblGroup.setOpaque(True)
    self.lblGroup.setText("plddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
    
    self.lblGroupPreferredSize = self.lblGroup.getPreferredSize()
    #h = self.lblGroupPreferredSize.getHeight()
    #w = self.lblGroupPreferredSize.getWidth()
    #self.lblGroupPreferredSize.setSize(h, w)
    self.pnlLayer = JPanel()
    self.pnlLayer.setOpaque(False)

    self.pnlLayer.setLayout(FlowLayout(FlowLayout.LEFT))

    self.lblClean = JLabel()

    self.chkLayerVisibility = JCheckBox()
    self.chkLayerVisibility.setOpaque(False)
    self.lblLayerName = JLabel()
    self.lblLayerIcon = JLabel()
    self.lblFeatureSelecteds = JLabel()

    self.pnlLayer.add(self.chkLayerVisibility)
    self.pnlLayer.add(self.lblClean)
    self.pnlLayer.add(self.lblFeatureSelecteds)
    self.pnlLayer.add(self.lblLayerIcon)
    self.pnlLayer.add(self.lblLayerName)
    self.tree.setRowHeight(int(self.pnlLayer.getPreferredSize().getHeight())-3)
    self.lblUnknown = JLabel()

    ## Feature
    self.lblFeatureIcon = JLabel()
    self.lblFeatureName = JLabel()
    i18n = ToolsLocator.getI18nManager()
    self.lblFeatureName.setText(i18n.getTranslation("_Feature"))
    self.pnlFeature = JPanel()
    self.pnlFeature.setOpaque(False)
    self.pnlFeature.setLayout(FlowLayout(FlowLayout.LEFT))
    self.pnlFeature.add(self.lblFeatureIcon)
    self.pnlFeature.add(self.lblFeatureName)
      
  def getTreeCellRendererComponent(self, tree, value, selected, expanded, leaf, row, hasFocus):
    uo = value.getUserObject()
    if isinstance(uo, DataGroup):
      text = "[" + str(value.getChildCount()) +"] " + uo.getName()
      self.lblGroup.setText(text)
      self.lblGroup.setPreferredSize(self.lblGroupPreferredSize)
      return self.lblGroup
    if isinstance(uo, DataLayer):
      layer = uo.getLayer()

      self.lblLayerName.setText(uo.getName())
      self.lblLayerIcon.setIcon(getIconFromLayer(layer))
      if layer.isVisible():
          self.lblLayerName.setEnabled(True)
      else:
          self.lblLayerName.setEnabled(False)
      self.lblClean.setIcon(getIconByName("edit-clear"))
      self.chkLayerVisibility.setSelected(layer.isVisible())
      if layer.isWithinScale(self.mapContext.getScaleView()): # and layer.isVisible():
          self.chkLayerVisibility.setEnabled(True)
      else:
          self.chkLayerVisibility.setEnabled(False)
      if layer.getDataStore() != None and layer.getDataStore().getSelection()!= None and layer.getDataStore().getSelection().getSize() !=0: # and layer.isVisible():
          self.lblClean.setEnabled(True)
          self.lblFeatureSelecteds.setText(str(layer.getDataStore().getSelection().getSize()))
          self.lblFeatureSelecteds.setEnabled(True)
      else:
          self.lblClean.setEnabled(False)
          self.lblFeatureSelecteds.setText("0")
          self.lblFeatureSelecteds.setEnabled(False)
          
      font = self.lblLayerName.getFont()
      self.lblLayerName.setForeground(Color.BLACK)
      if layer.isEditing():
          self.lblLayerName.setForeground(Color.RED)
      #if layer.isActive():
      if layer.isActive(): # and not font.isBold():
          newfont = font.deriveFont(Font.BOLD)
          self.lblLayerName.setFont(newfont)
      else:
          newfont = font.deriveFont(Font.PLAIN)
          self.lblLayerName.setFont(newfont)

      return self.pnlLayer
    if isinstance(uo, FeatureDataLayerNode):
      self.lblFeatureName.setText(uo.getFeature().toString())
      self.lblFeatureIcon.setIcon(getIconByName("edit-clear"))
      
      return self.pnlFeature
    self.lblUnknown.setText("")
    self.lblUnknown.setPreferredSize(Dimension(0,0))
    return self.lblUnknown
        
        
def createTreeModel(mapContext, reducedTree=True):
  i18n = ToolsLocator.getI18nManager()
  
  root = DefaultMutableTreeNode(i18n.getTranslation("_Selection"))
  
  rootSelected = DefaultMutableTreeNode(DataGroup(i18n.getTranslation("_Selected")))
  rootSelectable = DefaultMutableTreeNode(DataGroup(i18n.getTranslation("_Selectable")))
  rootNotSelectable = DefaultMutableTreeNode(DataGroup(i18n.getTranslation("_Not_selectable")))
  
  root.insert(rootSelected, root.getChildCount())
  root.insert(rootSelectable, root.getChildCount())
  root.insert(rootNotSelectable, root.getChildCount())

  for layer in iter(mapContext.deepiterator()):
    if not isinstance(layer, SingleLayer):
      continue
    store = layer.getDataStore()
    if isinstance(store,DefaultFeatureStore) and store.getSelection().getSize() != 0:
      newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))

      fset = layer.getDataStore().getSelection()
      for f in fset:
          newFeature = DefaultMutableTreeNode(FeatureDataLayerNode(layer.getName(),layer,f))
          newNode.insert(newFeature, newNode.getChildCount())
      rootSelected.insert(newNode, 0)
    elif isinstance(store,DefaultFeatureStore):
      newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
      rootSelectable.insert(newNode,0)
    else:
      newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
      rootNotSelectable.insert(newNode,0)
      
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
    if path != None:
      self.__label = os.path.basename(self.__path)
    else:
      self.__label = None
  def getName(self):
    return self.__label
  def getLayer(self):
      return self.__layer
  toString = getName
  __str__ = getName
  __repr__ = getName
  def isLeaf(self):
    return True
    
class FeatureDataLayerNode(object):
  def __init__(self,path,layer,feature):
    self.__path = path
    self.__layer = layer
    self.__label = os.path.basename(self.__path)
    self.__feature  = feature
  def getName(self):
    return self.__feature.toString()
  def getFeature(self):
    return self.__feature
  def getLayer(self):
      return self.__layer
  toString = getName
  __str__ = getName
  __repr__ = getName
  def isLeaf(self):
    return True
    
class FeatureDataLayer(DataLayer):
    def __init__(self, path, layer, feature):
        DataLayer.__init__(self,path,layer)
        self.__feature = feature
    def getName(self):
        return self.__feature.toString()
    def getFeature(self):
        return self.__feature
        
def main(*args):
    import tabbedtoc
    tabbedtoc.main()
    
    
