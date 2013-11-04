#!/usr/bin/env python
from PyQt4 import QtGui, QtCore, uic
import sys


class Node(object):
    def __init__(self, name, parent = None):
        self._name = name
        self._children = list()
        self._parent = parent
        
        if parent !=None:
            parent.addChild(self)
            
    def __repr__(self):
        return self.log()
            
    def addChild(self,child):
        #validate child is a Node
        if not isinstance(child, Node):
            raise TypeError("%s must be a %s" % (child, Node))
        
        self._children.append(child)
        
    def insertChild(self, position, child):
        if position < 0  or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        
        return True
    
    def removeChild(self, position):
        if position < 0  or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None
        
        return True

    def name(self):
        return self._name
    
    def setName(self, name):
        self._name = name
    
    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)
    
    
    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent:
            return self._parent._children.index(self)
    
    def typeInfo(self):
        return "Node"
    
    def log(self, tabLevel = -1):
        output = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
            
        output += '|------%s\n' % self._name
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += '\n'
        return output
        
        
class SceneGraph(QtCore.QAbstractItemModel):
    def __init__(self, root, parent = None):
        super(SceneGraph, self).__init__(parent)
        
        self._rootNode = root
        
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
        
        @param column: Columb index of the child node.
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

        rootNode      = Node("Hips")
        leftLegNode   = Node("LeftLeg", rootNode)
        leftFootNode   = Node("LeftFoot", leftLegNode)
        rightLegNode  = Node("RightLeg", rootNode)
        rightFootNode  = Node("RightFoot", rightLegNode)
        
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
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")

    wnd = WindowTutorial()
    wnd.show()
    
    sys.exit(app.exec_())