from japeto.libs import ordereddict
class Base(ordereddict.OrderedDict):
    def __init__(self, name, *args, **kwargs):
        super(Base,self).__init__(*args, **kwargs)
        self._name = name
        
    @property
    def name(self):
        return self._name
            
    def __repr__(self):
        return '< %s.%s >' % (self.__class__.__name__, self.name)
    
    
    def add(self, key, value, index = None):
        if self.keys():
            #get keys and values
            keys = self.keys()
            values = self.values()
            
            if index > len(self.keys()):
                if not self.has_key(key):
                    self.clear()
                    keys.append(key)
                    values.append(value)
                    for k,v in zip(keys, values):
                        self[k] = v
            if not self.has_key(key):
                keys.insert(index,key)
                values.insert(index,value)
                self.clear()
                for k,v in zip(keys, values):
                    self[k] = v
        else:
            self[key] = value

class Graph(Base):
    def addBlock(self, name):
        pass

class Block(Base):
    def addNode(self, name, parent = None):
        node = Node(name)
        if not self.has_key(name):
            if parent:
                if self.has_key(parent):
                    #index = self.keys().index(parent)
                    node = Node(name)
                    self[parent].update(node)
                    return node
            else:
                self[name] = node
                return node
                

            
class Node(Base):
    def setData(self, key, value):
        if not self.has_key(key):
            self.add(key, value)
        pass
    
    def getData():          
        pass