#from japeto.mlRig import ml_dict
from japeto.mlRig import ml_node

class MlGraph(object):
    def __init__(self, name):
        '''
        This constructor for the class sets up the base graph attributes.
        
        :param name: Name of the graph
        :type name: *str*
        '''
        super(MlGraph,self).__init__()
        
        self.__name       = name
        self.__rootNodes  = list()
        self.__nodes      = list()
        self.__rootNode__ = ml_node.MlNode('root')
    
    def name(self):
        return self.__name

    def rootNodes(self):
        return self.__rootNodes
        
    def addNode(self, node, parent = None, index = None):
        #if name passed in instead of node
        if isinstance(node, basestring):
            node = ml_node.MlNode(node, parent)
        elif parent:
            if node in self.__rootNodes:
                self.removeNode(node)
            node.setParent(parent)
        
        if not ml_node.MlNode.isValid(node):
            ml_node.MlNode.inValidError(node)    
        
        if parent and index != None:
            parent.moveChild(node, index)
        elif not parent and index != None:
            self.__rootNodes.insert(index,node)
        elif not parent and index == None:
            self.__rootNodes.append(node)
        elif parent and index == None:
            parent.addChild(node)
        
        return node
    
    def removeNode(self, node):
        if node in self.__rootNodes:
            self.__rootNodes.pop(node.index())
        
        if node.parent():
            node.parent().removeChild(node)
        
    def nodeCount(self):
        count = len(self.__rootNodes)
        
        for node in self.__rootNodes:
            count += node.descendantCount()
            
        return count
    
    def nodes(self):
        nodes = list()
        for node in self.__rootNodes:
            nodes.append(node)
            nodes.extend(node.descendants())
            
        return nodes
    
    def log(self, tabLevel = -1):
        '''
        Logs the whole graph. Returns the whole graph in a sting
        
        :param tabLevel: This shows how many tabs in we start
        :type tabLevel: int
        '''
        output = "\n"
        tabLevel += 1 #add to the tabLevel
        
        #tab in based on the tabLevel
        for i in range(tabLevel):
            output += "\t"
            
        output += '____%s\n' % self.__rootNode__.name()
        
        for node in self.__rootNodes:
            output += node.log(tabLevel)
        
        tabLevel -= 1
        output += '\n'
        return output

    def nodeNames(self):
        nodeNames = list()
        for node in self.__rootNodes:
            nodeNames.append(node.name())
            for child in node.descendants():
                nodeNames.append(child.name())
            
        return nodeNames
    
    def getNodeByName(self, name):
        for node in self.nodes():
            if name == node.name():
                return node
        return None
    
    '''
    def save(self, filepath):
        print 'Saving %s' % filepath
        
        for node in self.nodes():
            node
    ''' 
        