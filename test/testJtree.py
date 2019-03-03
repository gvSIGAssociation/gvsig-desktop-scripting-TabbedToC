# encoding: utf-8

import gvsig

from javax.swing.tree import DefaultMutableTreeNode
#
from addons.TabbedToC.patchs.fixformpanel import fixFormPanelResourceLoader
from javax.swing.tree import DefaultTreeModel

from javax.swing import JTree

from gvsig.libs.formpanel import FormPanel
from java.awt import Component

from javax.swing.tree import TreePath

def collapseAll(tree, parent):
    node = parent.getLastPathComponent()
    if node.getChildCount() >= 0:
      for n in node.children():
        path = parent.pathByAddingChild(n)
        collapseAll(tree, path)
    tree.collapsePath(parent)
    
def getExpansionState(tree):
    x = []
    for i in range(0, tree.getRowCount()):
      if tree.isExpanded(i):
        x.append(tree.getPathForRow(i))
    return x

def setExpansionState(tree, x, startingIndex=0):
    rowCount = tree.getRowCount()
    if not x:
       return
    for i in range(startingIndex, rowCount):
      p = tree.getPathForRow(i)
      for path in x:
        if path.toString()==p.toString():
          tree.expandPath(p)
    if tree.getRowCount()!=rowCount:
        setExpansionState(tree, x, rowCount)
    

def printNode(node):
    childCount = node.getChildCount()

    print "---" + node.toString() + "---"

    for i in range(0, childCount):
        childNode = node.getChildAt(i)
        if childNode.getChildCount() > 0:
            printNode(childNode)
        else:
            print childNode.toString(), type(childNode)
    print "+++" + node.toString() + "+++"

class Tabed1(FormPanel):
  def __init__(self, model):
    FormPanel.__init__(self,gvsig.getResource(__file__,"testJtree.xml"))
    self.jtreePanel.setModel(model)
    self.exp = ""
  def btnState_click(self,*args):
    self.exp = getExpansionState(self.jtreePanel)
    print self.exp

  def btnLoad_click(self,*args):
    setExpansionState(self.jtreePanel, self.exp)
    #self.jtreePanel.revalidate()
    #self.jtreePanel.repaint()
  def btnCollapse_click(self, *args):
    root =self.jtreePanel.getModel().getRoot()
    collapseAll(self.jtreePanel, TreePath(root))
  def btnSetState_click(self,*args):
    #self.jtreePanel.getModel().reload()
    exp = getExpansionState(self.jtreePanel)
    print "## Exp state:", exp
    model = createNewModel()
    self.jtreePanel.setModel(model)
    print "## Set Expansion state:", exp
    #collapseAll(self.jtreePanel, TreePath(self.jtreePanel.getModel().getRoot()))
    #self.jtreePanel.getModel().reload()
    setExpansionState(self.jtreePanel, exp)
    self.jtreePanel.revalidate()
    self.jtreePanel.repaint()
    
def main(*args):
  model = createNewModel()
  jtree = JTree(model)
  l = Tabed1(model)
  l.showTool("JTREE")
  
def createNewModel():
  root = DefaultMutableTreeNode("Root")
  vegetableNode = DefaultMutableTreeNode("Vegetables")
  vegetableNode.add(DefaultMutableTreeNode("Capsicum"))
  vegetableNode.add(DefaultMutableTreeNode("Carrot"))
  vegetableNode.add(DefaultMutableTreeNode("Tomato"))
  fruitNode = DefaultMutableTreeNode("Fruits")
  fruitNode.add(DefaultMutableTreeNode("Grapes"))
  fruitNode.add(DefaultMutableTreeNode("Orange"))
  color = DefaultMutableTreeNode("Colors")
  color.add(DefaultMutableTreeNode("Orange"))
  color.add(DefaultMutableTreeNode("Red"))
  fruitNode.add(color)
  root.add(vegetableNode)
  root.add(fruitNode)
  #printNode(root)
  model = DefaultTreeModel(root)
  return model

