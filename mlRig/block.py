#from japeto.mlRig import graph
from japeto.mlRig import mlRig_dict
from japeto.mlRig import node
from japeto.libs import ordereddict

class BaseBlock(mlRig_dict.MlRigDict):
    def __init__(self, name, *args, **kwargs):
        super(BaseBlock, self).__init__(*args, **kwargs)

        self.__name  = name
        self.__nodes = ordereddict.OrderedDict()
        
    @property
    def name(self):
        return self.__name
    
    @property
    def nodes(self):
        return self.__nodes.values()

class Block(BaseBlock):
    def addNode(self, name, parent = None, child = None):
        node = node.Node(name)
        self.nodes
        if not self.has_key(name):
            if parent:
                if self.has_key(parent):
                    
                    return node
            else:
                self[name] = node
                return node   