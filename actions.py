# encoding: utf-8

import gvsig

from gvsig import getResource

from java.io import File
from org.gvsig.andami import PluginsLocator
from org.gvsig.app import ApplicationLocator
from org.gvsig.scripting.app.extension import ScriptingExtension
from org.gvsig.tools import ToolsLocator
from org.gvsig.tools.swing.api import ToolsSwingLocator

from org.gvsig.app.project.documents import DocumentManager
from org.gvsig.app.project.documents.view import ViewManager
from org.gvsig.tools.observer import Observer
from addons.TabbedToC.tabbedtoc import TabbedToC

class ObserverViewManager(Observer):
  def __init__(self):
    pass

  def update(self, viewManager, notification):
    if notification.getValue()==None :
      return
    if notification.getType() != DocumentManager.NOTIFY_AFTER_CREATEMAINWINDOW :
      return
    #
    # Cada vez que se crea un panel de vista nuevo, le añadimos el TabbedToC.
    viewpanel = notification.getValue()
    panel = TabbedToC()
    panel.install(viewpanel)

def selfRegister():
  projectManager = ApplicationLocator().getProjectManager()
  viewManager = projectManager.getDocumentManager(ViewManager.TYPENAME)
  observerViewManager = ObserverViewManager()
  viewManager.setProperty("TabbedTocObserver",observerViewManager)
  viewManager.addObserver(observerViewManager)
  
  #
  # Si ya hay una vista abierta le mete el TabbedToC
  view = gvsig.currentView()
  if view != None:
    viewpanel = view.getWindowOfView()
    panel = TabbedToC()
    panel.install(viewpanel)
