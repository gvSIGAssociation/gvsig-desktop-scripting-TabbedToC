# encoding: utf-8

import gvsig
from sourceorder import expandAllNodes
from javax.swing.tree import DefaultMutableTreeNode
from javax.swing.tree import DefaultTreeModel
from org.gvsig.app.project.documents.view.toc import TocItemBranch, DnDJTree
from org.gvsig.app.project.documents.view.toc.gui import TOC
from java.lang import Object
import org.gvsig.app.project.documents.view.toc.gui.TOC
from javax.swing.tree import TreeSelectionModel
from org.gvsig.app.project.documents.view.toc.gui import TOCRenderer

def setTreeAsSelectionOrder(tree, mapContext):
  selectionToc = SelectionToc()
  #model = selectionToc.createTreeModel(mapContext)
  #tree.setModel(model)
  #expandAllNodes(tree, 0, tree.getRowCount())

  #from org.gvsig.app.project.documents.view.toc.gui import TOC
  #jpl10 = TOC()
  selectionToc.setMapContext(mapContext)
  tree.add(selectionToc)

from java.util import HashMap
from javax.swing.tree import TreePath
from org.apache.commons.lang import BooleanUtils

class ItemsExpandeds:
        itemsExpanded = HashMap()
        expandingNodes = False

        def isMarked(self, item):
            key = item.getLabel()
            isItemExpanded = BooleanUtils.isTrue(self.itemsExpanded.get(key))
            return isItemExpanded

        def setMark(self, item, expanded):
            key = item.getLabel()
            self.itemsExpanded.put(key, expanded)
            
        def removeLayer(self, layer):
            key = layer.getName()
            self.itemsExpanded.remove(key)

        def update(self, tree, node):
            if self.expandingNodes:
                return
            #try:
            expandingNodes = True
            treeModel = tree.getModel()
            nodes = node.children()
            while nodes.hasMoreElements():
                curNode = nodes.nextElement()
                if curNode.getChildCount() > 0:
                    self.update(tree, curNode)
                path = TreePath(treeModel.getPathToRoot(curNode))
                item = curNode.getUserObject()
                if self.isMarked(item):
                    tree.expandPath(path)
                else:
                    tree.collapsePath(path)
            #} finally {
            #    expandingNodes = false;
            #}
from java.awt import BorderLayout
class SelectionToc(TOC):
    mapContext = None
    itemsExpandeds = ItemsExpandeds()
    """
    m_Root = None
    m_TreeModel = None
    m_Tree = None
    m_TocRenderer = None
    """
    def __init__(self):
        #TOC.__init__(self)
        self.setName("TOC")
        self.setLayout(BorderLayout())
        from java.awt import Dimension
        dd = Dimension(200,200)
        self.setPreferredSize(dd)
        self.setMinimumSize(dd)
        self.m_Root = DefaultMutableTreeNode(Object)
        self.m_TreeModel = DefaultTreeModel(self.m_Root)
        self.m_Tree = DnDJTree(self.m_TreeModel)
        self.m_TocRenderer = TOCRenderer(self.m_Tree.getBackground())
        self.m_Tree.setCellRenderer(self.m_TocRenderer)
        self.m_Tree.setRootVisible(False)
        self.m_Tree.setShowsRootHandles(True)
        self.m_Tree.getSelectionModel().setSelectionMode(TreeSelectionModel.DISCONTIGUOUS_TREE_SELECTION)

        #self.nodeSelectionListener = org.gvsig.app.project.documents.view.toc.gui.TOC.NodeSelectionListener(m_Tree)
        #self.m_Tree.addMouseListener(nodeSelectionListener)
        
        
        
    def refresh(self):
        self.reloadLayers()
        #self.createTreeModel(self.mapContext())
        
    def setMapContext(self, mapContext):
        self.mapContext = mapContext
        TOC.setMapContext(self,self.mapContext)
        return None
    """
    def reloadLayers(self):
        #TOC.reloadLayers(self)
        theLayers = self.mapContext.getLayers()
        self.m_Root.removeAllChildren()
        self.m_Root.setAllowsChildren(True)
        
        #TOC.reloadLayers(self, theLayers, self.m_Root)
        for layer in iter(self.mapContext.deepiterator()):
            elTema = TocItemBranch(layer)
            nodeLayer = DefaultMutableTreeNode(elTema)
            self.m_TreeModel.insertNodeInto(nodeLayer,self.m_Root,self.m_Root.getChildCount())
            print self.m_TreeModel
            
        self.m_TreeModel.reload()
        self.repaint()
        self.itemsExpandeds.update(self.m_Tree, self.m_Root)
        print "Done"
        
    
    def createTreeModel(self, mapContext, reducedTree=True):
        root = DefaultMutableTreeNode("Visibility")
        model = DefaultTreeModel(root)
        for layer in iter(mapContext.deepiterator()):
            t1 = TocItemBranch(layer)
            nodeLayer = DefaultMutableTreeNode(t1)
            model.insertNodeInto(nodeLayer,root,root.getChildCount())
        return model

def main(*args):

    #Remove this lines and add here your code

    print "hola mundo"
    pass
    """