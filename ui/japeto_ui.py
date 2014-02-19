'''
japeto UI classes 
'''
import fields 
reload(fields)

#PyQt modules
from PyQt4 import QtGui
from PyQt4 import QtCore

#python modules
import os

#Japeto modules
from japeto.templates import rig
from japeto.components import component
from japeto.ui import widgets, models
from japeto.mlRig import ml_graph
reload(models)

#import maya modules
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import OpenMayaUI
from maya import cmds

#sip module
import sip

def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)


class CentralTabWidget(QtGui.QTabWidget):
    def __init__(self, graph = ml_graph.MlGraph('null'), parent = None):
        super(CentralTabWidget, self).__init__(parent)
        self._graph = graph
        
        #-------------------------------------------------
        #SETUP TAB
        #-------------------------------------------------
        setupWidget = QtGui.QWidget()
        self._setupWidgetLayout = QtGui.QGridLayout()
        self._setupTreeFilter = QtGui.QLineEdit()
        self._setupTreeView = QtGui.QTreeView()
        self._setupTreeView.setAlternatingRowColors(True)
        self._setupTreeView.setDragEnabled(True)
        self._setupTreeView.setAcceptDrops(True)
        
        #file view
        self._fileView = widgets.FileView()
        
        #fields
        attrsGroupBox = QtGui.QGroupBox('Attributes', self)
        attrsGroupLayout = QtGui.QVBoxLayout()
        self._setupAttrsWidget = QtGui.QWidget()
        self._setupAttrsLayout = QtGui.QVBoxLayout(self._setupAttrsWidget)
        self.attrsScrollArea = QtGui.QScrollArea()
        attrsGroupLayout.addWidget(self.attrsScrollArea)
        
        self.attrsScrollArea.setWidgetResizable(True)
        self.attrsScrollArea.setWidget(self._setupAttrsWidget)
        attrsGroupBox.setLayout(attrsGroupLayout)
        
        #buttons
        self._addFileButton = QtGui.QPushButton(QtGui.QIcon( os.path.join(os.path.dirname( __file__ ), 'icons/add.png') ),'Node')
        self._addFileButton.clicked.connect(self._addItemToGraph)
        
        #bring it all together
        self._setupWidgetLayout.addWidget(self._fileView, 1,0)
        self._setupWidgetLayout.addWidget(self._setupTreeFilter, 0,2)
        self._setupWidgetLayout.addWidget(self._addFileButton, 1,1)
        self._setupWidgetLayout.addWidget(self._setupTreeView, 1,2)
        self._setupWidgetLayout.addWidget(attrsGroupBox, 1,3)
        setupWidget.setLayout(self._setupWidgetLayout)
        
        #-------------------------------------------------
        #MODEL AND PROXY MODEL
        #-------------------------------------------------
        #setup proxy model
        self._proxyModel = QtGui.QSortFilterProxyModel()
        #model for scenegraph
        self._model = models.LayerGraphModel(self._graph)
        
        #hook proxy model to scenegraph model
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        QtCore.QObject.connect(self._setupTreeFilter,
                               QtCore.SIGNAL("textChanged(QString)"),
                               self._proxyModel.setFilterRegExp)
        
        #self._treeView.setModel(self._proxyModel)
        self._setupTreeView.setModel(self._proxyModel)
        
        self.addTab(setupWidget, 'Setup')
        self._setupTreeView.expandAll()
        
        #set selections
        if self._graph.nodes():
            self._setupTreeView.setCurrentIndex(self._model.index(0,0))
            self._populateSetupAttrsLayout(self._model.index(0,0))
        
        self._setupTreeView.clicked.connect(self._populateSetupAttrsLayout)

        #CONTEXT MENU
        self._setupTreeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self._setupTreeView, QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"), self.showCustomContextMenu)

    
    def showCustomContextMenu(self, pos):
        '''
        Show the context menu at the position of the curser
        
        :param pos: The point where the curser is on the screen
        :type pos: QtCore.QPoint
        '''
        index = self._setupTreeView.indexAt(pos)

        if not index.isValid():
            return

        node = self._model.itemFromIndex(index)
        #If node is disabled, return
        if not node.active():
            return
        
        #construct menus
        mainMenu = QtGui.QMenu(self)
        
        if isinstance(node, component.Component):
            setupMenu = QtGui.QMenu('Setup',mainMenu)
            buildMenu = QtGui.QMenu('Build',mainMenu)
            
            #setup menu actions
            runSelectedSetupAction     = setupMenu.addAction('Setup This Node')
            runFromSelectedSetupAction = setupMenu.addAction('Setup From This Node')
            runAllSetupAction          = setupMenu.addAction('Setup All')
            
            QtCore.QObject.connect(runSelectedSetupAction, QtCore.SIGNAL('triggered()'), self._runSelectedSetup)
            QtCore.QObject.connect(runFromSelectedSetupAction, QtCore.SIGNAL('triggered()'), self._runSetupFromSelected)
            QtCore.QObject.connect(runAllSetupAction, QtCore.SIGNAL('triggered()'), self._runSetupFromSelected)
            
            #build menu actions
            runSelectedBuildAction     = buildMenu.addAction('Build This Node')
            runFromSelectedBuildAction = buildMenu.addAction('Build From This Node')
            runAllBuildAction          = buildMenu.addAction('Build All')
            
            QtCore.QObject.connect(runSelectedBuildAction, QtCore.SIGNAL('triggered()'), self._runSelectedBuild)
            QtCore.QObject.connect(runFromSelectedBuildAction, QtCore.SIGNAL('triggered()'), self._runBuildFromSelected)
            QtCore.QObject.connect(runAllBuildAction, QtCore.SIGNAL('triggered()'), self._runBuildFromSelected)

            # your menu...
            #add menus to main menu
            mainMenu.addMenu(setupMenu)
            mainMenu.addMenu(buildMenu)
        else:
            executeNodeAction = mainMenu.addAction('Execute')
            QtCore.QObject.connect(executeNodeAction, QtCore.SIGNAL('triggered()'), self._executeSelectedNode)
        
        #main menu actions
        mainMenu.addSeparator()
        removeNodeAction = mainMenu.addAction('Remove Node')
        QtCore.QObject.connect(removeNodeAction, QtCore.SIGNAL('triggered()'), self._removeSelectedNode)
        
        mainMenu.popup(QtGui.QCursor.pos())

    def _initializeNode(self, node):
        attrDict = dict()
        for attr in node.attributes():
            #if fingers attribute, evaluate the attribute differently
            #.. todo: Make an attribute specifically for list in ml_attirbute.MlAttribute            
            attrDict[attr.name()] = attr.value()

        node.initialize(**attrDict)

    def _executeSelectedNode(self):
        '''
        Runs the selected item in the setup view
        '''
        node = self._selectedNode()
        attributes = dict()
        
        if node:
            attrs = node.attributes()
            if attrs:
                for attr in attrs:
                    attributes[attr.name()] = attr.value()
                
                    node.execute(**attributes)
                    return
            node.execute()
            
    def _runSetup(self):
        for rootNode in self._model._rootNode.children():
            rootNode.runSetupRig()
            for node in rootNode.descendants():
                self._initializeNode(node)
                node.runSetupRig()
                
    def _runSetupFromSelected(self):
        startNode = self._selectedNode()
        self._initializeNode(startNode)
        startNode.runSetupRig()
        for node in startNode.descendants():
            self._initializeNode(node)
            node.runSetupRig()
                    
    def _runSelectedSetup(self):
        '''
        Runs the selected item in the setup view
        '''
        node = self._selectedNode()
        
        if node:
            self._initializeNode(node)
            node.runSetupRig()
            
    def _runBuild(self):
        for rootNode in self._model._rootNode.children():
            self._initializeNode(rootNode)
            rootNode.runRig()
            for node in rootNode.descendants():
                self._initializeNode(node)
                node.runRig()
                
    def _runBuildFromSelected(self):
        startNode = self._selectedNode()
        self._initializeNode(startNode)
        startNode.runRig()
        for node in startNode.descendants():
            self._initializeNode(node)
            node.runRig()
                    
    def _runSelectedBuild(self):
        '''
        Runs the selected item in the setup view
        '''
        node = self._selectedNode()
        
        if node:
            self._initializeNode(node)
            node.runRig()
            
    def _addItemToGraph(self):
        '''
        Adds selected component from the file view
        '''
        index = self._fileView.currentIndex()
        
        if not index.isValid():
            return None
        
        model = self._fileView.model()
        node = model.itemFromIndex(index)
        nodeName = node.name()
        
        if node.active():
            if nodeName in model._graph.nodeNames():
                rootNode = self._model._rootNode
                try:
                    cmd = 'import japeto.components.%s as %s' % (nodeName, nodeName)
                    exec(cmd)
                    newNodeCmd = '%s.%s' % (nodeName, nodeName.title())
                    newNode = eval(newNodeCmd)
                    newNode = newNode('c_%s' % str(nodeName))
                    newNode.initialize()
                except:
                    cmd = 'import japeto.nodes.%s as %s' % (nodeName, nodeName)
                    exec(cmd)
                    newNodeCmd = '%s.%s' % (nodeName, nodeName.title())
                    newNode = eval(newNodeCmd)
                    newNode = newNode(str(nodeName))
                
                newNode.setColor(node.color())
                
                self._model.insertRows(rootNode.childCount(), 1,
                                       parent = QtCore.QModelIndex(),
                                       node = newNode)
        print self._graph.nodes()
            
    def _selectedNode(self):
        '''
        Returns the selected node
        '''
        index = self._setupTreeView.currentIndex()
        
        if not index.isValid():
            return None
        
        return self._model.itemFromIndex(index)
    
    
    def _removeSelectedNode(self):        
        index = self._setupTreeView.currentIndex()
        
        node = self._selectedNode()

        #self._model.removeRows(index.row(), 1, self._model)
        if node:
            self._model.beginRemoveRows( index.parent(), index.row(), index.row()+1-1 )
            self._graph.removeNode(node)
            #node.parent().removeChild(node)
            self._model.endRemoveRows()
            del node
        
    def _populateSetupAttrsLayout(self, index):
        '''
        Populates the attributes for the given node
        
        :param index: QModelIndex of the node you want to get attributes for
        :type index: QtCore.QModelIndex
        '''
        #Check if there are any items in the layout
        if self._setupAttrsLayout.count():
            self.clearLayout(self._setupAttrsLayout)

        #check to see if the index passed is valid
        if not index.isValid():
            return None
        
        #get the node
        node = self._model.itemFromIndex(index)

        #go through the attributes on the node and create appropriate field
        for attr in node.attributes():
            if attr.name() == 'position':
                field = fields.VectorField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "str":
                field = fields.LineEditField(attr.name(), value = str(attr.value()), attribute = attr)
            elif attr.attrType() == "bool":
                field = fields.BooleanField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "int":
                field = fields.IntField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "float":
                field = fields.IntField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "list":
                field = fields.ListField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "code":
                field = fields.TextEditField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "file":
                field = fields.FileBrowserField(label = attr.name(), filter = "",value = attr.value(), attribute = attr)
            elif attr.attrType() == "dir":
                field = fields.DirBrowserField(label = attr.name(), value = attr.value(), attribute = attr)
            
            #add the field to the layout
            self._setupAttrsLayout.addWidget(field)
        #add stretch to push all item up
        self.attrsScrollArea.setWidget(self._setupAttrsWidget)
        self._setupAttrsWidget.setLayout(self._setupAttrsLayout)
        self.attrsScrollArea.setWidgetResizable(True)
        self._setupAttrsLayout.addStretch()
    
    
    def clearLayout(self, layout):
        '''
        Clears a layout of any items with in the layout
        
        :param layout: Layout that you wish to clear
        :type layout: QtGui.QLayout
        '''
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
    
            if isinstance(item, QtGui.QWidgetItem):
                item.widget().close()
                # or
                # item.widget().setParent(None)
            elif isinstance(item, QtGui.QSpacerItem):
                pass
                # no need to do extra stuff
            else:
                self.clearLayout(item.layout())
    
            # remove the item from layout
            layout.removeItem(item)  
            
    def getAttrFieldValues(self):
        for i in reversed(range(self._setupAttrsLayout.count())):
            item = self._setupAttrsLayout.itemAt(i)
            if isinstance(item, QtGui.QWidgetItem):
                print item.widget().value()

    
#-------------------------------
#MAIN WINDOW
#-------------------------------
class JapetoWindow(QtGui.QMainWindow):
    def __init__(self, graph = ml_graph.MlGraph('null'), parent = None):
        '''
        This is the main window used for the Japeto rigging system
        
        :param graph: The graph which the ui will use for the setup view
        :type graph: ml_graph.MlGraph
        
        :param parent: The parent for the ui
        :type parent: QtGui.QWidget
        '''
        super(JapetoWindow, self).__init__(parent)
        #load in the style sheet
        '''
        f = open(os.path.join(os.path.dirname(__file__),'japeto_styleSheet.qss'), 'r')
        styleData = f.read()
        self.setStyleSheet(styleData)
        f.close()
        '''
        
        #set the window title and central widget
        self.setWindowTitle('Japeto Rig Build UI')
        tabWidget = CentralTabWidget(graph)
        self.setCentralWidget(tabWidget)
        
        #add menu bar to window
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        newTemplateAction = fileMenu.addAction('New Template')
        loadTemplateAction = fileMenu.addAction('Load Template')
        saveTemplateAction = fileMenu.addAction('Save Template')
        QtCore.QObject.connect(newTemplateAction, QtCore.SIGNAL('triggered()'), self._newTemplate)
        QtCore.QObject.connect(loadTemplateAction, QtCore.SIGNAL('triggered()'), self._loadTemplate)
        QtCore.QObject.connect(saveTemplateAction, QtCore.SIGNAL('triggered()'), self._saveTemplate)
        
        self.setMinimumSize(880,550)
        self.setMaximumSize(1000, 1200)
        
    def _loadTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.loadTemplateDialog = widgets.LoadTemplateDialog(self)
        self.loadTemplateDialog.show()

        self.loadTemplateDialog.finished.connect(self.setTemplate)
    
    def _newTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.inheritTemplateDialog = widgets.InheritTemplateDialog(self)
        self.inheritTemplateDialog.show()

        self.inheritTemplateDialog.finished.connect(self.setNewTemplate)
    
    def _saveTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.saveTemplateDialog = widgets.SaveTemplateDialog(self)
        result = self.saveTemplateDialog.show()
        
        if result:
            self.saveTemplateDialog.saveFile(self.centralWidget()._graph)

    def setNewTemplate(self, *args):
        '''
        sets the template to the template chosen in the templateDialog
        '''
        #get the template chosen
        parentTemplate = str(self.inheritTemplateDialog.parentTemplate)
        templateName = self.inheritTemplateDialog.templateNameLineEdit.value()
        #import the file and initialize
        if parentTemplate != 'None' and templateName:
            tabWidget = self.centralWidget()
            cmd = 'import japeto.templates.%s as %s' % (parentTemplate, parentTemplate)
            exec(cmd)
            tabWidget._graph = rig.Rig.createTemplate(templateName.capitalize(),
                                                      templateName,
                                                      eval('%s.%s' % (parentTemplate,parentTemplate.capitalize()))) 
            tabWidget._graph.initialize()
            tabWidget._model = models.LayerGraphModel(tabWidget._graph)
            tabWidget._proxyModel.setSourceModel(tabWidget._model)
            tabWidget._setupTreeView.setModel(tabWidget._proxyModel)
            tabWidget._setupTreeView.expandAll()
            
    def setTemplate(self, *args):
        '''
        sets the template to the template chosen in the templateDialog
        '''
        #get the template chosen
        template = str(self.loadTemplateDialog.template)
        templateFile = self.loadTemplateDialog.templateFile
        #import the file and initialize
        if template != 'None':
            tabWidget = self.centralWidget()
            #get data from the file
            data = dict()
            #run the data we got from file       
            execfile(templateFile, data)
            #newNodeCmd = '%s("%s")' % (template.title(), template) #<-- Construct template
            tabWidget._graph = data[template.title()](template)
            del(data) #<-- delete globals data
            tabWidget._graph.initialize()
            tabWidget._model = models.LayerGraphModel(tabWidget._graph)
            tabWidget._proxyModel.setSourceModel(tabWidget._model)
            tabWidget._setupTreeView.setModel(tabWidget._proxyModel)
            tabWidget._setupTreeView.expandAll()
