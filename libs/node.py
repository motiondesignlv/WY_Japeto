'''
This is the node module for all the node class
    ->Curve
    ->Surface
    ->etc....

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: September 2013
'''

#import maya modules
import maya.cmds as cmds
import maya.mel as mel

#import package modules
from japeto.libs import common

class Node(object):
    def __init__(self, name = str(), **kwargs):
        self._name         = name
        self._fullPathName = str()
    
    #---------------
    #GETTERS
    #---------------
    @property    
    def name(self):
        return self._name
    
    @property
    def fullPathName(self):
        if self._name:
            self._fullPathName = common.fullPathName(self._name)
            #end if
        #end if
                
        return self._fullPathName

    @name.setter
    def name(self, value):
        if not isinstance(value, basestring):
            raise ValueError('%s must be a *str* or *unicode* object' % value)
        #end if
        
        if self._name:
            if cmds.objExists(self._name):
                cmds.rename(self._name, value)
            #end if
        #end if
        
        self._name = value
        self._fullPathName = common.fullPathName(self._name)
        
    def delete(self):
        if cmds.objExists(self.fullPathName):
            cmds.delete(self.fullPathName)
            