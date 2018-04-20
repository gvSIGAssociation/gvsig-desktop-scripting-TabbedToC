# encoding: utf-8

import gvsig

from javax.swing import ImageIcon
from javax.imageio import ImageIO
from java.awt.event import ActionListener
from javax.swing.tree import TreePath
from javax.swing.tree import TreeNode
from java.io import File

from javax.swing.tree import DefaultTreeCellRenderer

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

def main(*args):
    pass
