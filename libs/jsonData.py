import json
import sys
import os

def dump(data):
    '''
    encodes python data to json data
    @param data:
    '''
    
    if isinstance(data, dict):
        return json.dumps(data, sort_keys = True, indent = 4)
    else:
        raise TypeError('%s must be of type dict()' % data)
        

def save(data, filepath = None):
    '''
    saves data out to a json file
    
    @param data:
    @param filepath:
    '''
    f = open(filepath, 'w')
    newData = dump(data)
    f.write( newData ) 
    f.close()
    
    return filepath
    

def load(filepath):
    """

    @param filepath:
    @return:
    """
    f = open(filepath, 'r')
    
    data = json.loads( f.read() )
    f.close()
    
    return data



