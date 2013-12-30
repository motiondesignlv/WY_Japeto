'''
This is the Neck component.

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    September 2013
'''
#import maya modules
from maya import cmds

#import package modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import ikfk
from japeto.libs import control
from japeto.libs import transform
from japeto.libs import joint

from japeto.components import spine

class Neck(spine.Spine):
    def __init__(self, name):
        super(Neck, self).__init__(name)
        
    def setupRig(self):
        super(Neck, self).setupRig()
        '''
        ..todo: still need to flesh out setup for neck
        '''
        endJointGuide   = self.endJoint.replace(common.JOINT, common.GUIDES)
        if not cmds.objExists(endJointGuide):
            return
        
        cmds.xform(common.getParent(endJointGuide), ws = True, r = True, t = [0,-5, 0])
