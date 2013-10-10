from japeto.libs import ordereddict

class MlRigDict(ordereddict.OrderedDict):
    def __init__(self, *args, **kwargs):
        super(Base,self).__init__(*args, **kwargs)
        
    def __repr__(self):
        '''
        This returns the dictionary as a string so people can see what's
        stored in the MlRigDict object.
        
        @example: 
            >>> mlDict = mlRig_dict.MlRigDict('one' = 1, 'two' = 2)
            >>> mlDict
            {'one':1, 'two':2}
        '''
        #get current keys and values
        keys = self.keys()
        values = self.values()
        
        #build you string to store keys:values
        reprStr = "{" 
        for k,v in zip(keys, values):
            if k == keys[-1]:
                reprStr = "%s'%s' : %s}" % (reprStr,k, v)    
                break
            #end if
            
            reprStr = "%s'%s' : %s, " % (reprStr,k, v)
        #end loop
        
        return reprStr
    
    
    def add(self, key, value, index = None):
        '''
        adds a key:value pair to the dictionary based on index.
        If no index is passed in, then it will just add it to 
        the end of the key:value pairs lists
        
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
            
            if index > len(self.keys()):
                if not self.has_key(key):
                    self.clear()
                    keys.append(key)
                    values.append(value)
                    for k,v in zip(keys, values):
                        self[k] = v
                    #end loop
                #end if
            #end if
            if not self.has_key(key):
                keys.insert(index,key)
                values.insert(index,value)
                self.clear()
                for k,v in zip(keys, values):
                    self[k] = v
                #end loop
            #end if
        #end if
        else:
            self[key] = value
        #end else