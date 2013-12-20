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

        
class LayerGraph(QtCore.QAbstractItemModel):
    NodeRole = QtCore.Qt.UserRole
    def __init__(self, graph, parent = None):
        super(LayerGraph, self).__init__(parent)

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
        
        print "Encoding drag with: ", "application/x-MlNodes"
        mimeData.setData("application/x-MlNodes", encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
    
        if action == QtCore.Qt.MoveAction:
            print "Moving"
        
        # Where are we inserting?
        beginRow = 0
        if row != -1:
            print """ROW IS NOT -1, meaning inserting inbetween,
                    above or below an existing node"""
            beginRow = row
        elif parent.isValid():
            print """PARENT IS VALID, inserting ONTO something since row was not -1, 
                    beginRow becomes 0 because we want to insert it at the begining
                    of this parents children"""
            beginRow = 0
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
        #BUILD WIDGET
        #-------------------------------------------------
        buildWidget = QtGui.QWidget()
        buildWidgetLayout = QtGui.QGridLayout()
        self._treeFilter = QtGui.QLineEdit()
        self._treeView = QtGui.QTreeView()
        self._treeView.setAlternatingRowColors(True)
        #self._contextTreeMenu
        
        #fields
        verticleLayout = QtGui.QVBoxLayout()
        self._intField = fields.IntField('Test1')
        self._intField2 = fields.IntField('Test2')
        verticleLayout.addWidget(self._intField)
        verticleLayout.addWidget(self._intField2)
        
        #bring it all together
        buildWidgetLayout.addWidget(self._treeFilter, 0,0)
        buildWidgetLayout.addWidget(self._treeView, 1,0)
        buildWidgetLayout.addLayout(verticleLayout, 1,1)
        buildWidget.setLayout(buildWidgetLayout)
        
        
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
        setupButtonLayout = QtGui.QHBoxLayout()
        self._addFileButton = QtGui.QPushButton('->')
        self._setupSelectedButton  = QtGui.QPushButton('Run Selected')
        self._setupButton  = QtGui.QPushButton('Run All')
        setupButtonLayout.addWidget(self._setupSelectedButton)
        setupButtonLayout.addWidget(self._setupButton)
        
        self._setupButton.clicked.connect(self._runSetupButton)
        self._setupSelectedButton.clicked.connect(self._runSelectedSetupButton)
        self._addFileButton.clicked.connect(self._addComponentToGraph)
        
        #bring it all together
        self._setupWidgetLayout.addWidget(self._fileView, 1,0)
        self._setupWidgetLayout.addWidget(self._setupTreeFilter, 0,2)
        self._setupWidgetLayout.addWidget(self._addFileButton, 1,1)
        self._setupWidgetLayout.addWidget(self._setupTreeView, 1,2)
        self._setupWidgetLayout.addLayout(setupButtonLayout, 2,2)
        self._setupWidgetLayout.addLayout(self._setupAttrsLayout, 1,3)
        setupWidget.setLayout(self._setupWidgetLayout)
        
        #-------------------------------------------------
        #MODEL AND PROXY MODEL
        #-------------------------------------------------
        #setup proxy model
        self._proxyModel = QtGui.QSortFilterProxyModel()
        #model for scenegraph
        self._model = LayerGraph(self._graph)
        
        #hook proxy model to scenegraph model
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        QtCore.QObject.connect(self._treeFilter,
                               QtCore.SIGNAL("textChanged(QString)"),
                               self._proxyModel.setFilterRegExp)
        QtCore.QObject.connect(self._setupTreeFilter,
                               QtCore.SIGNAL("textChanged(QString)"),
                               self._proxyModel.setFilterRegExp)
        
        self._treeView.setModel(self._proxyModel)
        self._setupTreeView.setModel(self._proxyModel)
        
        self.addTab(setupWidget, 'Setup')
        self.addTab(buildWidget, 'Build')
        self._setupTreeView.expandAll()
        
        #set selections
        self._setupTreeView.setCurrentIndex(self._model.index(0,0))
        self._populateSetupAttrsLayout(self._model.index(0,0))
        self._setupTreeView.clicked.connect(self._populateSetupAttrsLayout)
        
    def _runSetupButton(self):
        for rootNode in self._model._rootNode.children():
            print 'root : %s' % rootNode.name()
            print '%s children : %s' % (rootNode.name(), rootNode.children() )
            for node in rootNode.descendants():
                print node.name()
                
    def _runSelectedSetupButton(self):
        index = self._setupTreeView.currentIndex()
        if not index.isValid():
            return None
        
        node = self._model.itemFromIndex(index)
        
        if node:
            attrDict = dict()
            for attr in node.attributes():
                attrDict[attr.name()] = attr.value()
                
            node.initialize(**attrDict)
            node.runSetupRig()
            
    def _addComponentToGraph(self):
        index = self._fileView.currentIndex()
        
        model = self._fileView.model()
        nodeName = model.data(index)
        
        if nodeName in model._data:
            rootNode = self._model._rootNode
            cmd = 'import japeto.components.%s as %s' % (nodeName, nodeName)
            exec(cmd)
            newNodeCmd = '%s.%s' % (nodeName, nodeName.title())
            newNode = eval(newNodeCmd)
            newNode = newNode(str(nodeName))
            newNode.initialize()
            self._model.insertRows(rootNode.childCount(), 1,
                                   parent = QtCore.QModelIndex(),
                                   node = newNode)

    def _populateSetupAttrsLayout(self, index):
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
            print attr.name(), ':', attr.value()
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


class JapetoWindow(QtGui.QMainWindow):
    def __init__(self, graph, parent = None):
        super(JapetoWindow, self).__init__(parent)
        #get style sheet
        f = open(os.path.join(os.path.dirname(__file__),'japeto_styleSheet.qss'), 'r')
        styleData = f.read()
        self.setStyleSheet(styleData)
        f.close()
        
        self.setWindowTitle('Japeto Rig Build UI')
        tabWidget = CentralTabWidget(graph)
        self.setCentralWidget(tabWidget)
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('File')
        
        
