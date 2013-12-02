#!/usr/bin/env python
import fields 
reload(fields)

from PyQt4 import QtGui, QtCore, uic
import sys
import os
sys.path.append('/Users/walt/Library/preferences/Autodesk/maya/2013-x64/scripts')
from japeto.mlRig import ml_graph, ml_node
from japeto import components
reload(ml_graph) 
reload(ml_node)

try:
    from maya import OpenMaya
    from maya import OpenMayaAnim
except:
    print'Not in Maya!'



class BaseDeformer(object):
    def __init__(self, name):
        self.__mesh = str()
        self.__deformerType = str('Base')
        self.__name = name
        self._maps = [BaseMap('head'), BaseMap('jaw')]
    
    def name(self):
        return self.__name
    
    def setName(self, value):
        self.__name = value
        
    def maps(self):
        return self._maps
    
class SkinCluster(BaseDeformer):
    def __init__(self, name):
        super(SkinCluster, self).__init__(name)
        self.__deformerType = str('SkinCluster')
        self.__name = name
        self._maps = [BaseMap('arm'), BaseMap('leg')]
                
class BaseMap(object):
    def __init__(self, name):
        self.__name = name
        
    def name(self):
        return self.__name

class ListModel(QtCore.QAbstractListModel):
    def __init__(self,data, parent = None):
        super(ListModel, self).__init__(parent)
        
        self._data = data
        
    def headerData(self):
        pass
        #return 'Deformer'
    
    def rowCount(self, parent):
        return len(self._data)
    
    def data(self,index, role):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            obj = self._data[index.row()]
            return obj.name()
            
        return QtCore.QVariant()
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    '''
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode
    
    
    
    def insertRows(self,row,count,parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent,row, row + count - 1)
        
        parent = self.getNode(parent)
        
        self.endInsertRows()
    
    def removeRows(self):
        self.beginRemoveRows()
        pass
        self.endRemoveRows()
    '''
    
class FileListModel(QtCore.QAbstractListModel):
    __dirPath__ = components.__path__[0]
    
    def __init__(self, parent = None):
        super(FileListModel, self).__init__(parent)
        
        self._data = self._getFiles()
        
    def headerData(self):
        return 'Components'
    
    def rowCount(self, parent):
        return len(self._data)
    
    def data(self,index, role):
        if index.isValid() and role == QtCore.Qt.DisplayRole:
            return self._data[index.row()] 
            
        return QtCore.QVariant()
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
    
    def _getFiles(self):
        '''
        List all the files in the given directory for this model. (__dirPath__)
        '''
        files = os.listdir(FileListModel.__dirPath__)
        fileList = list()
        for file in files:
            if not '__init__' in file and not 'pyc' in file:
                if '.py' in file and file not in fileList:
                    fileList.append(file.split('.')[0])
                #end if
            #end if
        #end loop
        return fileList

        
class LayerGraph(QtCore.QAbstractItemModel):
    def __init__(self, graph, parent = None):
        super(LayerGraph, self).__init__(parent)

        self._rootNode = ml_node.MlNode('root')
        children = graph.rootNodes()
        #children.reverse()
        print children
        self._rootNode.addChildren(children)
        
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
        return self.createIndex(parentNode.row(), 0, parentNode)
    
    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(value)
                
                return True
            
        return False
    
    def index(self, row, column,parent):
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

        childItem = parentNode.childAtIndex(index = row)

        if childItem:
            return self.createIndex(row, column, childItem)
        
        return QtCore.QModelIndex()
        
    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    def insertRows(self,position, rows, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows + 1)
        
        parentNode = self.getNode(parent)
        
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = ml_node.MlNode("untitled%s" % childCount)
            success = parentNode.addChild(childNode,position)
            
        self.endInsertRows()
        
        return success
        
    def removeRows(self,position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        parentNode = self.getNode(parent)
        for row in range(rows):
            success = parentNode.removeChild(position)
            
        self.endRemoveRows()
        
        return success

class FileView(QtGui.QListView):
    def __init__(self, parent = None):
        super(FileView, self).__init__(parent)
        
        self.setAlternatingRowColors(True)
        self._model = FileListModel()
        self.setModel(self._model)
        self.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
        self.setDragEnabled(True)
        

class TreeWindow(QtGui.QTabWidget):
    def __init__(self, graph, parent = None):
        super(TreeWindow, self).__init__(parent)
        #-------------------------------------------------
        #BUILD WIDGET
        #-------------------------------------------------
        buildWidget = QtGui.QWidget()
        buildWidgetLayout = QtGui.QGridLayout()
        self._treeFilter = QtGui.QLineEdit()
        self._treeView = QtGui.QTreeView()
        self._treeView.setAlternatingRowColors(True)
        
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
        setupWidgetLayout = QtGui.QGridLayout()
        self._setupTreeFilter = QtGui.QLineEdit()
        self._setupTreeView = QtGui.QTreeView()
        self._setupTreeView.setAlternatingRowColors(True)
        self._setupTreeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        
        #file view
        self._fileView = FileView()
        
        #fields
        setupVerticleLayout = QtGui.QVBoxLayout()
        self._intField0 = fields.IntField('Test0')
        self._intField3 = fields.IntField('Test3')
        setupVerticleLayout.addWidget(self._intField0)
        setupVerticleLayout.addWidget(self._intField3)
        
        #buttons
        self._buttonLayout = QtGui.QHBoxLayout()
        self._setupButton  = QtGui.QPushButton('Run Setup') 
        
        #bring it all together
        setupWidgetLayout.addWidget(self._fileView, 1,0)
        setupWidgetLayout.addWidget(self._setupTreeFilter, 0,1)
        setupWidgetLayout.addWidget(self._setupTreeView, 1,1)
        setupWidgetLayout.addLayout(setupVerticleLayout, 1,2)
        setupWidget.setLayout(setupWidgetLayout)
        
        #-------------------------------------------------
        #MODEL AND PROXY MODEL
        #-------------------------------------------------
        #setup proxy model
        self._proxyModel = QtGui.QSortFilterProxyModel()
        #model for scenegraph
        self._model = LayerGraph(graph)
        
        #hook proxy model to scenegraph model
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True)
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        QtCore.QObject.connect(self._treeFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        QtCore.QObject.connect(self._setupTreeFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        
        self._treeView.setModel(self._proxyModel)
        self._setupTreeView.setModel(self._proxyModel)
        
        self.addTab(setupWidget, 'Setup')
        self.addTab(buildWidget, 'Build')
        
    def _runSetupButton(self):
        print 'Running Setup on all'
                


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")

    graph = ml_graph.MlGraph('Test')
    a = graph.addNode('A')
    b = graph.addNode('B', parent = a)
    c = graph.addNode('C')
    d = graph.addNode('D', parent = c)
    wnd = TreeWindow(graph)
    wnd.show()
 
    sys.exit(app.exec_())



#################################################################### 
class MainWindow(QtGui.QWidget): 
    def __init__(self, deformers, *args): 
        super(MainWindow, self).__init__(*args) 
        #list to store maps
        self._currentMaps = list()

        # create lists
        #deformers
        self.__deformers = deformers
        deformerModel = ListModel(deformers, self)
        deformerLayout = QtGui.QVBoxLayout()
        deformerLabel = QtGui.QLabel('Deformers')
        self._deformerView = QtGui.QListView()
        self._deformerView.setModel(deformerModel)
        deformerLayout.addWidget(deformerLabel)
        deformerLayout.addWidget(self._deformerView)
        
        self._deformerView.clicked.connect(self._setMapsList)
        
        
        #maps
        mapsLabel = QtGui.QLabel('Maps')
        self._mapsView = QtGui.QListView()
        mapsLayout = QtGui.QVBoxLayout()
        mapsLayout.addWidget(mapsLabel)
        mapsLayout.addWidget(self._mapsView)
        
        
        #buttons
        verticleLayout = QtGui.QVBoxLayout()
        buttonLayout = QtGui.QHBoxLayout()
        self._copyButton = QtGui.QPushButton('Copy')
        self._pasteButton = QtGui.QPushButton('Paste')
        self._saveButton = QtGui.QPushButton('Save')
        buttonLayout.addWidget(self._copyButton)
        buttonLayout.addWidget(self._pasteButton)
        buttonLayout.addWidget(self._saveButton)
        verticleLayout.addStretch()
        verticleLayout.addLayout(buttonLayout)
        
        self._saveButton.clicked.connect(self._saveMap)
        self._copyButton.clicked.connect(self._copyMap)
        self._pasteButton.clicked.connect(self._pasteMap)
        
        # layout
        layout = QtGui.QHBoxLayout()
        layout.addLayout(deformerLayout)
        layout.addLayout(mapsLayout)
        layout.addLayout(verticleLayout)
        self.setLayout(layout)
        
        
    def _setMapsList(self,index):
        if not index.isValid():
            return False
        #set the current maps
        self._currentMaps = self.__deformers[index.row()].maps()
        #create the model ans set it to the mapsView
        model = ListModel(self._currentMaps, self)
        self._mapsView.setModel(model)
        
    def _saveMap(self):
        index = self._mapsView.currentIndex()
        
        if not index.isValid():
            return False
        
        print 'saving map %s ' % self._currentMaps[index.row()].name()
    
    def _copyMap(self):
        index = self._mapsView.currentIndex()
        
        if not index.isValid():
            return False
        print 'copy map'
        
    def _pasteMap(self):
        index = self._mapsView.currentIndex()
        
        if not index.isValid():
            return False
        
        print 'paste map'        


####################################################################
''' 
def main(): 
    app = QtGui.QApplication(sys.argv)
    deformers = [BaseDeformer('Anna'), SkinCluster('Kristoff')]
    w = MainWindow(deformers) 
    w.show() 
    sys.exit(app.exec_()) 
        
####################################################################
if __name__ == "__main__": 
    main()        
        
'''
