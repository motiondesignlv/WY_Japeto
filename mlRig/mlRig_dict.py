from japeto.libs import ordereddict

class MlRigDict(ordereddict.OrderedDict):
    def __init__(self, *args, **kwargs):
        super(MlRigDict,self).__init__(*args, **kwargs)
        
    def __repr__(self):
        '''
        This returns the dictionary as a string so people can see what's
        stored in the MlRigDict object.
        
        @example: 
            >>> mlDict = mlRig_dict.MlRigDict('one' = 1, 'two' = 2)
            >>> print mlDict
            {'one':1, 'two':2}
        '''
        #get current keys and values
        keys = self.keys()
        values = self.values()
        
        #build you string to store keys:values
        _str = "{"
        if not keys or not values:
            return  '%s}' % _str
        
        for k,v in zip(keys, values):
            if k == keys[-1]:
                _str = "%s'%s' : %s}" % (_str,k, v)    
                break
            #end if
            
            _str = "%s'%s' : %s, " % (_str,k, v)
        #end loop
        
        return _str
    '''
    def __repr__(self):             
        return "< %s >" % (self.__class__.__name__)
    '''
    
    def add(self, key, value, index = None):
        '''
        adds a key:value pair to the dictionary based on index.
        If no index is passed in, then it will just add it to 
        the end of the key:value pairs lists
        
        @example:
            >>> mlDict = mlRig_dict.MlRigDict('one' = 1, 'two' = 2)
            >>> mlDict.add(key = 'three', value = 3)
            {'one':1, 'two':2, 'three' : 3}
            
        
        @example:
            >>> mlDict = mlRig_dict.MlRigDict('one' = 1, 'two' = 2)
            >>> mlDict.add(key = 'three', value = 3, index = 1)
            {'one':1, 'three' : 3, 'two':2}
        
        @param key: Name for the key in the dictionary
        @type key: *str*
        
        @param value: Value to go in the value for the key
        @type value: *str* *int* *float* *list* *tuple* *dict*
                     *function* *method* *class* 
        
        @param index: Position in the list of key:value pairs you want
                      your pair to be ordered.
        @type index: *int*  
        '''
        #check if there are keys
        if self.keys():
            #get keys and values
            keys = self.keys()
            values = self.values()
            #if no key in self append key and value to end of lists
            if not self.has_key(key):
                #check length of keys against index
                if index > len(self.keys()):
                    keys.append(key)
                    values.append(value)
                #end if
            #end if
                else: 
                    keys.insert(index,key)
                    values.insert(index,value)
            #end if
            elif self.has_key(key):
                self.move(key, index)
                if value != self[key]:
                    self[key] = value
                return
            #clear self and rebuild in new order
            self.clear()
            for k,v in zip(keys, values):
                self[k] = v
            #end loops
        #end if
        else:
            self[key] = value
        #end else
        
    def move(self, key, index):
        '''
        This will move the key based on the input index argument
        
        @param key: Key value you want to reorder
        @type key: *str*
        
        @param index: Index in the self.keys() list where you would like you
                      key placed
        @type index: *int* 
        '''
        if not self.has_key(key):
            raise KeyError('%s is not a valid key in %s' % (key, self))
        
        if self.keys():
            #get keys and values
            keys = self.keys()
            values = self.values()
        
        #get key and value from index
        originalIndex = keys.index(key)
        #pop key and value out of lists
        key = keys.pop(originalIndex)
        value = values.pop(originalIndex)
        #insert key and value into list
        keys.insert(index, key)
        values.insert(index, value)
        self.clear() #clear dict
        for k,v in zip(keys, values):
            self[k] = v