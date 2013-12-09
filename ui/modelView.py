#!/usr/bin/env python
import fields 
reload(fields)

from PyQt4 import QtGui, QtCore, uic
import cPickle
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

        print parentNode
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
        '''Items can be moved and copied (but we only provide an interface for moving items in this example.'''
        return QtCore.Qt.MoveAction | QtCore.Qt.CopyAction

    def insertRows(self, row, count, parent = QtCore.QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        self.endInsertRows()
        
        return True
     
    def removeRows( self, row, count, parentIndex ):
        '''Remove a number of rows from the model at the given row and parent.'''
        self.beginRemoveRows( parentIndex, row, row+count-1 )
        parent = self.getNode( parentIndex )
        for x in range( count ):
            parent.removeChild( parent.childAtIndex(row) )
        self.endRemoveRows()
        return True
    
    def mimeTypes( self ):
        '''The MimeType for the encoded data.'''
        types = QtCore.QStringList( 'application/x-pynode-item-instance' )
        return types
     
    def mimeData( self, indices ):
        '''Encode serialized data from the item at the given index into a QMimeData object.'''
        data = ''
        item = self.itemFromIndex( indices[0] )
        
        try:
            #print item.name()
            data += cPickle.dumps( item.name() )
        except:
            
            pass
        
        mimedata = QtCore.QMimeData()
        mimedata.setData( 'application/x-pynode-item-instance', data )
        return mimedata
     
    def dropMimeData( self, mimedata, action, row, column, parentIndex ):
        '''Handles the dropping of an item onto the model.
         
        De-serializes the data into a TreeItem instance and inserts it into the model.
        '''
        if not mimedata.hasFormat( 'application/x-pynode-item-instance' ):
            return False
        item = cPickle.loads( str( mimedata.data( 'application/x-pynode-item-instance' )))
        dropParent = self.itemFromIndex( parentIndex )
        for node in graph.nodes():
            if item == node.name():
                item = node
        dropParent.addChild( item )
        print dropParent.childCount()
        if dropParent.childCount() == 1:
            self.insertRows( dropParent.childCount()-1, 1, parentIndex )
        else:
            self.insertRows( dropParent.childCount()-2, 1, parentIndex )
        
        self.dataChanged.emit( parentIndex, parentIndex )
        return True
    
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
        self._graph = graph
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
        #self._setupTreeView.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self._setupTreeView.setDragDropMode(QtGui.QAbstractItemView.InternalMove) 
        self._setupTreeView.setDragEnabled( True )
        self._setupTreeView.setAcceptDrops( True )
        self._setupTreeView.expandAll()
        
        #file view
        self._fileView = FileView()
        
        #fields
        setupVerticleLayout = QtGui.QVBoxLayout()
        self._intField0 = fields.IntField('Test0')
        self._intField3 = fields.IntField('Test3')
        setupVerticleLayout.addWidget(self._intField0)
        setupVerticleLayout.addWidget(self._intField3)
        
        #buttons
        setupButtonLayout = QtGui.QHBoxLayout()
        self._addFileButton = QtGui.QPushButton('->') 
        self._setupSelectedButton  = QtGui.QPushButton('Run Selected')
        self._setupButton  = QtGui.QPushButton('Run All')
        setupButtonLayout.addWidget(self._setupSelectedButton)
        setupButtonLayout.addWidget(self._setupButton)
        
        self._setupButton.clicked.connect(self._runSetupButton)
        self._setupSelectedButton.clicked.connect(self._runSelectedSetupButton)
        
        #bring it all together
        setupWidgetLayout.addWidget(self._fileView, 1,0)
        setupWidgetLayout.addWidget(self._setupTreeFilter, 0,2)
        setupWidgetLayout.addWidget(self._addFileButton, 1,1)
        setupWidgetLayout.addWidget(self._setupTreeView, 1,2)
        setupWidgetLayout.addLayout(setupButtonLayout, 2,2)
        setupWidgetLayout.addLayout(setupVerticleLayout, 1,3)
        setupWidget.setLayout(setupWidgetLayout)
        
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
        
        QtCore.QObject.connect(self._treeFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        QtCore.QObject.connect(self._setupTreeFilter, QtCore.SIGNAL("textChanged(QString)"), self._proxyModel.setFilterRegExp)
        
        self._treeView.setModel(self._proxyModel)
        self._setupTreeView.setModel(self._proxyModel)
        
        self.addTab(setupWidget, 'Setup')
        self.addTab(buildWidget, 'Build')
        
    def _runSetupButton(self):
        for rootNode in self._graph.rootNodes():
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
            print node.name()
                


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


class SkeletonOutliner( QtGui.QMainWindow ):
    '''A window containing a tree view set up for drag and drop.'''
     
    def __init__( self, parent=None ):
        '''Instantiates the window as a child of the Maya main window, sets up the
        QTreeView with an OutlinerModel, and enables the drag and drop operations.
        '''
        super( SkeletonOutliner, self ).__init__( parent )
         
        self.tree = QtGui.QTreeView()
        self.outlinerModel = OutlinerModel( gatherItems() )
        self.tree.setModel( self.outlinerModel )
        self.tree.setDragEnabled( True )
        self.tree.setAcceptDrops( True )
        self.tree.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
         
        self.tree.expandAll()
         
        self.setCentralWidget( self.tree )
         
        self.show()
        
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