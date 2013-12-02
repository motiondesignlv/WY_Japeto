'''
Attribute will track and manage all data with-in an attribute
'''

class MlAttribute(object):
    '''
    Base Attribute to manage all data for nodes
    
    '''
    __attrTypes__ = (bool, basestring, int, float, list, tuple)
    @classmethod
    def isValid(cls, attr):
        if not isinstance(attr, Attribute):
            return False
        
        return True
    
    @classmethod
    def inValidError(cls, attr):
        raise TypeError("%s is not of type japeto.mlRig.attribute.Attribute" % attr)
    
    def __init__(self, longName = None, shortName = None, value = None, *args, **kwargs):
        super(MlAttribute, self).__init__(*args, **kwargs)
        self.__name        = longName
        self.__shortName   = shortName
        self.__value       = value
        self.__storable    = True
        self.__connectable = True
        self.__type        = type(self.__value).__name__
    
    def attrType(self):
        return self.__type
    
    def __repr__(self):
        return "< %s %s >" % (self.__class__.__name__, self.__type)
        
    def name(self):
        '''
        Long Name of attribute
        '''
        return self.__name
    
    def shortName(self):
        return self.__shortName
    
    def delete(self):
        '''
        Deletes attribute
        '''
        del self
    
    def create(self, longName, shortName, type, value):
        if not type in Attribute.__attrTypes__:
            raise TypeError('%s must be one of the following types: %s' % (type, str(*Attribute.__attrTypes__)))
        
        self.__name      = longName
        self.__shortName = shortName
        self.__type      = type
        
    def setStorable(self, value):
        self.__storable = _setBool(value)
        
    def setConnectable(self, value):
        self.__connectable = _setBool(value)
        
    def _setBool(self, value):
        if not isinstance(value, bool):
            raise TypeError("%s must be <type 'bool'>" % value)
        
        if value:
            return True
        
        return False 
        