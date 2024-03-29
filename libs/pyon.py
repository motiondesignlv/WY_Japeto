'''
pyon data library

'''

#Import python modules
import os
import tempfile
import inspect
import japeto.mlRig.ml_node as node
from japeto.libs import ordereddict
# ------------------------------------------------------------------------------
# Create custom encoder
#
class Encoder( object ):

    def __init__( self, indent=4, precision = 3 ):
        
        self.indent    = indent
        self.precision = precision
        self.__depth__ = 0
        
    # --------------------------------------------------------------------------
    
    def encode_none( self, obj ):
        return 'None'

    def encode_bool( self, obj ):
        return 'True' if obj else 'False'

    def encode_int( self, obj ):
        return '%i' % obj
    
    def encode_float( self, obj ):
        #return '%.3f' % obj
        return ('%.' + str(self.precision) + 'f') % obj

    def encode_str( self, obj ):
        return '"%s"' % obj

    def encode_unicode( self, obj ):
        return '"%s"' % obj

    def encode_tuple( self, obj ):

        items = range( len( obj ) )
        for i, value in enumerate( obj ):
            items[i] = self.encode( value )
        return '(%s)' % ', '.join(items)

    def encode_list( self, obj ):

        items = range( len( obj ) )
        for i, value in enumerate( obj ):
            items[i] = self.encode( value )
        return '[%s]' % ', '.join(items)
    
    def encode_ordereddict(self):
        items = range( len( obj ) )
        for i,k in enumerate(obj.keys()):
            items[i] = '%s%s: %s' % ( ' '*self.indent*self.__depth__, self.encode( k ), self.encode( obj[k] ) )
        self.__depth__ -= 1
        
    def encode_dict( self, obj ):

        items = range( len( obj ) )
        for i,k in enumerate(obj.keys()):
            items[i] = '%s%s: %s' % ( ' '*self.indent*self.__depth__, self.encode( k ), self.encode( obj[k] ) )
        self.__depth__ -= 1
        
        return '\n%s{\n%s\n%s}' % (' '*self.indent*self.__depth__, ',\n'.join(items), ' '*self.indent*self.__depth__ )
    
    def encode_method( self, obj ):
        '''
        @todo: Figure out how we really want to write this out
        @warning: Still a WIP. Would not use this yet.
        '''
        return '%s.%s.%s' % (str(obj.__self__.__module__), str(obj.__self__.__class__.__name__), str(obj.__func__.__name__))
    
    
    def encode_node( self, obj ):

        items = range( len( obj ) )
        for i,k in enumerate(obj.keys()):
            if isinstance(obj[k],node.MlNode):
                items[i] = '%snode %s: %s' % ( ' '*self.indent*self.__depth__, self.encode( k ), self.encode( obj[k] ) )
            else:
                items[i] = '%s%s: %s' % ( ' '*self.indent*self.__depth__, self.encode( k ), self.encode( obj[k] ) )
        self.__depth__ -= 1
        
        return '\n%s{\n%s\n%s}' % (' '*self.indent*self.__depth__, ',\n'.join(items), ' '*self.indent*self.__depth__ )
    # --------------------------------------------------------------------------

    def encode( self, obj ):
        '''
        Checks the type of python object it is and calls the 
        encode method that matches.
        
        @param obj: Python object to check
        @type obj: *str* *int* *float* *bool* *list* *tuple*
                   *dict* *method* 
        '''
        if isinstance( obj, bool ):
            return self.encode_bool( obj )

        elif isinstance( obj, int ):
            return self.encode_int( obj )

        # Parse float
        elif isinstance( obj, float ):
            return self.encode_float( obj )

        elif isinstance( obj, str ):
            return self.encode_str( obj )

        elif isinstance( obj, unicode ):
            return self.encode_unicode( obj )

        # Parse tuple
        elif isinstance( obj, tuple ):
            return self.encode_tuple( obj )

        # Parse list
        elif isinstance( obj, list ):
            return self.encode_list( obj )

        #Parse node
        elif isinstance(obj,node.MlNode):
            self.__depth__ += 1
            return self.encode_node(obj)            
        
        # Parse dict
        elif isinstance( obj, dict ):
            self.__depth__ += 1
            return self.encode_dict( obj )
        
        #Parse method
        elif inspect.ismethod(obj):
            return self.encode_method(obj)
# ------------------------------------------------------------------------------

def dump( data ):
    '''Converts the data to string using pyon parser
    '''
    return Encoder().encode( data ) 

def save( data, filepath=None ):
    '''Write to file with python encoding.
    
    Example:
        .. python::
            data = { 'joint1': [0,0,0], 'joint2': [90,0,0] }
	    save( data )

    :param data: Python dictionary to be dumped in a file
    :type data: *str*
    :param filepath: Optional filepath for your file. If **None**, it will be saved in a temporary location 
    :type filepath: *str*
    :param precision: Float precision.
    :type precision: *int*
    :param sort: Sort dictionary keys.
    :type sort: *bool*
    '''
    
    if filepath == None:
        filepath = os.path.join( tempfile.gettempdir(), 'data.pyon' )

    # Dump data
    f       = open( filepath, 'w' )
    newData = dump( data )
    f.write(newData)
    f.close()

    return filepath

def load( filepath ): 
    '''Read file decoding with pyson and return it as Python dictionary.
    
    Example:
        ..python::
            load( filepath = '/sl/shows/TEMBO/users/work.wyoder/scripts/myPyonFile' )

    :param filepath: file path and name of file
    :type filepath: *str*
    '''
    
    if not os.path.isfile( filepath ):
        raise IOError, 'File not found: "%s"' % filepath

    # Read data
    f    = open( filepath,'r' )
    data = eval( f.read() ) 
    f.close()
    
    return data
