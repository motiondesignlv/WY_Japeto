from japeto.mlRig import mlRig_dict
reload(mlRig_dict)

import inspect

class Node(mlRig_dict.MlRigDict):
    @classmethod
    def isValid(cls, node):
        if not isinstance(node, Node):
            return False
        
        return True
    
    @classmethod
    def inValidError(cls, node):
        raise TypeError("%s is not of type japeto.mlRig.node.Node" % node)
    
    def __init__(self, name, block = None, parent = None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.__name     = name
        self.__block    = block
        self.__parent   = parent
        self.__children = mlRig_dict.MlRigDict()
        #add the build dictionary for calling build functions and classes
        #self.add("build", mlRig_dict.MlRigDict(), index = 0)
    
    def __repr__(self):
        return "< %s %s >" % (self.__class__.__name__, self.name)
        
    @property
    def name(self):
        return self.__name
    
    @property
    def block(self):
        return self.__block
    
    @property
    def parent(self):
        return self.__parent
    
    @parent.setter
    def parent(self, value):
        self.setParent(value)
    
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
        if not self.has_key("build"):
            self.add("build", mlRig_dict.MlRigDict(), index = 0)
        #set the build data on the build key
        if not self["build"].keys():
            self["build"].add(name, (value,kwargs), index = 0)
            return
        
        #if it already exists, clear it and add the new one
        self["build"].clear()
        self["build"].add(name, (value,kwargs), index = 0)
        
    def setParent(self, parent):
        '''
        Sets the parent for self. Parent node must be node.Node
        
        @example:
            >>> a = node.Node('A')
            >>> b = node.Node('A') 
            >>> b.setParent(a)
            >>> a.children
            ['B']
        
        @param parent: Node you want to be parent of self
        @type parent: *node.Node* 
        '''
        #validate
        if not Node.isValid(parent):
            Node.inValidError(parent)
        #check if parent
        if self.__parent and self.__parent != parent:
            self.__parent.removeChild(self) #remove child from parent
        elif self.__parent == parent:
            return #return if there is a parent
        #add self to parent
        self.__parent = parent
        parent.addChild(self)
        
    
    def addChild(self, child, index = None):
        #check the index, make sure it's never 0
        if index == 0 and index != None:
            if self.has_key("build"):
                index = 1
        
        #check to see if there is a parent
        if not isinstance(child, Node):
            raise TypeError("%s must be of type jepeto.mlRig.node.Node" % child)

        #add self as parent of child node
        child.setParent(self)
        
        #child.setParent(self)
        self.__children[child.name] = child
        
        #change index if it's none
        if index == None:
            index = len(self.keys())

        self.add(child.name, child, index)
    
    def addArgument(self, key, value):
        if self["build"].values():
            self["build"].values()[1][key] = value
        
    def getData(self):
        '''
        Returns the value of the node. Normally this will be a 
        class or function.
        '''
        if len(self["build"].values()) >= 1:
            return self["build"].values()[0]
        
        return None
    
    def getArguments(self):
        '''
        Returns Keyword arguments passed into the second index
        of value list on the node
        '''
        if len(self["build"].values()) >= 1:
            return self["build"].values()[1]
        
        return None
    
    
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
    
    def removeChild(self, child):
        '''
        Removes child node from list of children and take is out of self
        
        @example:
            >>> a.children
            ['B', 'C']
            >>> b.parent.name
            A
            >>> a.removeChild(b)
            >>> a.children
            ['C']
        
        @param child: Node you want to remove from self
        @type child: *node.Node*  
        '''
        #check if child is valid
        if not Node.isValid(child):
            Node.inValidError(child)
        #check key on  __children dict, if it exists, pop it out of dict
        if self.__children.has_key(child.name):
            self.__children.pop(child.name) #remove it from __children dict
            self.pop(child.name) #remove it from self

    def moveChild(self, child, index):
        #check if child is a valid node
        if not Node.isValid(child):
            Node.inValidError(child)
        #reorder the __children dict
        self.__children.move(child.name, index)
        #change index for self dict
        if index == 0:
            if self.has_key("build"):
                index = 1
        #move child to new index
        self.move(child.name, index)

    def isChild(self, node):
        if not Node.isValid(node):
            node = node.name
        if not isinstance(node, basestring):
            raise TypeError("%s must be a *str* or *node.Node*" % node)
            
        if self.__children.has_key(node):
            return True
        
        return False
    
    def execute(self):
        #if self.getData()
        pass