'''
Node will track and manage all data with-in a node
'''
from japeto.mlRig import ml_dict
from japeto.mlRig import ml_attribute
reload(ml_attribute)
reload(ml_dict)

class MlNode(object):
    '''
    Base node to manage all data for nodes
    
    @todo:
        - Change validation to check for both node and node name
        - Make sure self.__children and self.__parent return the
          same type of data. (i.e. Node or Node.name)
      
    @warning:
        Some data may not match (i.e. Node.children returns 
        childNode.name and Node.parent return instance of parentNode)
    
    '''
    @classmethod
    def isValid(cls, node):
        if not isinstance(node, MlNode):
            return False
        
        return True
    
    @classmethod
    def inValidError(cls, node):
        raise TypeError("%s is not of type japeto.mlRig.ml_node.MlNode" % node)
    
    def __init__(self, name, parent = None, *args, **kwargs):
        super(MlNode, self).__init__(*args, **kwargs)
        
        #declare class variable
        self.__name       = name
        self.__parent     = parent
        self.__children   = ml_dict.MlDict()
        self.__attributes = ml_dict.MlDict()
        self.__enabled    = True
        
        if parent:
            if not MlNode.isValid(parent):
                MlNode.inValidError(parent)
            parent.addChild(self)


    
    def __repr__(self):
        return "< %s %s >" % (self.__class__.__name__, self.name)
        
    @property
    def name(self):
        return self.__name
    
    @property
    def parent(self):
        return self.__parent
    
    @parent.setter
    def parent(self, value):
        self.setParent(value)
    
    @property
    def children(self):
        return self.__children.values()
    
    def enable(self):
        self.__enabled = True
    
    def disable(self):
        self.__enabled = False
    
    
    def addAttribute(self, attr):
        '''
        sets the data on the node based on key : value pairs
        
        @example:
            >>> setData(limb.arm(), position = [20,10,10])
            {"Left Arm" : []}
            
        @param name: Nice name for user interface
        @type name: *str*

        @param value: python object to be called when run() is called
        @type value: *str*
        '''
        #check to make sure an attribute was passed in
        if not isinstance(attr, attribute.Attribute):
            raise TypeError('%s must be %s' % (attr, attribute.Attribute))
        
        #add attributes to the attributes dictionary
        self.__attributes.add(attr.name, attr, index = len(self.__attributes.keys()))
        
    def setParent(self, parent):
        '''
        Sets the parent for self. Parent node must be node.Node
        
        @example:
            >>> a = node.Node('A')
            >>> b = node.Node('B') 
            >>> b.setParent(a)
            >>> a.children
            ['B' : b]
        
        @param parent: Node you want to be parent of self
        @type parent: *node.Node* 
        '''
        #validate
        if not MlNode.isValid(parent) and parent != None:
            MlNode.inValidError(parent)
        #check if parent
        if self.__parent and self.__parent != parent:
            self.__parent.removeChild(self) #remove child from parent
        elif self.__parent == parent:
            return #return if there is a parent
        #add self to parent
        self.__parent = parent
        if parent == None:
            return
        parent.addChild(self)
        
    
    def addChild(self, child, index = None):
        '''
        Adds an existing node as a child.
        
        @example:
            >>> a = node.Node('A')
            >>> b = node.Node('B') 
            >>> a.addChild(a)
            >>> a.children
            ['B']
            
        @param child: child node you wish to add 
        @type child: *node.Node*  
        '''
        #validate child
        if not MlNode.isValid(child):
            MlNode.inValidError(child)
        
        #check the index, make sure it's never 0
        
        #add self as parent of child node
        child.setParent(self)
        
        #change index if it's none
        if index == None:
            index = len(self.__children.keys())

        #add child
        self.__children.add(child.name, child, index)
     
    
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
        if self.isChild(name):
            return True
        
        return False
    
    def getAttributes(self):
        '''
        Returns the value of the node. Normally this will be a 
        class or function.
        '''
        return self.__attributes  
    
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
        if not MlNode.isValid(child):
            MlNode.inValidError(child)
        #check key on  __children dict, if it exists, pop it out of dict
        if self.__children.has_key(child.name):
            self.__children.pop(child.name) #remove it from __children dict
            child.setParent(None) #remove self from parent

    def moveChild(self, child, index):
        '''
        moves child node from one position in dict to another
        
        @example:
            >>> a.children
            ['B', 'C']
            >>> b.parent.name
            A
            >>> a.moveChild(b,1)
            >>> a.children
            ['C','B']
        
        @param child: Node you want to move
        @type child: *node.Node*  or *str*
        '''
        #check if child is a valid node
        if not MlNode.isValid(child):
            MlNode.inValidError(child)
        #reorder the __children dict
        self.__children.move(child.name, index)

    def isChild(self, node):
        if not MlNode.isValid(node):
            MlNode.inValidError(node)
        
        if self.__children.has_key(node.name):
            return True
        
        return False
    
    def childCount(self):
        '''
        Returns the length of the children
        '''
        return len(self.children)
    
    def descendantCount(self):
        count = self.childCount()
        
        for child in self.children:
            count += child.childCount()
            
        return count
    
    def index(self):
        '''
        returns what index the current node is at on the parents list of children
        '''
        return self.__parent.children.index(self)
    
    
    def log(self, tabLevel = -1):
        output = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
            
        output += '|____%s\n' % self.__name
        
        for child in self.children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += '\n'
        return output
    
    def execute(self, *args, **kwargs):
        '''
        @todo: add execution code here
        '''
        return
            
            