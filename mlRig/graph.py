from japeto.mlRig import block
from japeto.mlRig import mlRig_dict
import inspect


class Graph(mlRig_dict.MlRigDict):
    def __init__(self, name, blocks = None, *args, **kwargs):
        '''
        This constructor for the class sets up the base graph attributes. 
        
        @param name: Name of the graph
        @type name: *str*
        
        @param blocks: Blocks that will be arranged on the graph
        @type blocks: *str* or *list* or *tuple* or *mlRig.block.Block*    
        '''
        super(Base,self).__init__(*args, **kwargs)
        
        self.__name = name
        
        try:
            if blocks:
                blocks = common.toList(blocks)
                for blk in blocks:
                    print blk
                #end loop
            #end if
        except:
            print 'No Blocks passed in. Graph is constructed.'
            
    @property
    def name(self):
        return self.__name
    
    def addBlock(self, name):
        pass
    
    def addNode(self, name, parent = None):
        #Construct and instance of the node object
        node = Node(name)
        if not self.has_key(name):
            if parent:
                if self.has_key(parent):
                    #index = self.keys().index(parent)
                    node = Node(name)
                    self[parent].update(node)
                    return node
            #end if
            else:
                self[name] = node
                return node
            #end else
        #end if