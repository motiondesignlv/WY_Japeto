from japeto.mlRig import mlRig_dict
reload(mlRig_dict)

import inspect

class Node(mlRig_dict.MlRigDict):
    def __init__(self, name, block = None, parent = None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.__name     = name
        self.__block    = block
        self.__parent   = parent
        self.__children = mlRig_dict.MlRigDict()
        
    @property
    def name(self):
        return self.__name
    
    @property
    def block(self):
        return self.__block
    
    @property
    def parent(self):
        return self.__parent
    
    @property
    def children(self):
        return self.__children.keys()
            
    def setBlock(self, block):
        '''
        Sets the block for the node
        '''
        if not self.__block:
            self.__block = block
    
    
    def setData(self, name, value, **kwargs):
        '''
        sets the data on the node based on key :value pairs and takes 
        additional keyword arguments to hand overloading of arguments 
        on the functions or classes.
        
        @example:
            >>> setData("Left Arm", limb.arm(), position = [20,10,10])
            {"Left Arm" : []}
            
        @param name: Nice name for user interface
        @type name: *str*

        @param value: python object to be called when run() is called
        @type value: *method* or *function* or *class*
        '''
        #need to figure out how to store the data
        """
        if not len(self.keys()) < 1 and self.values():
            raise RuntimeError('%s already has data on it. Must be setting %s. Try addArgument(key, value)' % (self.name, self.keys()[0]))
        """
        self.add(name, (value,kwargs), index = 0)
    
    '''
    def setParent(self, parent = None):
        if self.__block:
            if self.__block.has_key(parent):
                if self.__block[parent].has_key("children"):
    '''             
    
    def addChild(self, child = None):
        if not isinstance(child, Node):
            raise TypeError("%s must be of type *japeto.mlRig.node.Node*" % child)
        self.__children[child.name] = child
    
    def addArgument(self, key, value):
        if self.values():
            self.values()[1][key] = value
        
    def getData(self):
        '''
        Returns the key of the node. Normally this will be a 
        class or function.
        '''  
        return self.values()[0]
    
    def getArguments(self):
        '''
        Returns Keyword arguments passed into the second index
        of value list on the node
        '''
        return self.values()[0][0]
    
    def hasChild(self, name = str()):
        '''
        Returns True or False depending on whether or not self 
        has child node.
        
        @param name: Name of the child to query
        @type name: *str*
        
        @return: True if it has child, False if it does not
        @rtype: *bool*  
        '''
        #check to see if the node has a child
        if self.__children.has_key(name):
            return True
        
        return False
    
    def getChild(self, name = str()):
        '''
        Gets child by name
        
        @param name: Name of the child to query
        @type name: *str*
        
        @return: Child node
        @rtype: *node.Node*  
        '''
        if self.__children.has_key(name):
            return self.__children[name]
    
    def getParent(self):
        return True
    