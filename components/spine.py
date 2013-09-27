'''
This is the Spine component.

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
from japeto.libs import curve
from japeto.libs import surface
reload(ikfk)
reload(common)

from japeto.components import component
from japeto.components import chain
reload(chain)

class Spine(chain.Chain):
    def __init__(self, name):
        super(Spine, self).__init__(name)
        self.__spineIkFk = str()
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Spine,self).initialize(**kwargs)
        
        #TODO: Place builds arguments specific to the spine

    def setupRig(self):
        super(Spine, self).setupRig()
        
    def rig(self):
        component.Component.rig(self)
        self.__spineIkFk = ikfk.IkFkRibbon(self.startJoint,
            self.endJoint,
            name = self.name)
        
        self.__spineIkFk.create()
        self.ikFkGroup = self.__spineIkFk.group
        
        #FK Control Setup
        fkCtrls = self._fkControlSetup(self.__spineIkFk.fkJoints)        
        
        #IK Controls Setup
        #startIkControl = control.create(self.ikJoints[0].replace('_%s_' % common.JOINT, '_%s_' % common.CONTROL), type = 'circle', parent = None, color = 'yellow')