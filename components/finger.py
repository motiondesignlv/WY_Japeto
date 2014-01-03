'''
This is the Finger component.

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    August 2013
'''

#import python modules
import maya.cmds as cmds

#import package modules
from japeto.libs import common
from japeto.libs import control

from japeto.components import component
from japeto.components import  chain

class Finger(chain.Chain):
    def __init__(self, name):
        super(Finger, self).__init__(name)
        
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Finger,self).initialize(**kwargs)
        
    def setupRig(self):
        if super(Finger, self).setupRig():
            return True

        if self._getSide() == common.LEFT:
            cmds.xform(common.getParent(self.endJoint.replace(common.JOINT, common.GUIDES)), r = True, t = [-4.0, 0, 0])
        elif self._getSide() == common.RIGHT:
            cmds.xform(common.getParent(self.endJoint.replace(common.JOINT, common.GUIDES)), r = True, t = [4.0, 0, 0])
        
    def rig(self):
        super(Finger, self).rig()
        
        for ctrl in self.controls['fk']:
            control.scaleShape(ctrl,scale = [self.controlScale  * .5,self.controlScale *.5,self.controlScale * .5])