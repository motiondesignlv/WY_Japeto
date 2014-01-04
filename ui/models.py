'''
UI models 
'''
#PyQt modules
from PyQt4 import QtGui
from PyQt4 import QtCore

#python modules
import os

#Japeto modules
from japeto.mlRig import ml_graph, ml_node
from japeto import components, nodes

#import maya modules
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import OpenMayaUI
from maya import cmds


class FileListModel(QtCore.QAbstractListModel):
    __dirPath__ = components.__path__[0]
    
    def __init__(self, parent = None):
        super(FileListModel, self).__init__(parent)
        
        self._data = self._getFiles()
        
    def headerData(self,section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:  
            return QtCore.QVariant('Components')
     
        return None  
        
    
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
        for _file in files:
            if _file not in nullFiles and '.pyc' not in _file:
                if '.py' in _file and _file not in fileList:
                    fileList.append(_file.split('.')[0])
                #end if
            
        #end loop
        return fileList


class LayerGraphModel(QtCore.QAbstractItemModel):
    NodeRole = QtCore.Qt.UserRole
    def __init__(self, graph, parent = None):
        super(LayerGraphModel, self).__init__(parent)

        self._rootNode = ml_node.MlNode('root')
        children = graph.rootNodes()
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
    
    def headerData(self,section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:  
            return QtCore.QVariant('Graph')  
     
        return None  
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
    
    def parent(self, index):
        """
        :param index: Index of the node on the graph you want to get the parent
        :type index: *QModelIndex* 
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
        :param row: Row index of the child node.
        :type index: *int* 
        
        :param column: Column index of the child node.
        :type column: *int* 
        
        :param parent: Parent of the child we are looking for.
        :type parent: *QModelIndex*
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
        return QtCore.Qt.MoveAction 

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
            #print """PARENT IS VALID, inserting ONTO something since row was not -1, 
            #        beginRow becomes 0 because we want to insert it at the begining
            #        of this parents children"""
            parentNode = parent.internalPointer()
            beginRow = parentNode.childCount()
        else:
            #print """PARENT IS INVALID, inserting to root, can change to 0 if you want 
            #        it to appear at the top"""
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


class FileGraphModel(LayerGraphModel):
    __componentPath__ = components.__path__[0]
    __nodePath__ = nodes.__path__[0]
    
    def __init__(self, parent = None):
        self._graph      = ml_graph.MlGraph('fileList')
        self._components = self._graph.addNode('Components')
        self._nodes = self._graph.addNode('Nodes')
        
        #disable the top nodes
        self._components.disable()
                
        self._getComponents()
        self._getNodes()
        
        super(FileGraphModel, self).__init__(self._graph,parent)
    
    def headerData(self,section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:  
            return QtCore.QVariant('Node List')  
     
        return None  
    
    def flags(self, index):
        if index.isValid():
            node = index.internalPointer()
            if not node.active():
                return QtCore.Qt.ItemIsEnabled
        
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled

    def _getComponents(self):
        '''
        List all the files in the given directory for this model. (__dirPath__)
        '''
        nullFiles = ['__init__.py', 'puppet.py', 'component.py']
        files = os.listdir(FileGraphModel.__componentPath__)
        fileList = list()
        for _file in files:
            if _file not in nullFiles and '.pyc' not in _file:
                if '.py' in _file and _file not in fileList:
                    self._graph.addNode(_file.split('.')[0], self._components)
                #end if
                
    def _getNodes(self):
        '''
        List all the files in the given directory for this model. (__dirPath__)
        '''
        nullFiles = ['__init__.py', 'puppet.py', 'component.py']
        files = os.listdir(FileGraphModel.__nodePath__)
        fileList = list()
        for _file in files:
            if _file not in nullFiles and '.pyc' not in _file:
                if '.py' in _file and _file not in fileList:
                    self._graph.addNode(_file.split('.')[0], self._nodes)
                #end if
