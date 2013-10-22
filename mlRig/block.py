#from japeto.mlRig import graph
from japeto.mlRig import mlRig_dict
from japeto.mlRig import node

class BaseBlock(mlRig_dict.MlRigDict):
    def __init__(self, name, *args, **kwargs):
        super(BaseBlock, self).__init__(*args, **kwargs)

        self.__name = name
        
    @property
    def name(self):
        return self.__name
    
    @property
    def graph(self):
        return self.__graph__
    
    @graph.setter
    def graph(self, value):
        if isinstance(value, graph.Graph):
            self.__graph__ = value

class Block(BaseBlock):
    def addNode(self, name, parent = None, child = None):
        node = node.Node(name)
        if not self.has_key(name):
            if parent:
                if self.has_key(parent):
                    #index = self.keys().index(parent)
                    node = node.BaseNode(name)
                    self[parent].update(node)
                    return node
            else:
                self[name] = node
                return node   