'''
Attribute will track and manage all data with-in an attribute
'''

class MlAttribute(object):
    '''
    Base Attribute to manage all data for nodes
    
    '''
    __attrTypes__ = (bool, basestring, str, int, float, list, tuple)
    @classmethod
    def isValid(cls, attr):
        if not isinstance(attr, cls):
            return False
        
        return True
    
    @classmethod
    def inValidError(cls, attr):
        raise TypeError("%s is not of type japeto.mlRig.attribute.Attribute" % attr)
    
    def __init__(self, longName = None, shortName = None, value = None, attrType = None, *args, **kwargs):
        super(MlAttribute, self).__init__()
        self.__name        = longName
        self.__shortName   = shortName
        self.__value       = value
        self.__storable    = True
        self.__connectable = True
        if not attrType:
            self.__type = type(self.__value).__name__
        else:
            self.__type = attrType
    
    def attrType(self):
        return self.__type
    
    def setAttrType(self, value):
        self.__type = value
    
    def __repr__(self):
        return "< %s %s >" % (self.__class__.__name__, self.__type)
        
    def name(self):
        '''
        Long Name of attribute
        '''
        return self.__name
    
    def shortName(self):
        return self.__shortName
    
    def setValue(self, value):
        if not type(value).__name__ not in self.__attrTypes__:
            raise TypeError('%s needs to be one of the following types: %s' % (value, self.__attrTypes__))
        
        #build the command
        if isinstance(value, basestring):
            cmd = "self._set%s('%s')" % (type(value).__name__.title(), value)
        else:
            cmd = 'self._set%s(%s)' % (type(value).__name__.title(), value)
            
        #execute the command
        value = eval(cmd)
        
        self.__value = value #set the value
        
    def value(self):
        return self.__value
    
    def delete(self):
        '''
        Deletes attribute
        '''
        del self
    
    def create(self, longName, shortName, attrType, value):
        if not attrType in MlAttribute.__attrTypes__:
            raise TypeError('%s must be one of the following types: %s' % (attrType, str(*MlAttribute.__attrTypes__)))
        
        self.__name      = longName
        self.__shortName = shortName
        self.__type      = attrType
        
    def setStorable(self, value):
        self.__storable = self._setBool(value)
        
    def setConnectable(self, value):
        self.__connectable = self._setBool(value)
        
    #---------------------------------------------
    #Set attribute type values
    #---------------------------------------------
    def _setBool(self, value):
        if not isinstance(value, bool):
            raise TypeError("%s must be <type 'bool'>" % value)
        
        if value:
            return True
        
        return False 
    
    def _setStr(self, value):
        if not isinstance(value, basestring):
            raise TypeError("%s must be <type 'str'>" % value)

        return str(value)
    
    def _setFloat(self, value):
        if not isinstance(value, float):
            raise TypeError("%s must be <type 'float'>" % value)
        
        return float(value)
    
    def _setInt(self, value):
        if not isinstance(value, int):
            raise TypeError("%s must be <type 'int'>" % value)
        
        return int(value)
    
    def _setList(self, value):
        if not isinstance(value, list):
            raise TypeError("%s must be <type 'list'>" % value)

        return list(value)
    
    def _setTuple(self, value):
        if not isinstance(value, tuple):
            raise TypeError("%s must be <type 'tuple'>" % value)

        return tuple(value)

        