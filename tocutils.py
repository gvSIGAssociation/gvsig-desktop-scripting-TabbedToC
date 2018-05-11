# encoding: utf-8

import gvsig

from javax.swing import ImageIcon
from javax.imageio import ImageIO
from java.awt.event import ActionListener
from javax.swing.tree import TreePath
from javax.swing.tree import TreeNode
from java.io import File

from javax.swing.tree import DefaultTreeCellRenderer

from javax.swing import JMenuItem
from javax.swing import JPopupMenu
from org.gvsig.app.project.documents.view import IContextMenuActionWithIcon
from org.gvsig.app.project.documents.view.toc import TocItemLeaf
from org.gvsig.tools import ToolsLocator

from org.gvsig.fmap.mapcontext.layers import LayerCollectionListener
from org.gvsig.fmap.mapcontext.layers.operations import LayerCollection

from org.gvsig.fmap.mapcontext import MapContextLocator
from org.gvsig.fmap.mapcontext.layers import LayerListener
from org.gvsig.tools.swing.api import ToolsSwingLocator

class TOCSimpleNode(TreeNode, ActionListener):
  def __init__(self, parent, icon=None):
    self.__parent = parent
    self.setIcon(icon)
        
  def toString(self):
    return  "Unknown"

  def getTree(self):
    return self.__parent.getTree()
    
  def createPopup(self):
    return None

  def showPopup(self, invoker, x, y):
    menu = self.createPopup()
    if menu!=None:
      menu.show(invoker, x, y)

  def getIcon(self):
    return self.__icon

  def setIcon(self, icon):
    if icon != None:
      if isinstance(icon, ImageIcon):
        self.__icon = icon
      else:
        self.__icon = self.load_icon(str(icon))
    else:
      self.__icon = None

  def load_icon(self, pathname):
    f = File(str(pathname))
    return ImageIcon(ImageIO.read(f))
  
  def children(self):
    # Returns the children of the receiver as an Enumeration.
    return None
    
  def getAllowsChildren(self):
    # Returns true if the receiver allows children.
    return False

  def getChildAt(self, childIndex):
    # Returns the child TreeNode at index childIndex.
    return None
    
  def getChildCount(self):
    return -1

  def getIndex(self, node):
    # Returns the index of node in the receivers children.
    return -1
     
  def getParent(self):
    # Returns the parent TreeNode of the receiver.
    return self.__parent
    
  def isLeaf(self):
    # Returns true if the receiver is a leaf.
    return True

  def actionPerformed(self, event):
    pass

  def getTreePath(self):
    x = self.getParent().getTreePath()
    x.append(self)
    return x

class TOCNode(TOCSimpleNode):
  def __init__(self, parent, icon=None):
    TOCSimpleNode.__init__(self,parent, icon=icon)
    self.__children = list()

  def toString(self):
    return "node"
    
  def getAllowsChildren(self):
    # Returns true if the receiver allows children.
    return True

  def getChildAt(self, childIndex):
    # Returns the child TreeNode at index childIndex.
    return self.__children[childIndex]
    
  def getChildCount(self):
    # Returns the number of children TreeNodes the receiver contains.
    return len(self.__children)

  def getIndex(self, node):
    # Returns the index of node in the receivers children.
    index = 0
    for x in self.__children:
      if node == x:
        return index
      index += 1
    return -1
     
  def isLeaf(self):
    # Returns true if the receiver is a leaf.
    return False

  def expand(self, node=None):
    if node == None:
      node = self
    treepath = TreePath(self.getTreePath())
    self.getTree().expandPath(treepath)  
      
  def reload(self):
    #print ">>> reload "
    root = self.getTree().getModel().getRoot()
    expandeds = self.getTree().getExpandedDescendants(TreePath(root))
    self.getTree().getModel().reload()
    if expandeds != None:
      for treePath in expandeds:
        self.getTree().expandPath(treePath)

  def add(self, element):
    self.__children.append(element)
    self.reload()
    
  def remove(self, element):
    self.__children.remove(element)
    self.reload()

  def __delslice__(self, i, j):
    del self.__children[i:j]

class TOCTreeCellRenderer(DefaultTreeCellRenderer):
  def __init__(self, icon_folder, icon_doc):
    self._icon_folder = icon_folder
    self._icon_doc = icon_doc

  def getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused):
    c = DefaultTreeCellRenderer.getTreeCellRendererComponent(self, tree, value, selected, expanded, isLeaf, row, focused)
    icon = value.getIcon()
    if icon == None:
      if value.isLeaf():
        icon = self._icon_doc
      else:
        icon = self._icon_folder
    self.setIcon(icon)
    return c


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

def createToCContextMenu(mapContext, selectedLayer):
  menu = JPopupMenu()
  ep = ToolsLocator.getExtensionPointManager().get("View_TocActions")
  tocItem = TocItemLeaf(None, selectedLayer.getName(),selectedLayer.getShapeType())
  activesLayers = mapContext.getLayers().getActives()

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
              newItem = LayerMenuItem(action, selectedLayer,tocItem, mapContext)
              menu.add(newItem)
          else:
              newItem = LayerMenuItem(action,selectedLayer,tocItem, mapContext)
              newItem.setEnabled(False)
              menu.add(newItem)
  return menu


class UpdateToCListener(LayerListener,LayerCollectionListener):
  def __init__(self, id, callable):
    self.callable = callable
    self.id = id

  def getId(self):
    return self.id

  def fireEvent(self):
    try:
      self.callable()
    except Exception,ex:
      pass
  
  def layerAdded(self, e):
    layer = e.getAffectedLayer()
    if isinstance(layer,LayerCollection):
      layer.addLayerCollectionListener(self)
    self.fireEvent()
    
  def layerAdding(self, e):
    pass

  def layerMoved(self, e):
    self.fireEvent()

  def layerMoving(self, e):
    pass

  def layerRemoved(self, e):
    self.fireEvent()

  def layerRemoving(self, e):
    pass

  def visibilityChanged(self, e):
    self.fireEvent()
  
  def activationChanged(self,e):
    self.fireEvent()

  def drawValueChanged(self,e):
    self.fireEvent()

  def editionChanged(self,e):
    self.fireEvent()

  def nameChanged(self,e):
    self.fireEvent()


def addUpdateToCListener(id, mapContext, func):
  layers = mapContext.getLayers()
  if layers == None:
    return
  mylistener = UpdateToCListener(id,func)
  layersList = list()
  layersList.append(layers)
  layersList.extend(mapContext.deepiterator()) 
  for layer in layersList:
    listeners = layer.getLayerListeners()
    for listener in listeners:
      if isinstance(listener,UpdateToCListener) and listener.getId()==id:
        layer.removeLayerListener(listener)
    if isinstance(layer, LayerCollection):
      layer.addLayerCollectionListener(mylistener)
    layer.addLayerListener(mylistener)


mapContextManager = None
iconTheme = None

def getIconByPath(pathname):
    f = File(str(pathname))
    return ImageIcon(ImageIO.read(f))
    
def getIconByName(iconName):
  global iconTheme
  if iconTheme == None:
    iconTheme = ToolsSwingLocator.getIconThemeManager().getCurrent()
  icon = iconTheme.get(iconName)
  return icon
  
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


def expandAllNodes(tree, startingIndex, rowCount):
    for i in xrange(startingIndex,rowCount): 
        tree.expandRow(i)
    if tree.getRowCount()!=rowCount:
        expandAllNodes(tree, rowCount, tree.getRowCount())
        

            
def getExpansionState(tree):
    x = []
    for i in range(0, tree.getRowCount()):
        if tree.isExpanded(i):
            x.append(tree.getPathForRow(i)) #[1].toString()))
    return x

def setExpansionState(tree, x):
    for i in x:
       tree.expandPath(i)

def main(*args):
    pass
