'''
This is the Finger component.

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    August 2013
'''

#import python modules
import os
import sys

import maya.cmds as cmds
import japeto 

#import package modules
from japeto.libs import common, attribute, ikfk, control, transform, joint
import japeto.components.component as component
import japeto.components.chain as chain

class Finger(chain.Chain):
    def __init__(self, name):
        super(Finger, self).__init__(name)
        
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Finger,self).initialize(**kwargs)
        
    def setupRig(self):
        super(Finger, self).setupRig()

	#TODO: Put setup code here
	if self._getSide() == common.LEFT:
	    cmds.xform(common.getParent(self.endJoint.replace(common.JOINT, common.GUIDES)), r = True, t = [-4.0, 0, 0])
	elif self._getSide() == common.RIGHT:
	    cmds.xform(common.getParent(self.endJoint.replace(common.JOINT, common.GUIDES)), r = True, t = [4.0, 0, 0])
	    
    def rig(self):
        super(Finger, self).rig()
        
        
        