'''
This is the Chain component.
    -Base component for the following Parts:
        -> Finger
        -> Spine
        -> Neck

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    August 2013
'''

#import python modules
import os
import sys

from maya import cmds

#import package modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import ikfk
from japeto.libs import control
from japeto.libs import transform
from japeto.libs import joint

from japeto.components import component

class Chain(component.Component):
    def __init__(self, name):
        super(Chain, self).__init__(name)
        
        self.__chainIkFk = None
        self.ikFkGroup   = str()
        self.fkJoints    = list()
        self.ikJoints    = list()
        self.blendJoints = list()
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Chain,self).initialize(**kwargs)
        
        self.addArgument('numJoints', 2, 2)
        self.addArgument('stretch', True, 3)
        
        self.addArgument('startJoint',
                '%s_start%s_%s_%s' % (self._getPrefix(),
                common.getDescription(self.name()),
                common.SKINCLUSTER,
                common.JOINT), 5)

        self.addArgument('endJoint',
                '%s_end%s_%s_%s' % (self._getPrefix(),
                common.getDescription(self.name()),
                common.SKINCLUSTER,
                common.JOINT), 6)
    
    @property
    def _ikfkChain(self):
        return self.__chainIkFk
        
    def setupRig(self):
        super(Chain, self).setupRig()
        
        self.skinClusterJnts = [self.startJoint, self.endJoint]
                
        if self._getSide() == common.LEFT:
            positions = (
            [self.position[0] + 2, self.position[1], self.position[2]],
            [self.position[0] + 9, self.position[1], self.position[2]]
            )
            
            aimCtrlPosition = [positions[0][0],
                    positions[0][1] + 5,
                    positions[0][2]]
        #end if    
        elif self._getSide() == common.RIGHT:
            positions = (
            [self.position[0] - 2, self.position[1], self.position[2]],
            [self.position[0] - 9, self.position[1], self.position[2]]
            )
            
            aimCtrlPosition = [positions[0][0],
                    positions[0][1] + 5,
                    positions[0][2]]
        #end elif    
            
        elif self._getSide() == common.CENTER:
            positions = (
            [self.position[0], self.position[1], self.position[2]],
            [self.position[0], self.position[1] + 9, self.position[2]]
            )
            
            aimCtrlPosition = [positions[0][0],
                    positions[0][1],
                    positions[0][2] + 5]
        #end elif
        print self.skinClusterJnts
        print positions
        for i,jnt in enumerate(self.skinClusterJnts):
            
            cmds.joint(n = jnt,position = positions[i])
            
            if i == 0:
                cmds.parent(jnt, self.skeletonGrp)
                #place Master Guide control in the same position
                #  as the first joint
                transform.matchXform(jnt,
                        common.getParent(self.masterGuide),
                        type = 'position')
            else:
                cmds.parent(jnt, self.skinClusterJnts[i - 1])
            #end if/else
                
            ctrl = self.setupCtrl(jnt.replace('_%s' % common.JOINT, ''),jnt)
            #create template control
            #control.createTemplate(ctrl)
            cmds.select(cl = True)
        #end loop
        

        # ----------------------------------------------------------------------
        # CREATE GUIDES
        startJointGuide = self.startJoint.replace(common.JOINT, common.GUIDES)
        endJointGuide   = self.endJoint.replace(common.JOINT, common.GUIDES)



        # ----------------------------------------------------------------------
        # ORIENTATION 
        #
        if self._getSide() == common.RIGHT:
            aimVectorAttr = attribute.switch ('aimVector',
                    node= self.masterGuide,
                    value=4,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])
            upVectorAttr  = attribute.switch ('upVector',
                    node=self.masterGuide,
                    value=3,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])
        else:
            aimVectorAttr = attribute.switch ('aimVector',
                    node=self.masterGuide,
                    value=1,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])

            upVectorAttr  = attribute.switch ('upVector',
                    node=self.masterGuide,
                    value=3,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])
        
        #create in-between joints and guides and make connections 
        step   = 1.0 / (self.numJoints - 1)
        parent = self.startJoint
        for i in range( 1, self.numJoints - 1 ):
            j = joint.create( name= '%s_%s_%s_%s_%s' % (self._getPrefix(),
                    common.getDescription(self.name()),
                    common.padNumber(i,3),
                    common.SKINCLUSTER,
                    common.JOINT))

            transform.matchXform( self.startJoint,j, type='rotate' )
            ctrl = self.setupCtrl(j.replace('_%s' % common.JOINT, ''),j)
            ctrlParent = common.getParent(ctrl)
            #create point constraint and figure out percentage for position
            constraint = cmds.pointConstraint( self.startJoint,
                    endJointGuide, ctrlParent )[0]

            weightAliasList = cmds.pointConstraint( constraint,
                    q=True,
                    weightAliasList=True)

            cmds.setAttr( '%s.%s' % (constraint, weightAliasList[0]), 1-(step*i) )
            cmds.setAttr( '%s.%s' % (constraint, weightAliasList[1]),  step*i )

            #adding the joint to skincluster joints list
            self.skinClusterJnts.insert(-1, j)
            cmds.parent(j, parent)
            parent = j

            if i == self.numJoints - 2:
                cmds.parent(self.endJoint, j)
                constraint = cmds.orientConstraint(j, self.endJoint)[0]
                #add constraints to setup constraint list
                self._addSetupConstraints(constraint)


        #create aim control
        aimLocator = self._createAimLocator(aimCtrlPosition,
                color = common.SIDE_COLOR_SECONDARY[self._getSide()])
        
        #create aim constraints
        for i, jnt in enumerate(self.skinClusterJnts):
            if jnt == self.endJoint:
                break
            constraint = cmds.aimConstraint(
                    self.skinClusterJnts[i+1].replace('_%s' % common.JOINT, '_%s' % common.GUIDES),
                    jnt,
                    worldUpType = "object",
                    worldUpObject = aimLocator)[0]

            attribute.connect(aimVectorAttr, '%s.aimVector' % constraint)
            attribute.connect(upVectorAttr, '%s.upVector' % constraint)
            #add constraints to setup constraint list
            self._addSetupConstraints(constraint)


    def rig(self):
        super(Chain, self).rig()
        self.__chainIkFk = ikfk.IkFk(self.startJoint,
            self.endJoint,
            name = self.name())

        self.__chainIkFk.create()
        self.ikFkGroup   = self.__chainIkFk.group
        self.fkJoints    = self.__chainIkFk.fkJoints
        self.ikJoints    = self.__chainIkFk.ikJoints
        self.blendJoints = self.__chainIkFk.blendJoints
        #----FK Setup---
        self.controls['fk'] = self._fkControlSetup(self.fkJoints)
        
            
    def postRig(self):
        super(Chain, self).postRig()
        #parent ikfk group to the rig grp
        cmds.parent(self.ikFkGroup, self.jointsGrp)
        
        cmds.setAttr('%s.ikfk' % self.ikFkGroup, 1) #<--- might change to IK
        
        #turn off visibility of joints
        for jnt in [self.fkJoints[0], self.ikJoints[0],self.blendJoints[0]]:
            cmds.setAttr('%s.v' % jnt, 0)

        #assign hooks
        self.hookRoot.extend([self.ikJoints[0],common.getParent(self.controls['fk'][0])])
        self.hookPoint.extend([self.blendJoints[-1]])
        
    def _fkControlSetup(self, joints):
        '''
        Creates FK control setup on the input joints
        
        Example:
            ...python:
                    self._fkControlSetup(["jnt1", "jnt2", "jnt3"])
                    #Return: ["ctrl1", "ctrl2", "ctrl3"]
                    
        @param joints: Joints to have controls drive
        @type joints: *list* or *tupple* or *str*
        
        
        '''
        joints = common.toList(joints)
        
        if not isinstance(joints, list) and not isinstance(joints, tuple):
            raise RuntimeError('%s must be a *list* or *tuple*' % joints)
        
        fkCtrls = list()
        parent = self.controlsGrp

        for jnt in joints:            
            ctrl = control.create(name= jnt.split('_%s' % common.JOINT)[0],
                    type = 'circle',
                    parent = parent,
                    color = common.SIDE_COLOR[self._getSide()])

            ctrlParent = common.getParent(ctrl)
            transform.matchXform(jnt, ctrlParent, type = 'pose')
            cmds.parentConstraint(ctrl, jnt, mo = True) #----> might change this to connect rotations and not use translation
            
            #connect visibility of shapes to foot control
            for shape in common.getShapes(ctrl):
                if self.ikFkGroup:
                    attribute.connect('%s.ikfk' % self.ikFkGroup,
                                      '%s.v' % shape)
                #end if
            #end loop

            parent = ctrl
            fkCtrls.append(ctrl)
        #end loop
            
        return fkCtrls
        
    def _createAimLocator(self, position = [0,0,0], color = None):
        #create aim locator and move into position
        aimLocator = \
            cmds.spaceLocator(n = '%s_aim_%s' % (self.name(), common.LOCATOR))[0]

        aimZero = \
            cmds.createNode('transform',
                    n = aimLocator.replace(common.LOCATOR, common.ZERO))

        cmds.parent(aimLocator, aimZero)
        cmds.xform(aimZero, ws = True, t = position)
        
        #create display line between aim locator and start joint
        displayLine = control.displayLine(self.startJoint, aimLocator)
        cmds.parent(displayLine, self.guidesGrp)
        
        
        #set color on aim control
        common.setColor(aimLocator, color)
        
        #parent locator to zero group
        cmds.parent(aimZero, self.masterGuide)
        
        
        return aimLocator
        
        