# encoding: utf-8

import gvsig

# TODO soport para el viewportlistener
# http://downloads.gvsig.org/download/web/es/build/html/scripting_devel_guide/2.3/capturando_eventos.html


from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel
import os

def setTreeAsVisibilityOrder(tree, mapContext):
  model = createTreeModel(mapContext)
  tree.setModel(model)
  expandAllNodes(tree, 0, tree.getRowCount())

def expandAllNodes(tree, startingIndex, rowCount):
    for i in xrange(startingIndex,rowCount): 
        tree.expandRow(i)

    if tree.getRowCount()!=rowCount:
        expandAllNodes(tree, rowCount, tree.getRowCount())
        
def createTreeModel(mapContext, reducedTree=True):
    root = DefaultMutableTreeNode("Visibility")
    rootWithVisibility = DefaultMutableTreeNode(DataFolder("Layers with Visibility",None))
    rootWithoutVisibility = DefaultMutableTreeNode(DataFolder("Layers without Visibility",None))
    rootNotVisibility = DefaultMutableTreeNode(DataFolder("Layers desactivated",None))
    
    root.insert(rootWithVisibility, root.getChildCount())
    root.insert(rootWithoutVisibility, root.getChildCount())
    root.insert(rootNotVisibility, root.getChildCount())
    
    yesVis = list()
    outVis = list()
    notVis = list()
    for layer in iter(mapContext.deepiterator()):
        if layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            yesVis.append(layer)
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithVisibility.insert(newNode, rootWithVisibility.getChildCount())
        elif not layer.isWithinScale(mapContext.getScaleView()) and layer.isVisible():
            outVis.append(layer)
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootWithoutVisibility.insert(newNode, rootWithoutVisibility.getChildCount())
        elif layer.isVisible()==False:
            notVis.append(layer)
            newNode = DefaultMutableTreeNode(DataLayer(layer.getName(),layer))
            rootNotVisibility.insert(newNode,rootNotVisibility.getChildCount())
            
    #for v in yesVis:
    #    folder = DefaultMutableTreeNode(DataFolder(path,path))
    #    root.insert(folder, root.getChildCount())
    """
    layers.sort(cmp = lambda x,y: cmp(x[0],y[0]))
    if reducedTree:
      buildReducedTreeFromLayers(localLayers,layers)
    else:
      for path,layer in layers:
        buildTreeFromPath(localLayers,path,layer)
    """
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
    
def main(*args):

    layer = gvsig.currentLayer()
    print layer.getMinScale()
    print layer.getMaxScale()
    print layer.isVisible()
    mapcontext = gvsig.currentView().getMapContext()
    print layer.isWithinScale(mapcontext.getScaleView())
    
    
