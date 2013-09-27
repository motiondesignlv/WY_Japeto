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
        self.controls['tweak'] = list()
        self.controls['ik'] = list()
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Spine,self).initialize(**kwargs)
        
        #TODO: Place builds arguments specific to the spine

    def setupRig(self):
        super(Spine, self).setupRig()
        
    def rig(self):
        component.Component.rig(self)
        #initialize the spine class (ribbon ik/fk setup)
        self.__spineIkFk = ikfk.IkFkRibbon(self.startJoint,
            self.endJoint,
            name = self.name)
        #create spine setup
        self.__spineIkFk.create()
        
        #declare variables for function
        self.ikFkGroup    = self.__spineIkFk.group
        self.ikJoints     = self.__spineIkFk.ikJoints
        self.fkJoints     = self.__spineIkFk.fkJoints
        self.blendJoints  = self.__spineIkFk.blendJoints
        self.driverJoints = self.__spineIkFk.driverJoints
        self.follicles    = self.__spineIkFk.follicles
        startDriverJnt    = self.__spineIkFk.driverJoints['start'][0]
        middleDriverJnt   = self.__spineIkFk.driverJoints['middle'][0]
        endDriverJnt      = self.__spineIkFk.driverJoints['end'][0]
        targetJoints      = self.__spineIkFk.targetJoints
        upAxis            = self.__spineIkFk.upAxis
        aimAxis           = self.__spineIkFk.aimAxis
        
        startDriverPos = cmds.xform(startDriverJnt,
                                    q = True,
                                    ws = True,
                                    t = True)
        middleDriverPos = cmds.xform(middleDriverJnt,
                                     q = True,
                                     ws = True,
                                     t = True)
        endDriverPos = cmds.xform(endDriverJnt,
                                  q = True,
                                  ws = True,
                                  t = True)
        
        #FK Control Setup
        self.controls['fk'] = self._fkControlSetup(self.__spineIkFk.fkJoints)        
        
        #IK Controls Setup
        startIkControl = control.create('%s_torso_%s_%s' % (self._getSide(),
                                                            common.IK,
                                                            common.padNumber(1, 3)
                                                            ),
                                        type = 'implicitSphere',
                                        parent = self.controlsGrp,
                                        color = common.SIDE_COLOR
                                        [self._getSide()])
        startIkControlZero = common.getParent(startIkControl)
        
        middleIkControl = control.create('%s_torso_%s_%s' % (self._getSide(),
                                                             common.IK,
                                                             common.padNumber(2, 3)
                                                             ),
                                         type = 'implicitSphere',
                                         parent = self.controlsGrp,
                                         color = common.SIDE_COLOR
                                         [self._getSide()])
        middleIkControlZero = common.getParent(middleIkControl)
        
        endIkControl = control.create('%s_chest_%s' % (self._getSide(),
                                                       common.IK,
                                                       ),
                                      type = 'implicitSphere',
                                      parent = self.controlsGrp,
                                      color = common.SIDE_COLOR
                                      [self._getSide()])
        endIkControlZero = common.getParent(endIkControl)
        
        #add ik controls to the controls dictionary in the "ik" key
        self.controls['ik'].extend([startIkControl,middleIkControl,endIkControl])
        
        #parent controls and joints
        cmds.xform(startIkControlZero, ws = True, t = startDriverPos)
        cmds.xform(middleIkControlZero, ws = True, t = middleDriverPos)
        cmds.xform(endIkControlZero, ws = True, t = endDriverPos)

        cmds.parent(startDriverJnt, startIkControl)
        cmds.parent(endDriverJnt, endIkControl)
        cmds.parent(middleIkControlZero, common.getParent(middleDriverJnt))
        cmds.parent(middleDriverJnt, middleIkControl)
        
        #create target controls
        for i,jnt in enumerate(targetJoints):
            tweakControl = control.create('%s_%s_%s' % (self.name,
                                                        common.TWEAK,
                                                        common.padNumber(i,3)
                                                        ),
                                          type = 'square',
                                          parent = self.controlsGrp,
                                          color = common.SIDE_COLOR_SECONDARY
                                          [self._getSide()])
            #get the parent of the control and reposition control
            tweakControlZero = common.getParent(tweakControl)
            jntPos = cmds.xform(jnt, q = True, ws = True, t = True)
            cmds.xform(tweakControlZero, ws = True, t = jntPos)
            cmds.parent(tweakControlZero, common.getParent(jnt))
            cmds.parent(jnt, tweakControl)
            self.controls['tweak'].append(tweakControl)#add to tweak list
        #end loop
        
        #-----------------------
        #Get tweak control rotations to work correctly.
        #@TODO: Still needs to be cleaned up. The aim isn't setup smoothly
        #----------------------
        tweakList  = [self.controls['tweak'][0],self.controls['tweak'][-1]]
        driverList = [middleDriverJnt, middleDriverJnt]
        
        for twk, drv in zip(tweakList, driverList):
            tweakParent = common.getParent(twk)
            tweakUpJnt = common.duplicate(twk,
                                          twk.replace('_%s_' % common.TWEAK,
                                                      '_%s_' % common.UP),
                                          common.getParent(tweakParent))
            cmds.xform(tweakUpJnt,ws = True, relative = True, 
                       t = [0,0,1])
            if twk == self.controls['tweak'][0]:
                aim = transform.AXES[aimAxis]
            else:
                aim = [a * -1 for a in transform.AXES[aimAxis]]
            
            #------NEED TO CLEAN THIS UP-----------
            cmds.aimConstraint(drv,tweakParent, aim = aim,
                               u = [0,0,1], 
                               worldUpType = 'object', 
                               worldUpObject = tweakUpJnt, skip=["x","y"])
            
            cmds.setAttr('%s.rotateOrder' % tweakParent, 1 )
        
    def postRig(self):
        super(Spine, self).postRig()
        
        cmds.setAttr('%s.v' % self.__spineIkFk.surface, 0)
        reverse = cmds.createNode('reverse', n = '%s_%s' % (self.name, common.REVERSE))
        attribute.connect('%s.ikfk' % self.ikFkGroup, '%s.inputX' % reverse)
        for ctrl in self.controls['ik']:
            for shape in common.getShapes(ctrl):
                if shape and cmds.objExists(shape):
                    attribute.connect('%s.outputX' % reverse, '%s.v' % shape)
                #end if
            #end loop
        #end loop
        for v in self.driverJoints.values():
            for jnt in v:
                if cmds.objExists(jnt):
                    cmds.setAttr('%s.v' % jnt, 0)
                #end if
            #end loop
        #end loop
        for follicle in self.follicles:
            if common.isValid(follicle):
                cmds.setAttr('%s.v' % common.getShapes(follicle, 0), 0)
            #end if
        #end loop
        
        tweakAttribute = attribute.addAttr(self.ikFkGroup, 'ikTweakCtrls',
                                               'enum', True, ['off','on'],0)
            
        for ctrl in self.controls['tweak']:
            if common.isValid(ctrl):
                shapes = common.getShapes(ctrl)
                if shapes:
                    for shape in shapes:
                        attribute.connect(tweakAttribute, '%s.v' % shape)
                    #end loop
                #end if
            #end if
        #end loop
        
        for jnt in [self.__spineIkFk.upJoint, self.__spineIkFk.aimJoint]:
            cmds.setAttr('%s.overrideEnabled' % jnt, 1)
            cmds.setAttr('%s.overrideLevelOfDetail' % jnt, 1)
        
        for jnt in self.__spineIkFk.targetJoints:
            if common.isValid(jnt):
                cmds.setAttr('%s.v' % jnt, 0)
            #end if
        #end loop
        
        cmds.setAttr('%s.ikfk' % self.ikFkGroup, 0)