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

class LayerMenuItem(JMenuItem, ActionListener):
    def __init__(self, action, layer, tocItem,mapContext):
        self.action = action
        self.layer = layer
        self.tocItem = tocItem
        self.mapContext = mapContext
        self.addActionListener(self)
        self.setText(self.action.getText())
        if isinstance(self.action, IContextMenuActionWithIcon):
            self.setIcon(self.action.getIcon())
            
    def actionPerformed(self, event):
        layers = self.mapContext.getLayers().getActives()
        self.action.execute(self.tocItem,layers)

def setTreeAsVisibilityOrder(tree, mapContext):
  model = createTreeModel(mapContext)
  tree.setModel(model)
  tree.setCellRenderer(VisibilityCellRenderer(tree, mapContext))
  tree.addMouseListener(VisibilityMouseAdapter(tree,mapContext))
  vportlistener = VisibilityViewPortListener(tree, mapContext)
  mapContext.getViewPort().addViewPortListener(vportlistener)
  for layer in iter(mapContext.deepiterator()): #org.gvsig.fmap.mapcontext.layers
    listeners = layer.getLayerListeners()
    for listener in listeners:
        if getattr(listener, 'getName', False):
            if listener.getName()=='VisibilityLayerListener':
              layer.removeLayerListener(listener)
    store = layer.getDataStore()
    #if isinstance(store,DefaultFeatureStore):
    layer.addLayerListener(VisibilityLayerListener(tree,mapContext))
  expandAllNodes(tree, 0, tree.getRowCount())
  
class VisibilityLayerListener(LayerListener):
  def __init__(self, tree,mapContext):
    self.mapContext = mapContext
    self.tree = tree
  def getName(self):
    return "VisibilityLayerListener"
  def activationChanged(self,e):
    model = createTreeModel(self.mapContext)
    self.tree.setModel(model)
    expandAllNodes(self.tree, 0, self.tree.getRowCount())
  def drawValueChanged(self,e):
    model = createTreeModel(self.mapContext)
    self.tree.setModel(model)
    expandAllNodes(self.tree, 0, self.tree.getRowCount())
  def editionChanged(self,e):
    model = createTreeModel(self.mapContext)
    self.tree.setModel(model)
    expandAllNodes(self.tree, 0, self.tree.getRowCount())
  def nameChanged(self,e):
    print "name"
  def visibilityChanged(self,e):
    model = createTreeModel(self.mapContext)
    self.tree.setModel(model)
    expandAllNodes(self.tree, 0, self.tree.getRowCount())
    
#TODO viewport class
class VisibilityViewPortListener(ViewPortListener):
  def __init__(self, tree,mapContext):
      self.mapContext = mapContext
      self.tree = tree
  # Metodo obligatorio de ViewPortListener
  def backColorChanged(self,*args):
      pass

  # Metodo obligatorio de ViewPortListener
  def extentChanged(self,*args):
      model = createTreeModel(self.mapContext)
      self.tree.setModel(model)
      expandAllNodes(self.tree, 0, self.tree.getRowCount())
  # Metodo obligatorio de ViewPortListener
  def projectionChanged(self,*args):
      pass
      
def expandAllNodes(tree, startingIndex, rowCount):
    for i in xrange(startingIndex,rowCount): 
        tree.expandRow(i)

    if tree.getRowCount()!=rowCount:
        expandAllNodes(tree, rowCount, tree.getRowCount())
        

mapContextManager = None
iconTheme = None

def getIconFromLayer(layer):
  global mapContextManager
  global iconTheme
  if layer == None or layer.getDataStore()==None:
      return None
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
            menu = JPopupMenu()
            ep = ToolsLocator.getExtensionPointManager().get("View_TocActions")
            tocItem = TocItemLeaf(None, layer.getName(),layer.getShapeType())
            activesLayers = self.mapContext.getLayers().getActives()

            actions = []
            for epx in ep.iterator():
                action = epx.create()
                actions.append([action,action.getGroupOrder(), action.getGroup(), action.getOrder()])

            sortedActions =  sorted(actions, key = lambda x: (x[1], x[2],x[3]))
            group = None
            for actionList in sortedActions:
                action = actionList[0]
                if action.isVisible(tocItem, activesLayers): #(layer,)):
                    if group == None:
                        pass
                    elif group != action.getGroup():
                        menu.addSeparator()
                    group = action.getGroup()
                    if action.isEnabled(tocItem, activesLayers):
                        newItem = LayerMenuItem(action, layer,tocItem, self.mapContext)
                        menu.add(newItem)
                    else:
                        newItem = LayerMenuItem(action,layer,tocItem, self.mapContext)
                        newItem.setEnabled(False)
                        menu.add(newItem)

            menu.show(self.tree,x,y)
            return
            
def getExpansionState(tree):
    x = []
    for i in range(0, tree.getRowCount()):
        if tree.isExpanded(i):
            x.append(tree.getPathForRow(i)) #[1].toString()))
    return x

def setExpansionState(tree, x):
    for i in x:
       tree.expandPath(i)

class VisibilityCellRenderer(TreeCellRenderer):
    def __init__(self,tree,mapContext):
        self.tree = tree
        self.mapContext = mapContext
        self.lblGroup = JLabel()
        self.lblGroup.setBackground(Color(222,227,233)) #.BLUE.brighter())
        self.lblGroup.setOpaque(True)
        self.lblGroup.setText("plddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        self.lblGroupPreferredSize = self.lblGroup.getPreferredSize()
        #self.lblGroupPreferredSize.setSize(30,200)#self.lblGroupPreferredSize.getHeight()+4, self.lblGroupPreferredSize.getWidth())
        self.pnlLayer = JPanel()
        self.pnlLayer.setOpaque(False)
        #self.pnlLayer.setBorder(EmptyBorder(2,2,2,2))

        self.pnlLayer.setLayout(FlowLayout(FlowLayout.LEFT))
        self.chkLayerVisibility = JCheckBox()
        self.pnlLayer.add(self.chkLayerVisibility)
        self.lblLayerIcon = JLabel()
        self.lblLayerName = JLabel()
        self.pnlLayer.add(self.lblLayerIcon)
        self.pnlLayer.add(self.lblLayerName)
        self.tree.setRowHeight(int(self.pnlLayer.getPreferredSize().getHeight())) #+2
        
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
    root = DefaultMutableTreeNode("Visibility")
    
    rootWithVisibility = DefaultMutableTreeNode(DataGroup("Visible"))
    rootWithoutVisibility = DefaultMutableTreeNode(DataGroup("Out of Scale Range"))
    rootNotVisibility = DefaultMutableTreeNode(DataGroup("Not visible"))
    
    root.insert(rootWithVisibility, root.getChildCount())
    root.insert(rootWithoutVisibility, root.getChildCount())
    root.insert(rootNotVisibility, root.getChildCount())
    
    for layer in iter(mapContext.deepiterator()):
        if layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithVisibility.insert(newNode, rootWithVisibility.getChildCount())
            
        elif not layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithoutVisibility.insert(newNode, rootWithoutVisibility.getChildCount())
        elif layer.isVisible()==False:
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
    import tabbedtoc
    tabbedtoc.main()
    
    
