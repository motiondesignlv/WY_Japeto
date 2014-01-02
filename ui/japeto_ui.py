'''
japeto UI classes 
'''
import fields 
reload(fields)

#PyQt modules
from PyQt4 import QtGui
from PyQt4 import QtCore

#python modules
import sys
import os

#Japeto modules
from japeto.mlRig import ml_graph, ml_node
from japeto import components
from japeto import templates
from japeto.templates import rig
from japeto.components import component

#import maya modules
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import OpenMayaUI

#sip module
import sip

def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)


class FileListModel(QtCore.QAbstractListModel):
    __dirPath__ = components.__path__[0]
    
    def __init__(self, parent = None):
        super(FileListModel, self).__init__(parent)
        
        self._data = self._getFiles()
        
    def headerData(self):
        return 'Components'
    
    def rowCount(self, parent):
        return len(self._data)
    
    def data(self,index, role = QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return self._data[index.row()] 
            
        return QtCore.QVariant()
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
    
    def _getFiles(self):
        '''
        List all the files in the given directory for this model. (__dirPath__)
        '''
        nullFiles = ['__init__.py', 'puppet.py', 'component.py']
        files = os.listdir(FileListModel.__dirPath__)
        fileList = list()
        for file in files:
            if file not in nullFiles and '.pyc' not in file:
                if '.py' in file and file not in fileList:
                    fileList.append(file.split('.')[0])
                #end if
            
        #end loop
        return fileList

        
class LayerGraphModel(QtCore.QAbstractItemModel):
    NodeRole = QtCore.Qt.UserRole
    def __init__(self, graph, parent = None):
        super(LayerGraphModel, self).__init__(parent)

        self._rootNode = ml_node.MlNode('root')
        children = graph.rootNodes()
        #children.reverse()
        self._rootNode.addChildren(children)
    
    def itemFromIndex( self, index ):
        return index.data(self.NodeRole).toPyObject() if index.isValid() else self._rootNode
    
    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
            
        return parentNode.childCount()
    
    def columnCount(self, parent):
        return 1
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.name()
        elif role == self.NodeRole:
            return node
    
    def headerData(self, section, orientation, role):
        return "Outliner"
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
    
    def parent(self, index):
        """
        @param index: Index of the node on the graph you want to get the parent
        @type index: *QModelIndex* 
        """
        node = index.internalPointer()
        parentNode = node.parent()
        
        
        if not parentNode:
            parentNode = self._rootNode
            
        #if parent is root, return QModelIndex
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        
        #if parent isn't root node, we wrap it up in a QModel index by
        #using internal method.
        return self.createIndex(parentNode.index(), 0, parentNode)
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(str(value.toString()))
                
                return True
            
        return QtCore.QVariant()
    
    def index(self, row, column,parent = QtCore.QModelIndex()):
        """
        @param row: Row index of the child node.
        @type index: *int* 
        
        @param column: Column index of the child node.
        @type column: *int* 
        
        @param parent: Parent of the child we are looking for.
        @type parent: *QModelIndex*
        
        
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        try:
            childItem = parentNode.childAtIndex(index = row)
    
            if childItem:
                return self.createIndex(row, column, childItem)
        except:
            return QtCore.QModelIndex()
        
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    def supportedDropActions( self ):
        '''Items can be moved and copied (but we only provide an interface 
        or moving items in this example.'''
        return QtCore.Qt.MoveAction #| QtCore.Qt.CopyAction

    def insertRows(self, row, count,
                   parent = QtCore.QModelIndex(),
                   node = None):
        '''
        Insert rows at given row index
        '''
        self.beginInsertRows(parent, row, row + count - 1)
        if node:
            if not parent.isValid():
                parentNode = self._rootNode
            else:
                parentNode = parent.internalPointer()
            
            parentNode.addChild(node, row)
            
        self.endInsertRows()
        
        return True

    def removeRows( self, row, count, parentIndex ):
        '''Remove a number of rows from the model at the given row and parent.'''
        self.beginRemoveRows( parentIndex, row, row+count-1 )
        self.endRemoveRows()
        return True

    def mimeTypes(self):
        return [ "application/x-MlNodes" ]

    def mimeData(self, indices):
        mimeData = QtCore.QMimeData()
        encodedData = QtCore.QByteArray()
        stream = QtCore.QDataStream(encodedData, QtCore.QIODevice.WriteOnly)

        for index in indices:
            if not index.isValid():
                continue
            node = index.internalPointer()
        
            variant = QtCore.QVariant(node.name())
        
            # add all the items into the stream
            stream << variant
        
        #print "Encoding drag with: ", "application/x-MlNodes" < --- for testing
        mimeData.setData("application/x-MlNodes", encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
    
        if action == QtCore.Qt.MoveAction:
            #print "Moving" <-- for testing 
            pass
        
        # Where are we inserting?
        beginRow = 0
        if row != -1:
            #print """ROW IS NOT -1, meaning inserting inbetween,
            #       above or below an existing node""" <-- for testing
            beginRow = row
        elif parent.isValid():
            print """PARENT IS VALID, inserting ONTO something since row was not -1, 
                    beginRow becomes 0 because we want to insert it at the begining
                    of this parents children"""
            parentNode = parent.internalPointer()
            beginRow = parentNode.childCount()
        else:
            print """PARENT IS INVALID, inserting to root, can change to 0 if you want 
                    it to appear at the top"""
            beginRow = self.rowCount(QtCore.QModelIndex())
        
        # create a read only stream to read back packed data from our QMimeData
        encodedData = data.data("application/x-MlNodes")
        
        stream = QtCore.QDataStream(encodedData, QtCore.QIODevice.ReadOnly)
    
        # decode all our data back into dropList
        dropList = []
        numDrop = 0
        
        while not stream.atEnd():
            variant = QtCore.QVariant()
            stream >> variant # extract
            name = variant
            node = None
            
            for node in self._rootNode.descendants():
                if name == node.name():
                    node = node 
                    break
                
            if not node:
                break
            
            # add the python object that was wrapped up by a QVariant back
            #in our mimeData method
            dropList.append( node ) 
            
            # number of items to insert later
            numDrop += 1
        
            # This will insert new items, so you have to either update the
            #values after the insertion or write your own method to receive
            #our decoded dropList objects.
            self.insertRows(beginRow, numDrop, parent, node)

        return True
    
class FileView(QtGui.QListView):
    def __init__(self, parent = None):
        super(FileView, self).__init__(parent)
        
        self.setAlternatingRowColors(True)
        self._model = FileListModel()
        self.setModel(self._model)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.setDragEnabled(True)
        

class CentralTabWidget(QtGui.QTabWidget):
    def __init__(self, graph, parent = None):
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
        #self._setupTreeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        #self._setupTreeView.setDragDropMode(QtGui.QAbstractItemView.InternalMove) 
        self._setupTreeView.setDragEnabled( True )
        self._setupTreeView.setAcceptDrops( True )
        
        #file view
        self._fileView = FileView()
        
        #fields
        self._setupAttrsLayout = QtGui.QVBoxLayout()
        #test = fields.IntField('Test1')
        #self._setupAttrsLayout.addWidget(test)
        
        #buttons
        #setupButtonLayout = QtGui.QHBoxLayout()
        self._addFileButton = QtGui.QPushButton('-Add->')
        self._setupSelectedButton  = QtGui.QPushButton('Run Selected')
        self._setupButton  = QtGui.QPushButton('Run All')
        #setupButtonLayout.addWidget(self._setupSelectedButton)
        #setupButtonLayout.addWidget(self._setupButton)
        
        #self._setupButton.clicked.connect(self._runSetupButton)
        #self._setupSelectedButton.clicked.connect(self._runSelectedSetupButton)
        self._addFileButton.clicked.connect(self._addComponentToGraph)
        
        #bring it all together
        self._setupWidgetLayout.addWidget(self._fileView, 1,0)
        self._setupWidgetLayout.addWidget(self._setupTreeFilter, 0,2)
        self._setupWidgetLayout.addWidget(self._addFileButton, 1,1)
        self._setupWidgetLayout.addWidget(self._setupTreeView, 1,2)
        #self._setupWidgetLayout.addLayout(setupButtonLayout, 2,2)
        self._setupWidgetLayout.addLayout(self._setupAttrsLayout, 1,3)
        setupWidget.setLayout(self._setupWidgetLayout)
        
        #-------------------------------------------------
        #MODEL AND PROXY MODEL
        #-------------------------------------------------
        #setup proxy model
        self._proxyModel = QtGui.QSortFilterProxyModel()
        #model for scenegraph
        self._model = LayerGraphModel(self._graph)
        
        #hook proxy model to scenegraph model
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        '''
        QtCore.QObject.connect(self._treeFilter,
                               QtCore.SIGNAL("textChanged(QString)"),
                               self._proxyModel.setFilterRegExp)
        '''
        QtCore.QObject.connect(self._setupTreeFilter,
                               QtCore.SIGNAL("textChanged(QString)"),
                               self._proxyModel.setFilterRegExp)
        
        #self._treeView.setModel(self._proxyModel)
        self._setupTreeView.setModel(self._proxyModel)
        
        self.addTab(setupWidget, 'Setup')
        '''
        self.addTab(buildWidget, 'Build')
        '''
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
            #.. todo: this is hacky
            if attr.name == 'fingers':
                attrDict[attr.name()] = eval(attr.value())
                continue
            
            attrDict[attr.name()] = attr.value()
            
        node.initialize(**attrDict)

    def _executeSelectedNode(self):
        '''
        Runs the selected item in the setup view
        '''
        node = self._selectedNode()
        
        if node:
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
            
    def _addComponentToGraph(self):
        '''
        Adds selected component from the file view
        '''
        index = self._fileView.currentIndex()
        
        model = self._fileView.model()
        nodeName = model.data(index)
        
        if nodeName in model._data:
            rootNode = self._model._rootNode
            cmd = 'import japeto.components.%s as %s' % (nodeName, nodeName)
            exec(cmd)
            newNodeCmd = '%s.%s' % (nodeName, nodeName.title())
            newNode = eval(newNodeCmd)
            newNode = newNode('c_%s' % str(nodeName))
            newNode.initialize()
            self._model.insertRows(rootNode.childCount(), 1,
                                   parent = QtCore.QModelIndex(),
                                   node = newNode)
            
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
            node.parent().removeChild(node)
            self._model.endRemoveRows()
            del node
        
    def _populateSetupAttrsLayout(self, index):
        '''
        Populates the attributes for the given node
        
        :param index: QModelIndex of the node you want to get attibutes for
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
            elif attr.attrType() == "str" or attr.attrType() == "list":
                field = fields.LineEditField(attr.name(), value = str(attr.value()), attribute = attr)
            elif attr.attrType() == "bool":
                field = fields.BooleanField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "int":
                field = fields.IntField(attr.name(), value = attr.value(), attribute = attr)
            elif attr.attrType() == "float":
                field = fields.IntField(attr.name(), value = attr.value(), attribute = attr)
            
            #add the field to the layout
            self._setupAttrsLayout.addWidget(field)
        #add stretch to push all item up
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
    
class InheritTemplateDialog(QtGui.QDialog):
    '''
    Dialog used for loading graphs or templates that have been saved or written
    '''
    def __init__(self, parent = None):
        super(InheritTemplateDialog, self).__init__(parent)
        self.parentTemplate = None
        
        layout = QtGui.QVBoxLayout()
        buttonLayout = QtGui.QHBoxLayout()
        self.okButton = QtGui.QPushButton('Ok')
        self.closeButton = QtGui.QPushButton('Close')
        
        
        self.closeButton.clicked.connect(self._close)
        self.okButton.clicked.connect(self._getChosenTemplate)
        
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(self._getTemplates())
        
        self.templateNameLineEdit = fields.LineEditField('New Template Name')
        
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.closeButton)
        layout.addWidget(self.templateNameLineEdit)
        layout.addWidget(self.comboBox)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def _getTemplates(self):
        '''
        Get all the templates on disk
        '''
        nullFiles = ['__init__.py']
        files = os.listdir(templates.__path__[0])
        fileList = list()
        for file in files:
            if file not in nullFiles and '.pyc' not in file:
                if '.py' in file and file not in fileList:
                    fileList.append(file.split('.')[0])
                #end if
            
        #end loop
        return fileList
    
    def _close(self):
        '''
        Closes to the dialog
        '''
        self.close()
        
    def _getChosenTemplate(self):
        '''
        Assigns the chosen template to the template attribute on this dialog
        '''
        self.parentTemplate = self.comboBox.currentText()
        self.close()


class LoadTemplateDialog(QtGui.QDialog):
    '''
    Dialog used for loading graphs or templates that have been saved or written
    '''
    def __init__(self, parent = None):
        super(LoadTemplateDialog, self).__init__(parent)
        self.template = None
        
        layout = QtGui.QVBoxLayout()
        buttonLayout = QtGui.QHBoxLayout()
        self.okButton = QtGui.QPushButton('Ok')
        self.closeButton = QtGui.QPushButton('Close')
        
        
        self.closeButton.clicked.connect(self._close)
        self.okButton.clicked.connect(self._getChosenTemplate)
        
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(self._getTemplates())
        
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.closeButton)
        layout.addWidget(self.comboBox)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def _getTemplates(self):
        '''
        Get all the templates on disk
        '''
        nullFiles = ['__init__.py']
        files = os.listdir(templates.__path__[0])
        fileList = list()
        for file in files:
            if file not in nullFiles and '.pyc' not in file:
                if '.py' in file and file not in fileList:
                    fileList.append(file.split('.')[0])
                #end if
            
        #end loop
        return fileList
    
    def _close(self):
        '''
        Closes to the dialog
        '''
        self.close()
        
    def _getChosenTemplate(self):
        '''
        Assigns the chosen template to the template attribute on this dialog
        '''
        self.template = self.comboBox.currentText()
        self.close()

class SaveTemplateDialog(QtGui.QFileDialog):
    '''
    This is the dialog used for saving our graphs/templates
    '''
    __caption__ = 'Save Template'
    __filter__  = '*.py'
    
    def __init__(self, parent = None, directory = str()):
        super(SaveTemplateDialog, self).__init__(parent, self.__caption__, directory, self.__filter__)
        
        self.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        self.setDefaultSuffix('.py')
        self._fileName = str()
        
    def show(self):
        '''
        Shows the fileDialog and sets the _fileName attribute from the user input 
        '''
        #Bring up the file dialog box and return the file that is being saved if any
        fileName = str(self.getSaveFileName(parent = self.parent(), caption = self.__caption__, directory = str(self.directory().absolutePath()), filter = self.__filter__))
        
        #if no file name we will exit the function
        if not fileName:
            return False
        
        #seperate the fileName from the extension so we can attach the proper extension
        fileName, fileExt = os.path.splitext(fileName)

        #make sure the file hase the extension
        self._fileName = '%s%s' % (fileName, self.defaultSuffix())
        
        return True
        
    def saveFile(self, data):
        '''
        Saves the file specified through the dialog writing the data passed in.
        This is used by for writing the graph/template in the JapetoWindow
        
        :see: JapetoWindow._saveTemplate
        
        :param data: Data/graph/template to be written to the file
        :type data: str        
        '''
        if not self._fileName:
            raise RuntimeError("No file path specified")
        '''
        if not isinstance(data, str):
            raise TypeError("Data passed in must be passed as a string")
        '''
        print "Saving %s" % self._fileName

        #write the data to the file
        rig.Rig.saveTemplate(data, self._fileName)

class JapetoWindow(QtGui.QMainWindow):
    def __init__(self, graph, parent = None):
        '''
        This is the main window used for the Japeto rigging system
        
        :param graph: The graph which the ui will use for the setup view
        :type graph: ml_graph.MlGraph
        
        :param parent: The parent for the ui
        :type parent: QtGui.QWidget
        '''
        super(JapetoWindow, self).__init__(parent)
        #load in the style sheet
        f = open(os.path.join(os.path.dirname(__file__),'japeto_styleSheet.qss'), 'r')
        styleData = f.read()
        self.setStyleSheet(styleData)
        f.close()
        
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
        
    def _loadTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.loadTemplateDialog = LoadTemplateDialog(self)
        self.loadTemplateDialog.show()

        self.loadTemplateDialog.finished.connect(self.setTemplate)
    
    def _newTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.inheritTemplateDialog = InheritTemplateDialog(self)
        self.inheritTemplateDialog.show()

        self.inheritTemplateDialog.finished.connect(self.setNewTemplate)
    
    def _saveTemplate(self):
        '''
        Load all the templates into the dialog
        '''
        self.saveTemplateDialog = SaveTemplateDialog(self)
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
        if parentTemplate and templateName:
            tabWidget = self.centralWidget()
            cmd = 'import japeto.templates.%s as %s' % (parentTemplate, parentTemplate)
            exec(cmd)
            print templateName.capitalize(),templateName, '%s.%s' % (parentTemplate,parentTemplate.capitalize())
            tabWidget._graph = rig.Rig.createTemplate(templateName.capitalize(),
                                                      templateName,
                                                      eval('%s.%s' % (parentTemplate,parentTemplate.capitalize()))) 
            tabWidget._graph.initialize()
            tabWidget._model = LayerGraphModel(tabWidget._graph)
            tabWidget._proxyModel.setSourceModel(tabWidget._model)
            tabWidget._setupTreeView.setModel(tabWidget._proxyModel)
    
    def setTemplate(self, *args):
        '''
        sets the template to the template chosen in the templateDialog
        '''
        #get the template chosen
        template = str(self.loadTemplateDialog.template)
        
        #import the file and initialize
        if template:
            tabWidget = self.centralWidget()            
            cmd = 'import japeto.templates.%s as %s' % (template, template)
            exec(cmd)
            newNodeCmd = '%s.%s("%s")' % (template, template.title(), template)
            tabWidget._graph = eval(newNodeCmd)
            tabWidget._graph.initialize()
            tabWidget._model = LayerGraphModel(tabWidget._graph)
            tabWidget._proxyModel.setSourceModel(tabWidget._model)
            tabWidget._setupTreeView.setModel(tabWidget._proxyModel)
