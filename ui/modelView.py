#!/usr/bin/env python
import fields 
reload(fields)

from PyQt4 import QtGui, QtCore, uic
import sys
sys.path.append('/Users/walt/Library/preferences/Autodesk/maya/2013-x64/scripts')
from japeto.mlRig import ml_graph, ml_node
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

        
class LayerGraph(QtCore.QAbstractItemModel):
    def __init__(self, graph, parent = None):
        super(LayerGraph, self).__init__(parent)

        self.__rootNode = graph.root
        
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
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
    
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
            
        childItem = parentNode.child(row)
        
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
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
            childNode = Node("untitled%s" % childCount)
            success = parentNode.insertChild(position,childNode)
            
        self.endInsertRows()
        
        return success
        
    def removeRows(self,position, rows, parent = QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        parentNode = self.getNode(parent)
        for row in range(rows):
            success = parentNode.removeChild(position)
            
        self.endRemoveRows()
        
        return success
    
#load the ui file    
base , form = uic.loadUiType("mainWindow.ui")

class WindowTutorial(base, form):
    def __init__(self, parent = None):
        super(base, self).__init__(parent)
        self.setupUi(self)
        
        #setup proxy model
        self._proxyModel = QtGui.QSortFilterProxyModel()
        #model for scenegraph
        self._model = SceneGraph(rootNode)
        
        #hook proxy model to scenegraph model
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setDynamicSortFilter(True) 
        self._proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        
        self.uiTree.setModel(self._proxyModel)
        
        QtCore.QObject.connect(self.uiFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        
        self.uiTree.setSortingEnabled(True)


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
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")


    wnd = WindowTutorial()
    wnd.show()

    checkNumLabel = fields.LineEditField('Checks',value = 'Walter')
    amountField = fields.IntField('Amount',value = 20, description = 'Amount of money to deposit.', min = 0)
    
    tabWidget = QtGui.QTabWidget()
    cashWidget = QtGui.QWidget()
    cashLayout = QtGui.QHBoxLayout()
    cashLayout.addWidget(checkNumLabel)
    cashLayout.addWidget(amountField)
    cashWidget.setLayout(cashLayout)
    tabWidget.addTab(cashWidget, 'Check')
    
    tabWidget.show()
    
    sys.exit(app.exec_())
'''