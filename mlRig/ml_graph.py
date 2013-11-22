from japeto.mlRig import mlRig_dict
from japeto.mlRig import block
from japeto.mlRig import ml_node
from japeto.libs import common
import inspect

class MlGraph(object):
    def __init__(self, name):
        '''
        This constructor for the class sets up the base graph attributes.
        
        @param name: Name of the graph
        @type name: *str*
        '''
        super(MlGraph,self).__init__()
        
        self.__name = name
        self.__rootNodes = list()
            
    @property
    def name(self):
        return self.__name
    
    @property
    def rootNodes(self):
        return self.__rootNodes

    def addNode(self, name, parent = None, index = None):
        #Construct and instance of the node object
        node = ml_node.MlNode(name, parent)
        
        if parent and index != None:
            parent.moveChild(node, index)
        elif not parent and index != None:
            self.__rootNodes.insert(index,node)
        elif not parent and index == None:
            self.__rootNodes.append(node)
        
        return node
    
    def nodeCount(self):
        count = len(self.rootNodes)
        
        for node in self.__rootNodes:
            count += node.descendantCount()
            
        return count