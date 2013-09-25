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

import maya.cmds as cmds
import japeto 

#import package modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import ikfk
from japeto.libs import control
from japeto.libs import transform
from japeto.libs import joint
reload(ikfk)

from japeto.components import component

class Chain(component.Component):
    def __init__(self, name):
        super(Chain, self).__init__(name)
        
        self.__chainIkFk = None
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Chain,self).initialize(**kwargs)
        
        self.addArgument('startJoint',
                '%s_start%s_%s_%s' % (self._getPrefix(),
                common.getDescription(self.name),
                common.SKINCLUSTER,
                common.JOINT))

        self.addArgument('endJoint',
                '%s_end%s_%s_%s' % (self._getPrefix(),
                common.getDescription(self.name),
                common.SKINCLUSTER,
                common.JOINT))

        self.addArgument('numJoints', 5)
        self.addArgument('stretch', True)
    
    @property
    def _ikfkChain(self):
        return self.__chainIkFk
        
    def setupRig(self):
        super(Chain, self).setupRig()
        
        self.skinClusterJnts.extend([self.startJoint, self.endJoint])
                
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
            j = joint.create( name= '%s_%s_%s_%s_%s' % (self._getSide(),
                    common.getDescription(self.name),
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
            name = self.name)

        self.__chainIkFk.create(stretch = True)
        
        #parent ikfk group to the rig grp
        cmds.parent(self.__chainIkFk.group, self.jointsGrp)
        
        
        #----FK Setup---
        fkCtrls = list()
        parent = self.controlsGrp

        for jnt in self.__chainIkFk.fkJoints:            
            ctrl = control.create(name= jnt.split('_%s' % common.JOINT)[0],
                    type = 'circle',
                    parent = parent,
                    color = common.SIDE_COLOR[self._getSide()])

            ctrlParent = common.getParent(ctrl)
            transform.matchXform(jnt, ctrlParent, type = 'pose')
            cmds.parentConstraint(ctrl, jnt, mo = True) #----> might change this to connect rotations and not use translation
            
            #connect visibility of shapes to foot control
            for shape in common.getShapes(ctrl):
                attribute.connect('%s.ikfk' % self.__chainIkFk.group,
                        '%s.v' % shape)

            #end for

            parent = ctrl
            fkCtrls.append(ctrl)
            
        cmds.setAttr('%s.ikfk' % self.__chainIkFk.group, 1) #<--- might change to IK
        
        #turn off visibility of joints
        for jnt in [self.__chainIkFk.fkJoints[0], self.__chainIkFk.ikJoints[0],self.__chainIkFk.blendJoints[0]]:
            cmds.setAttr('%s.v' % jnt, 0)

        #assign hooks
        self.hookRoot.extend([self.__chainIkFk.ikJoints[0],
                common.getParent(fkCtrls[0])])
        self.hookPoint.extend([self.__chainIkFk.blendJoints[-1]])
        
    def _createAimLocator(self, position = [0,0,0], color = None):
        #create aim locator and move into position
        aimLocator = \
            cmds.spaceLocator(n = '%s_aim_%s' % (self.name, common.LOCATOR))[0]

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
        
        