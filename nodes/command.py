'''
This is the base component for all the rig components

:author: Walter Yoder
:contact: walteryoder:gmail.com
:date: October 2012
'''

#import python modules

#import maya modules
import maya.cmds as cmds

#import package modules
#libs
from japeto.mlRig import ml_node

class Command(ml_node.MlNode):
    def __init__(self, name, parent = None):
        super(Command, self).__init__(name, parent)
        
        self.command = self.addAttribute("command", "#write your python code here", attrType = "code")
    
    def execute(self, **kwargs):
        for attr in self.attributes():
            if kwargs.has_key(attr.name()):
                exec(attr.value())