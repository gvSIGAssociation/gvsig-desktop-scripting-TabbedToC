# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

import os

import tocutils
reload(tocutils)

from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel
from org.gvsig.app import ApplicationLocator
#from tocutils import expandAllNodes

from java.awt import Color
from java.awt import Dimension
from java.awt import FlowLayout
from java.awt import Font
from javax.swing import BorderFactory
from javax.swing import JCheckBox
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing.tree import TreeCellRenderer
from tocutils import getIconFromLayer
from tocutils import addUpdateToCListener

from java.awt.event import MouseAdapter
from javax.swing import SwingUtilities
from tocutils import createToCContextMenu

from tocutils import getIconByName
from org.gvsig.tools import ToolsLocator

from tocutils import getIconByPath

from tocutils import getExpansionState
from tocutils import setExpansionState
from org.gvsig.fmap.mapcontext.layers.operations import SingleLayer
def setTreeAsSourceOrder(tree, mapContext):
  updateAll(tree, mapContext)
 
  tree.setCellRenderer(SourceCellRenderer(tree, mapContext))
  tree.addMouseListener(SourceMouseAdapter(tree,mapContext))
  addUpdateToCListener("SourceOrder", mapContext, UpdateListener(tree,mapContext))
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
  tree.revalidate()
  tree.repaint()
    
class UpdateListener():
  def __init__(self, tree, mapContext):
    self.mapContext = mapContext
    self.tree = tree

  def __call__(self):
    if SwingUtilities.isEventDispatchThread():
      updateAll(self.tree, self.mapContext)
    else:
      SwingUtilities.invokeLater(lambda:updateAll(self.tree, self.mapContext))


    
class SourceMouseAdapter(MouseAdapter):
    def __init__(self,tree,mapContext):
        MouseAdapter.__init__(self)
        self.tree = tree
        self.mapContext = mapContext

    def mouseClicked(self, event):
        x = event.getX()
        y = event.getY()
        row = self.tree.getRowForLocation(x,y)
        path = self.tree.getPathForRow(row)
        #print "left mouseadapter:", x,y,row,path

        if path == None or path.getPathCount() != 4:
            return
        node = path.getLastPathComponent()
        # exit for DataGroup objects
        if node == None or isinstance(node.getUserObject(), DataGroup):
            return
        layer = node.getUserObject().getLayer()
        #if SwingUtilities.isLeftMouseButton(event):
        if x < 46:
            return
        es = getExpansionState(self.tree) # save expansion tree state
        if x < 62:
            v = layer.isVisible()
            layer.setVisible(not v)
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
        setExpansionState(self.tree,es)
        #expandAllNodes(self.tree, 0, self.tree.getRowCount())
        if SwingUtilities.isRightMouseButton(event):
            # EVENT Right click"
            menu = createToCContextMenu(self.mapContext, layer)
            menu.show(self.tree,x,y)
            return
        ApplicationLocator.getApplicationManager().refreshMenusAndToolBars()
class SourceCellRenderer(TreeCellRenderer):
    def __init__(self,tree,mapContext):
        self.tree = tree
        self.mapContext = mapContext
        ## Group
        self.lblFolder = JLabel()
        self.lblFolder.setBackground(Color(222,227,233)) #.BLUE.brighter())
        self.lblFolder.setOpaque(True)
        self.lblFolder.setText("plddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        
        ### Folder
        self.pnlFolder = JPanel()
        self.pnlFolder.setOpaque(False)
        self.pnlFolder.setLayout(FlowLayout(FlowLayout.LEFT))
        self.lblGroup = JLabel()
        #self.lblGroup.setBackground(Color(222,227,233)) #.BLUE.brighter())
        #self.lblGroup.setOpaque(True)
        self.lblGroup.setText("plddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        self.lblGroupPreferredSize = self.lblGroup.getPreferredSize()
        self.lblGroupIcon = JLabel()
        self.pnlFolder.add(self.lblGroupIcon)
        self.pnlFolder.add(self.lblGroup)
        #self.lblGroup.setBorder(
        #  BorderFactory.createLineBorder(Color(222,227,233).darker(),1)
        #)
        #self.lblGroupPreferredSize.setSize(30,200)#self.lblGroupPreferredSize.getHeight()+4, self.lblGroupPreferredSize.getWidth())
        
        ### LAYER
        self.pnlLayer = JPanel()
        self.pnlLayer.setOpaque(False)
        #self.pnlLayer.setBorder(EmptyBorder(2,2,2,2))

        self.pnlLayer.setLayout(FlowLayout(FlowLayout.LEFT))
        self.chkLayerVisibility = JCheckBox()
        self.chkLayerVisibility.setOpaque(False)
        self.pnlLayer.add(self.chkLayerVisibility)
        self.lblLayerIcon = JLabel()
        self.lblLayerName = JLabel()
        self.pnlLayer.add(self.lblLayerIcon)
        self.pnlLayer.add(self.lblLayerName)
        #self.tree.setRowHeight(int(self.pnlLayer.getPreferredSize().getHeight())) #+2
        self.tree.setRowHeight(int(self.pnlFolder.getPreferredSize().getHeight()))
        
        self.lblUnknown = JLabel()
        
    def getTreeCellRendererComponent(self, tree, value, selected, expanded, leaf, row, hasFocus):
        uo = value.getUserObject()
        if isinstance(uo, DataFolder):
            #self.lblFolder.setText(uo.getName())
            text = "[" + str(value.getChildCount()) +"] " + uo.getName()
            self.lblFolder.setText(text)
            self.lblFolder.setPreferredSize(self.lblGroupPreferredSize)
            if uo.getIcon()!=None:
                self.lblGroupIcon.setIcon(uo.getIcon())
            else:
                self.lblGroupIcon.setIcon(getIconByName("common-folder-open")) #icon-folder-open"))
            
            return self.lblFolder
        if isinstance(uo, DataGroup):
            self.lblGroup.setText(uo.getName())
            self.lblGroup.setPreferredSize(self.lblGroupPreferredSize)
            if uo.getIcon()!=None:
                self.lblGroupIcon.setIcon(uo.getIcon())
            else:
                #import pdb
                #pdb.set_trace()
                self.lblGroupIcon.setIcon(getIconByName("common-folder-open")) #icon-folder-open"))
            
            return self.pnlFolder
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
                newfont = font.deriveFont(Font.BOLD)
                self.lblLayerName.setFont(newfont)
            else:
                newfont = font.deriveFont(Font.PLAIN)
                self.lblLayerName.setFont(newfont)
            #self.pnlLayer.repaint()
            return self.pnlLayer
        self.lblUnknown.setText("")
        self.lblUnknown.setPreferredSize(Dimension(0,0))

        return self.lblUnknown


class DataFolder(object):
  def __init__(self,name, path, icon=None):
    self.__name = name
    self.__path = path
    #if icon==None:
    #   self.__icon = icon
    #else:
    self.__icon = icon
    
  def getIcon(self):
      return self.__icon
  def getName(self):
    return self.__name

  def __str__(self):
    return self.__name
  toString = __str__
  __repr__ = __str__

  def isLeaf(self):
    return False
    
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

class DataGroup(object):
  def __init__(self,name, path, icon=None):
    self.__name = name
    self.__path = path
    #if icon==None:
    #   self.__icon = icon
    #else:
    self.__icon = icon
    
  def getIcon(self):
      return self.__icon
  def getName(self):
    return self.__name

  def __str__(self):
    return self.__name
  toString = __str__
  __repr__ = __str__

  def isLeaf(self):
    return False
    

def buildTreeFromPath(root, path, layer):
  if path[0]=="/":
    path=path[1:]
  pathsegments = path.split("/")
  node = root
  curpath = ""
  for segment in pathsegments:
    curpath = os.path.join(curpath,segment)
    index = childIndex(node, segment)
    if index < 0:
      newChild = DefaultMutableTreeNode(DataFolder(segment,curpath))
      node.insert(newChild, node.getChildCount())
      node = newChild
    else:
      node = node.getChildAt(index)
  node.setUserObject(DataLayer(path,layer))
 
def childIndex(node, name):
  for index in xrange(0,node.getChildCount()):
    child = node.getChildAt(index)
    x = child.getUserObject()
    if x.getName() == name:
      return index
  return -1

def buildReducedTreeFromLayers(root, layers):
  folders = dict()
  for path,layer in layers:
    dirname = os.path.dirname(path)
    leafs = folders.get(dirname,None)
    if leafs == None:
      leafs=list()
      folders[dirname] = leafs
    leafs.append((path,layer))
  paths = folders.keys()
  paths.sort()

  for path in paths:
    # select icon and insert in tree
    folderPath = folders[path]
    if not os.path.isdir(path):
        #properIcon = getIconByPath(gvsig.getResource(__file__,"images","tabbedtoc-database.png"))
        properIcon = getIconByName("tabbedtoc-database")
        if path=="":
            i18n = ToolsLocator.getI18nManager()
            path=i18n.getTranslation("_Services")
        folder = DefaultMutableTreeNode(DataGroup(path,path,properIcon))
    else:
        properIcon = getIconByName("common-folder-closed")
        folder = DefaultMutableTreeNode(DataGroup(path,path,properIcon))
    
    root.insert(folder, root.getChildCount())
    for pathLayer,layer in folderPath:
      leaf = DefaultMutableTreeNode(DataLayer(pathLayer,layer))
      folder.insert(leaf, folder.getChildCount())
      
def createTreeModel(mapContext, reducedTree=True):
  i18n = ToolsLocator.getI18nManager()
  root = DefaultMutableTreeNode(i18n.getTranslation("_Root"))
  localLayers = DefaultMutableTreeNode(DataFolder(i18n.getTranslation("_Local_layers"),None))
  remoteLayers = DefaultMutableTreeNode(DataFolder(i18n.getTranslation("_Remote_layers"),None))
  root.insert(localLayers, root.getChildCount())
  root.insert(remoteLayers, root.getChildCount())
  layers = list()
  remotes = list()

  for layer in iter(mapContext.deepiterator()):
    getDataStore = getattr(layer,"getDataStore",None)
    if getDataStore == None:
      continue
    if getDataStore() == None:
        # asumimos que es raster
        uri = layer.getURI()
        if uri != None:
            layers.append((uri.getPath(),layer))
        else:
            remotes.append((layer.getName(), layer))
        continue
    
    params = getDataStore().getParameters()
    getFile = getattr(params, "getFile", None)
    if getFile != None and getFile() !=None:
      getTable = getattr(params, "getTable", None)
      if  getTable != None and getTable() !=None:
        layers.append((os.path.join(getFile().getAbsolutePath(),getTable()),layer))
      else:
        layers.append((getFile().getAbsolutePath(),layer))
    else:
      remotes.append((layer.getName(), layer))
  layers.sort(cmp = lambda x,y: cmp(x[0],y[0]))

  if reducedTree:
    buildReducedTreeFromLayers(localLayers,layers)
    buildReducedTreeFromLayers(remoteLayers,remotes)
  else:
    for path,layer in layers:
      buildTreeFromPath(localLayers,path,layer)
    
  model = DefaultTreeModel(root)
  return model
  
def main(*args):
    import tabbedtoc
    tabbedtoc.main()
    
