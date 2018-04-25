# encoding: utf-8

import gvsig
from gvsig import getResource
from gvsig.libs.formpanel import load_icon

import os

import tocutils
reload(tocutils)

from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel

def setTreeAsSourceOrder(tree, mapContext):
  model = createTreeModel(mapContext)
  tree.setModel(model)
  expandAllNodes(tree, 0, tree.getRowCount())


def expandAllNodes(tree, startingIndex, rowCount):
    for i in xrange(startingIndex,rowCount): 
        tree.expandRow(i)

    if tree.getRowCount()!=rowCount:
        expandAllNodes(tree, rowCount, tree.getRowCount())

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
    
class DataLayer(object):
  def __init__(self,path,layer):
    self.__path = path
    self.__layer = layer
    self.__label = os.path.basename(self.__path)
  def getName(self):
    return self.__label
  
  toString = getName
  __str__ = getName
  __repr__ = getName

  def isLeaf(self):
    return True
    

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
    folder = DefaultMutableTreeNode(DataFolder(path,path))
    root.insert(folder, root.getChildCount())
    for pathLayer,layer in folders[path]:
      leaf = DefaultMutableTreeNode(DataLayer(pathLayer,layer))
      folder.insert(leaf, folder.getChildCount())
      
def createTreeModel(mapContext, reducedTree=True):
  root = DefaultMutableTreeNode("root")
  localLayers = DefaultMutableTreeNode(DataFolder("Local layers",None))
  remoteLayers = DefaultMutableTreeNode(DataFolder("Remote layers",None))
  root.insert(localLayers, root.getChildCount())
  root.insert(remoteLayers, root.getChildCount())
  layers = list()
  for layer in iter(mapContext.deepiterator()):
    if layer.getDataStore() == None:
        continue
    params = layer.getDataStore().getParameters()
    getFile = getattr(params, "getFile", None)
    if getFile != None:
      getTable = getattr(params, "getTable", None)
      if getTable!=None:
        layers.append((os.path.join(getFile().getAbsolutePath(),getTable()),layer))
      else:
        layers.append((getFile().getAbsolutePath(),layer))
  layers.sort(cmp = lambda x,y: cmp(x[0],y[0]))
  if reducedTree:
    buildReducedTreeFromLayers(localLayers,layers)
  else:
    for path,layer in layers:
      buildTreeFromPath(localLayers,path,layer)
    
  model = DefaultTreeModel(root)
  return model
  
def main(*args):
    import tabbedtoc
    tabbedtoc.main()
    
