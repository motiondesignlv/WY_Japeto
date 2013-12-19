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
        #if not isinstance(node, cls):
        #    return False
        
        return True
    
    @classmethod
    def inValidError(cls, node):
        raise TypeError("%s is not of type japeto.mlRig.ml_node.MlNode" % node)
    
    def __init__(self, name, parent = str()):
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
        return "< %s %s >" % (self.__class__.__name__, self.__name)
    
    def name(self):
        return self.__name    

    def parent(self):
        return self.__parent
    
    def children(self):
        return self.__children.values()
    
    def enable(self):
        self.__enabled = True
    
    def disable(self):
        self.__enabled = False
        
    def attributes(self):
        return self.__attributes.values()
    
    def attributeAtIndex(self, index = None):
        if index != None and not index > len(self.__attributes.keys()):
            return self.__attributes.values()[index]
    
    def setName(self, value):
        self.__name  = value
    
    def addAttribute(self, attr, value):
        '''
        sets the data on the node based on key : value pairs
        
        @example:
            >>> setData(limb.arm(), position = [20,10,10])
            {"Left Arm" : []}
            
        @param attr: Nice name for user interface
        @type attr: *str*

        @param value: python object to be called when run() is called
        @type value: *str*
        '''
        if isinstance(attr, basestring):
            attr = ml_attribute.MlAttribute(attr, value = value)
        
        #check to make sure an attribute was passed in
        if not isinstance(attr, ml_attribute.MlAttribute):
            raise TypeError('%s must be %s' % (attr, ml_attribute.MlAttribute))
        
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
        
    def addChildren(self, children, index = None):
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
        if index == None:
            index = 0
        for child in children:
            self.addChild(child, index)
            index +=1
     
    
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
    
    def getChild(self, name = str(), index = None):
        '''
        Gets child by name
        
        @param name: Name of the child to query
        @type name: *str*
        
        @return: Child node
        @rtype: *node.Node*  
        '''
        if self.__children.has_key(name):
            return self.__children[name]
        
        return None
    
    def childAtIndex(self, index = None):
        '''
        Gets child by name
        
        @param name: Name of the child to query
        @type name: *str*
        
        @return: Child node
        @rtype: *node.Node*  
        '''
        if index != None:
            if self.children():
                return self.children()[index]
        
        return None
    
    
    
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
        return len(self.children())
    
    def descendantCount(self):
        children = self.children()
        count = 0
        if children:
            for child in children: 
                count += 1
                count += child.descendantCount()
            return count
        else:
            return count
        
    def descendants(self):
        children = self.children()
        nodes = list()
        if children:
            for child in children:
                nodes.append(child)
                newNodes = child.descendants()
                if newNodes:
                    if newNodes not in nodes:
                        nodes.extend(newNodes)
            return nodes
        else:
            return nodes


    def index(self):
        '''
        returns what index the current node is at on the parents list of children
        '''
        if self.__parent.children():
            return self.__parent.children().index(self)
        
        return 0
    
    
    def log(self, tabLevel = -1):
        output = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
            
        output += '|____%s\n' % self.__name
        
        for child in self.children():
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += '\n'
        return output
    
    def execute(self, *args, **kwargs):
        '''
        @todo: add execution code here
        '''
        return
            
            