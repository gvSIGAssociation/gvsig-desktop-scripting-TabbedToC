# encoding: utf-8

import gvsig
from org.gvsig.tools import ToolsLocator
from org.gvsig.app.project.documents.view.toc import TocItemLeaf
from java.awt.event import ActionListener
from javax.swing import JMenuItem

from org.gvsig.app.project.documents.view import IContextMenuActionWithIcon

from javax.swing import JPopupMenu

class MenuItem(JMenuItem, ActionListener):
    def __init__(self, action, layer, tocItem):
        self.action = action
        self.layer = layer
        self.tocItem = tocItem
        self.addActionListener(self)
        self.setText(self.action.getText())
        if isinstance(self.action, IContextMenuActionWithIcon):
            self.setIcon(self.action.getIcon())
            
    def actionPerformed(self, event):
        self.action.execute(self.tocItem,(self.layer,))
        

def main(*args):
    menu = JPopupMenu()
    ep = ToolsLocator.getExtensionPointManager().get("View_TocActions")
    layer = gvsig.currentLayer()
    tocItem = TocItemLeaf(None, layer.getName(),layer.getShapeType())
    for x in ep.iterator():
        action = x.create()
        print "action", action
        continue
        if action.isVisible(tocItem, (layer,)):
            print action
            menu.add(MenuItem(action, layer,tocItem))
        else:
            print "*** else:", action
    #menu.show(None,100,100)