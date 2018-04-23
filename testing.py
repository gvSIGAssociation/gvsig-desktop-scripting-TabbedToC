# encoding: utf-8

import gvsig

from java.util import HashMap
from javax.swing.tree import TreePath
from org.apache.commons.lang import Utils
from java.awt import Dimension
from javax.swing import JComponent
from java.awt import BorderLayout

class ItemsExpandeds:
    itemsExpanded = HashMap()
    expandingNodes = False
  
    def isMarked(self, item):
        key = item.getLabel()
        isItemExpanded = Utils.isTrue(self.itemsExpanded.get(key))
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


      
class TOC(JComponent):
  serialVersionUID = 5689047685537359038L
  #logger = LoggerFactory.getLogger(TOC)
  mapContext = None
  m_Tree = None
  m_TreeModel = None
  m_Root = None
  m_TocRenderer = None
  m_Scroller = None
  itemsExpandeds = ItemsExpandeds()
  nodeSelectionListener = None
  def __init__(self):
    self.setName("TOC")
    self.setLayout(BorderLayout())
  
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
    nodeSelectionListener = NodeSelectionListener(self.m_Tree)
    self.m_Tree.addMouseListener(nodeSelectionListener)
    class ComponentListener:
      def componentResized(e):
        self.tocResized()
      def componentMoved(e):
        pass
      def componentShown(e):
        pass
      def componentHidden(e):
        pass
    self.addComponentListener(cp)
    
    class ITocOrderListener:
      def orderChanged(oldPos, newPos, layers):
        try:
          layers.moveTo(oldPos, newPos)
        except:
          pass #logger.warn("Can't change order of layers in TOC", e);
        mapContext.invalidate()

      def parentChanged(source, targer, layer):
        try:
            source.move(layer, targer)
        except:
            pass #logger.warn("Can't move layers in TOC", e);
        mapContext.invalidate()
  
    self.m_Tree.addOrderListener(ITocOrderListener())

  
    class TreeExpansionListener:
      def treeCollapsed(event):
        path = event.getPath()
        node = path.getLastPathComponent()
        if  instanceof(node.getUserObject(), ITocItem):
            itemsExpandeds.setMark(node.getUserObject(), False)
      def treeExpanded(event):
        path = event.getPath();
        node = path.getLastPathComponent()
        if instanceof(node.getUserObject(),ITocItem):
          itemsExpandeds.setMark(node.getUserObject(), True)
    m_Tree.addTreeExpansionListener(new TreeExpansionListener() 
    m_Tree.setRowHeight(0)#; // Para que lo determine el renderer

    m_Scroller = JScrollPane(m_Tree)
    m_Scroller.setBorder(BorderFactory.createEmptyBorder())

    self.add(m_Scroller)

    def setMapContext(self,mc):
      self.mapContext = mc
      class AtomicEventListener:
        def atomicEvent(e):
          #if not SwingUtilities.isEventDispatchThread():
          #    SwingUtilities.invokeLater(Runnable() {
          #        @Override
          #        public void run() {
          #            atomicEvent(e);
          #        }
          #    });
          #    return;
          #}
          if (len(e.getLayerCollectionEvents()) > 0) or (len(e.getLegendEvents()) > 0):
            self.reloadLayers()
          if len(e.getLayerEvents()) > 0:
            self.repaint()
          if len(e.getExtentEvents()) > 0:
            self.repaint()
          events = e.getLayerCollectionEvents()
          for i in range(0, len(events)):#(int i = 0; i < events.length; i++) {
            if events[i].getEventType() == LayerCollectionEvent.LAYER_ADDED):
              if PluginServices.getMainFrame() != None:
                PluginServices.getMainFrame().enableControls()
            #// Change visibility of layer before adding, according to app preferences
            if events[i].getEventType() == LayerCollectionEvent.LAYER_ADDING:
              if haveToAddNewLayersInInvisibleMode():
                events[i].getAffectedLayer().setVisible(False)

      self.mapContext.addAtomicEventListener(AtomicEventListener) 
      class LegendListener:
          def legendChanged(e):
              reloadLayers()
          def legendChanged(e):
              reloadLayers()

      self.mapContext.getLayers().addLegendListener(LegendListener())

      self.reloadLayers()

    def refresh(self):
        self.reloadLayers()
    def reloadLayers(self):
        #if not SwingUtilities.isEventDispatchThread()):
        #    SwingUtilities.invokeLater(new Runnable() {

        #        @Override
        #        public void run() {
        #            reloadLayers();
        #        }
        #    });
        #    return;
        #}
        theLayers = mapContext.getLayers()
        m_Root.removeAllChildren();
        m_Root.setAllowsChildren(True)
        reloadLayers(theLayers, m_Root)
        m_TreeModel.reload()
        itemsExpandeds.update(m_Tree, m_Root)

     def reloadLayers(self, theLayers, parentNode):

        width = m_Tree.getWidth()
        if width == 0:
            width = 300

        #// Get the tree font height
        font = m_Tree.getFont()
        metrics = self.getFontMetrics(font)
        sizeBranch =Dimension(width, metrics.getHeight() + 4)

        for i in range(0, theLayers.getLayersCount()):#(int i = theLayers.getLayersCount() - 1; i >= 0; i--) {
            lyr = theLayers.getLayer(i)
            if not lyr.isInTOC():
                continue
            elTema = TocItemBranch(lyr)
            elTema.setSize(sizeBranch)

            nodeLayer = DefaultMutableTreeNode(elTema)

            m_TreeModel.insertNodeInto(nodeLayer, parentNode, parentNode.getChildCount())
            if instanceof(lyr,LayerCollection):
                group = lyr
                self.reloadLayers(group, nodeLayer)

            elif self.haveToShowLeyendOfLayer(lyr):
                self.addLegend(nodeLayer, lyr)

     def addLegend(self,nodeLayer, lyr):
        width = m_Tree.getWidth()
        if width == 0:
            width = 300
        
        sizeLeaf = Dimension(width, 15)

        if instanceof(lyr,Classifiable):
            classifiable = lyr
            legendInfo = classifiable.getLegend()

            try:
                if instanceof(legendInfo, IClassifiedLegend):
                    cl = legendInfo
                    descriptions = cl.getDescriptions()
                    symbols = cl.getSymbols()
                    for j in range(0, len(descriptions)): # (int j = 0; j < descriptions.length; j++) {
                        itemLeaf = TocItemLeaf(symbols[j], descriptions[j], classifiable.getShapeType())
                        itemLeaf.setSize(sizeLeaf)
                        nodeValue = new DefaultMutableTreeNode(itemLeaf);
                        m_TreeModel.insertNodeInto(nodeValue, nodeLayer, nodeLayer.getChildCount())

                if instanceof(legendInfo , ISingleSymbolLegend) and legendInfo.getDefaultSymbol() != None):
                    itemLeaf = TocItemLeaf(legendInfo.getDefaultSymbol(), legendInfo.getDefaultSymbol().getDescription(), classifiable.getShapeType())
                    itemLeaf.setSize(sizeLeaf)
                    nodeValue = DefaultMutableTreeNode(itemLeaf)
                    m_TreeModel.insertNodeInto(nodeValue, nodeLayer, nodeLayer.getChildCount())

                if instanceof(legendInfo, IHasImageLegend):
                    imageLegend = legendInfo
                    #// Las imagenes de la leyenda que vienen de servicios
                    #// remotos pueden
                    #// ser lentas de pintar y relentizan todo gvSIG, asi que
                    #// mejor si
                    #// podemos hacerlo en segundo plano.
                    #thread = new Thread(new Runnable()
                    # TODO HACERLO EN OTRO THREAD
                    
                    image = imageLegend.getImageLegend()
                    
                    int w = 0
                    int h = 0
  
                    if image != None:
                        w = image.getWidth(None)
                        h = image.getHeight(None)
                                    }

                        if image != None and w > 0 and h > 0:
                            itemLeaf = TocItemLeaf()
                            itemLeaf.setImageLegend(image, "", new Dimension(w, h));
                            nodeValue = new DefaultMutableTreeNode(itemLeaf);
                            self.m_TreeModel.insertNodeInto(nodeValue, nodeLayer, nodeLayer.getChildCount());

     def tocResized(self):
        enumeration = self.m_Root.children()

        while enumeration.hasMoreElements():
            n = enumeration.nextElement()

            if instanceof(n.getUserObject(), TocItemBranch):
                item = n.getUserObject()
                szAnt = item.getSize()
                item.setSize( Dimension(self.getWidth() - 40, szAnt.height))

    def getJScrollPane(self):
        return self.m_Scroller

    def getTree(self):
        return self.m_Tree

    #/**
    # * Clase Listener que reacciona al pulsar sobre el checkbox de un nodo y
    # * crea un popupmenu al pulsar el botón derecho.
    # */
    class NodeSelectionListener(MouseAdapter, ActionListener):

        tree = None
        dlg = None
        colorChooser = None
        popmenu = None
        node = None

        /**
         * Crea un nuevo NodeSelectionListener.
         *
         * @param tree
         *            !
         */
        def __init__(self, tree):
            self.tree = tree
        def mouseClicked(self,e):
            x = e.getX()
            y = e.getY()
            row = tree.getRowForLocation(x, y)
            path = tree.getPathForRow(row)
            layers = mapContext.getLayers()
            plainListLayers = toPlainList(layers)
            plainListLayers.remove(plainListLayers.size() - 1)
            countDeepActiveLayers = countDeepActiveLayers(plainListLayers)

            if path != None:
                if e.getClickCount() == 1:
                    #// self fixes a bug when double-clicking. JTree by default
                    #// expands the tree when double-clicking, so we capture a
                    #// different node in the second click than in the first
                    node = path.getLastPathComponent()

                if node != None and instanceof(node.getUserObject(),  TocItemBranch):
                    #// double click with left button ON A BRANCH/NODE (layer)
                    if e.getClickCount() >= 2 and e.getButton() == MouseEvent.BUTTON1:
                        e.consume()
                        PluginServices.getMDIManager().setWaitCursor();
                        try :
                            leaf = node.getUserObject()
                            action = leaf.getDoubleClickAction()
                            if action != None:
                                #/*
                                # * if there is an action associated with the
                                # * double-clicked element it will be fired for
                                # * it and FOR ALL OTHER COMPATIBLES THAT HAVE
                                # * BEEN ACTIVATED.
                                # */
                                targetLayers = ArrayList()

                                owner = node.getUserObject()

                                masterLayer = owner.getLayer()
                                targetLayers.add(masterLayer)
                                actives = mapContext.getLayers().getActives()
                                for i in range(0, len(actives)): #(int i = 0; i < actives.length; i++) {
                                    if actives[i].getClass().equals(masterLayer.getClass()):
                                        if instanceof(actives[i], FLyrVect):
                                            vectorLayer = actives[i]
                                            vectorMaster = masterLayer
                                            if vectorLayer.getShapeType() == vectorMaster.getShapeType():
                                                targetLayers.add(vectorLayer)
                                                vectorLayer.setActive(True)
                                            else:
                                                vectorLayer.setActive(False)
                                        #// TODO for the rest of layer types
                                        #// (i.e. FLyrRaster)
                                    else:
                                        actives[i].setActive(False);

                                #// Do nothing if there is a non-available layer
                                for k in range(0, targetLayers.size()): #(int k = 0; k < targetLayers.size(); k++) {
                                    if not targetLayers.get(k).isAvailable():
                                        return
                                    targetLayers.get(k).setActive(True);
                                action.execute(leaf, targetLayers.toArray(FLayer[0]))
                        except:
                            NotificationManager.addError(ex);
                        finally:
                            PluginServices.getMDIManager().restoreCursor()
                        return

                    elTema = node.getUserObject()
                    lyr = elTema.getLayer()
                    iflyr.isAvailable():
                        lyr.getMapContext().beginAtomicEvent()
                    #// Si está pulsado SHIFT
                    if (e.getModifiers() and InputEvent.SHIFT_MASK) != 0 and (e.getButton() == MouseEvent.BUTTON1 or e.getButton() == MouseEvent.BUTTON3)):
                        if countDeepActiveLayers > 0:
                            self.selectInterval(plainListLayers, lyr)
                        else:
                            lyr.setActive(!lyr.isActive())

                    else: # { // Si no está pulsado SHIFT
                        #// Si no está pulsado CTRL
                        if not (e.getModifiers() and InputEvent.CTRL_MASK) != 0:
                            if e.getButton() == MouseEvent.BUTTON1:
                                if countDeepActiveLayers > 1:
                                    layers.setAllActives(False)
                                    lyr.setActive(True)
                                else:
                                     active = lyr.isActive()
                                    layers.setAllActives(False)
                                    lyr.setActive(!active)

                            if e.getButton() == MouseEvent.BUTTON3:
                                if lyr.isActive():
                                    pass
                                    #// No modificamos la selección porque lo que
                                    #// se va a hacer más abajo es abrir el menú
                                    #// contextual
                                else:
                                     active = lyr.isActive()
                                    layers.setAllActives(False)
                                    lyr.setActive(!active)
                        else: # // Si sí está pulsado CTRL
                            if e.getButton() == MouseEvent.BUTTON1:
                                #// BUTTON1 cambiamos la activación de la lyr
                                #// seleccionada
                                lyr.setActive(!lyr.isActive())
                            if e.getButton() == MouseEvent.BUTTON3:
                                if lyr.isActive():
                                    #// No modificamos la selección porque lo que
                                    #// se va a hacer más abajo es abrir el menú
                                    #// contextual
                                else:
                                    lyr.setActive(True)

                    layerNodeLocation = tree.getUI().getPathBounds(tree, path).getLocation()

                    #// Rectángulo que representa el checkbox
                    checkBoxBounds = m_TocRenderer.getCheckBoxBounds()
                    checkBoxBounds.translate(layerNodeLocation.getX(), layerNodeLocation.getY())

                    if checkBoxBounds.contains(e.getPoint()):
                        self.updateVisible(lyr)
                        #// si node no tiene leyenda llamar a addLegend

                    if e.getButton() == MouseEvent.BUTTON3:
                        popmenu = new FPopupMenu(mapContext, node);
                        tree.add(popmenu);
                        popmenu.show(e.getComponent(), e.getX(), e.getY())
                    if lyr.isAvailable():
                        lyr.getMapContext().endAtomicEvent()

                if node != None and instanceof(node.getUserObject(),  TocItemLeaf):
                    owner = node.getParent()).getUserObject()
                    masterLayer = owner.getLayer()

                    #// double click with left button ON A LEAF (ISymbol)
                    if e.getClickCount() >= 2 and e.getButton() == MouseEvent.BUTTON1:
                        e.consume()

                        PluginServices.getMDIManager().setWaitCursor();
                        try:
                            leaf = node.getUserObject()
                            action = leaf.getDoubleClickAction()
                            if action != None:
                                #/*
                                # * if there is an action associated with the
                                # * double-clicked element it will be fired for
                                # * it and FOR ALL OTHER COMPATIBLES THAT HAVE
                                # * BEEN ACTIVATED.
                                # */
                                #/*
                                # * #3035: Symbology is applied to active layers
                                # * too
                                # * Now it will be done only on the
                                # * double-clicked one
                                # */
                                action.execute(leaf, masterLaye)
                        except Exception as ex:
                            logger.warn("Problems executing action in the ToC.", ex)
                        finally:
                            PluginServices.getMDIManager().restoreCursor();
                        return
                tree.getModel()).nodeChanged(node)
                if row == 0:
                    tree.revalidate()
                    tree.repaint()

                #// FIXME Is it really necessary?
                if PluginServices.getMainFrame() != None:
                  PluginServices.getMainFrame().enableControls();
                else:
                  if e.getButton() == MouseEvent.BUTTON3:
                      popmenu = FPopupMenu(mapContext, None)
                      tree.add(popmenu)
                      popmenu.show(e.getComponent(), e.getX(), e.getY())


         def selectInterval(self, layers,  lyr):
            #// FLayer[] activeLayers = layers.getActives();
            firstActive = Integer.MAX_VALUE
            lastActive = -1
            myLayer = -1

            for j in range(0, layers.size()): #(int j = 0; j < layers.size(); j++) {
                layerAux = layers.get(j)
                if layerAux.isActive():
                    if firstActive > j:
                        firstActive = j
                    
                    if lastActive < j:
                        lastActive = j
                    
                    if layerAux.equals(lyr):
                        myLayer = j
                    
                
                if myLayer < 0 and layerAux.equals(lyr):
                    myLayer = j;


            if firstActive < Integer.MAX_VALUE and myLayer >= 0:
                for pasada in range(0, 2): #(int pasada = 0; pasada < 2; pasada++) {
                    if myLayer < firstActive:
                        for j in range(0, myLayer): # (int j = 0; j < myLayer; j++) {
                            layerAux = layers.get(j)
                            if pasada == 0:
                                if instanceof(layerAux, FLayers):
                                    layerAux.setActive(False)
                            else:
                                if not instanceof(layerAux, FLayers):
                                    layerAux.setActive(False)
                        for ~j in range(0, lastActive): #(int j = myLayer; j <= lastActive; j++) {
                            layerAux = layers.get(j)
                            if pasada == 0:
                                if instanceof(layerAux, FLayers):
                                    layerAux.setActive(True)
                            else {
                                if not instanceof(layerAux,  FLayers):
                                    layerAux.setActive(True)

                        for j in range( lastActive + 1, layers.size()): #(int j = lastActive + 1; j < layers.size(); j++) {
                            layerAux = layers.get(j)
                            if pasada == 0:
                                if instanceof(layerAux,  FLayers):
                                    layerAux.setActive(False)
                            else:
                                if not instanceof(layerAux  FLayers):
                                    layerAux.setActive(False)
                    else:
                        if myLayer > lastActive:
                            for j in range(0, firstActive): # (int j = 0; j < firstActive; j++) {
                                layerAux = layers.get(j)
                                if pasada == 0:
                                    if instanceof(layerAux , FLayers):
                                        layerAux.setActive(False)
                                else:
                                    if not instanceof(layerAux,  FLayers):
                                        layerAux.setActive(False)
                            for j in range(firstActive,myLayer):  #(int j = firstActive; j <= myLayer; j++) {
                                layerAux = layers.get(j)
                                if pasada == 0:
                                    if instanceof(layerAux, FLayers):
                                        layerAux.setActive(True)
                                else:
                                    if not instanceof(layerAux, FLayers):
                                        layerAux.setActive(True)
                            for j in range(myLayer + 1,layers.size()): #(int j = myLayer + 1; j < layers.size(); j++) {
                                layerAux = layers.get(j)
                                if pasada == 0:
                                    if instanceof(layerAux, FLayers):
                                        layerAux.setActive(False)
                                else:
                                    if not instanceof(layerAux, FLayers):
                                        layerAux.setActive(False)
                        else: #{ // Si myLayer está entre firstActive y lastActive
                                 #// seleccionamos desde myLayer hasta lastLayer
                            for j in range(0, myLayer): #(int j = 0; j < myLayer; j++) {
                                layerAux = layers.get(j)
                                if pasada == 0:
                                    if instanceof(layerAux,  FLayers):
                                        layerAux.setActive(False)
                                else:
                                    if not instanceof(layerAux, FLayers):
                                        layerAux.setActive(False)
                            for j in range(myLayer, lastActive): #(int j = myLayer; j <= lastActive; j++) {
                                layerAux = layers.get(j)
                                if pasada == 0:
                                    if instanceof(layerAux, FLayers):
                                        layerAux.setActive(True)
                                else:
                                    if not instanceof(layerAux, FLayers):
                                        layerAux.setActive(True)
                            for j in range(lastActive+1, layers.size()): # (int j = lastActive + 1; j < layers.size(); j++) {
                                layerAux = layers.get(j)
                                if pasada == 0:
                                    if instanceof(layerAux, FLayers):
                                        layerAux.setActive(False)
                                else:
                                    if not instanceof(layerAux, FLayers):
                                        layerAux.setActive(False)

         def toPlainList(self, layer):
            return toPlainList(layer, ArrayList) #new ArrayList<FLayer>())

         def toPlainList(self,layer, result):
            if instanceof(layer, FLayers):
                layerGroup = layer
                for i in range(0, layerGroup.getLayersCount()): #(int i = 0; i < layerGroup.getLayersCount(); i++) {
                    toPlainList(layerGroup.getLayer(i), result)
            result.add(layer)
            return result

         def countDeepActiveLayers(self,layers):
            count = 0
            for fLayer in layers: #(FLayer fLayer : layers) {
                if fLayer.isActive()
                    count += 1
            return count

         #/**
         # * Actualiza la visibilidad de la capas.
         # *
         # * @param lyr
         # *            Capa sobre la que se está clickando.
         # */
         def updateVisible(self,lyr):
            if lyr.isAvailable():
                lyr.setVisible(not lyr.visibleRequired())
                self.updateVisibleChild(lyr)
                self.updateVisibleParent(lyr)
                if node != None and not instanceof(lyr, FLayers):
                    if self.haveToShowLeyendOfLayer(lyr):
                        if node.getChildCount() == 0:
                            self.addLegend(node, lyr)
                    else:
                        self.node.removeAllChildren()
                        m_TreeModel.reload(node)
         #/**
         #* Actualiza de forma recursiva la visibilidad de los hijos de la capa
         #* que se pasa como parámetro.
         #*
         #* @param lyr
         #*            Capa a actualizar.
         #*/
         def updateVisibleChild(self,lyr):
            if instanceof(lyr, FLayers):# { // Es la raiz de una rama o cualquier nodo intermedio.
                layergroup = lyr
                for i in range(0,layergroup.getLayersCount()): #(int i = 0; i < layergroup.getLayersCount(); i++) {
                    layergroup.getLayer(i).setVisible(lyr.visibleRequired())
                    self.updateVisibleChild(layergroup.getLayer(i))

         #/**
         #* Actualiza de forma recursiva la visibilidad del padre de la capa que
         #* se pasa como parámetro.
         #*
         #* @param lyr
         #*            Capa a actualizar.
         #*/
         def updateVisibleParent(self,lyr):
            parent = lyr.getParentLayer()
            if parent != None:
                 parentVisible = False
                for i in range(0,parent.getLayersCount()) : # (int i = 0; i < parent.getLayersCount(); i++) {
                    if (parent.getLayer(i).visibleRequired()):
                        parentVisible = True;

                parent.setVisible(parentVisible)
                self.updateVisibleParent(parent)

 
        def mouseReleased(arg0):
            super.mouseReleased(arg0)

        def mouseEntered(MouseEvent arg0)
            super.mouseEntered(arg0)

      def haveToAddNewLayersInInvisibleMode(self)
        ProjectPreferences projectPreferences = ApplicationLocator.getProjectManager().getProjectPreferences()

        return projectPreferences.getAddNewLayersInInvisibleMode()
        
      def haveToShowLeyendOfLayer(self,layer):
        ProjectPreferences projectPreferences = ApplicationLocator.getProjectManager().getProjectPreferences()
        return !(!layer.isVisible() and  projectPreferences.getHideLegendInToCOfNonVisibleLayers())

    }

}








def main(*args):

    print TOC()
