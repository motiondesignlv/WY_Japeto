from japeto.mlRig import mlRig_dict
from japeto.mlRig import block
import inspect

class Node(mlRig_dict.MlRigDict):
    __block__ = None
    
    def __init__(self, name, *args, **kwargs):
        self.__name = name
        
    @property
    def name(self):
        return self.__name
    
    @property
    def block(self):
        return self.__block__

    @block.setter
    def block(self, value):
        if isinstance(value, block.Block): 
            self.__block__ = value
    
    def setData(self, name, value, **kwargs):
        '''
        sets the data on the node based on key :value pairs and takes 
        additional keyword arguments to hand overloading of arguments 
        on the functions or classes.
        @example:
            >>> setData("Left Arm", limb.arm(), position = [20,10,10])
            
        @param name: Nice name for user interface
        @type name: *str*

        @param value: python object to be called when run() is called
        @type value: *method* or *function* or *class*
        '''
        if not len(self.keys()) < 1:
            raise RuntimeError('%s already has data on it. Must be setting %s. Try addArgument(key, value)' % (self.name, self.keys()[0]))
        
        self.add(name, (value,kwargs))
        
    def setAddress(self, address):
        return True
    
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
    
    def getParent(self):
        return True
    
    
    def execute(self):
        if len(self.keys()) < 1:
            return 
        print "in execute"
        objName = self.keys()[0]
        kwargs = self[objName][1]
        
        if inspect.isclass(self[objName][0]):
            obj = self[objName][0](objName)
            if isinstance(obj, component.Component):
                self._executeComponent(obj, **kwargs)
        elif inspect.isfunction(self[objName][0]):
            obj = self[objName][0](**kwargs)
            

    def _executeComponent(self, obj, **kwargs):
        obj.initialize(**kwargs)
        obj.runSetupRig()
        obj.runRig()
        print 'executed component %s' % obj.__class__.__name__
        
    def _executeFunction(self):
        return