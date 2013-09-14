'''
This is the biped template for all the biped characters

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: Sepember 2013
'''

#import python modules
import inspect
import copy
import sys
import os

#import maya modules
import maya.cmds as cmds

#import package modules
import japeto

import japeto.templates.rig as rig
reload(rig)
#import libs
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import joint
from japeto.libs import control

#import components
from japeto.components import component
from japeto.components import limb
from japeto.components import leg
from japeto.components import arm
from japeto.components import foot
from japeto.components import chain
from japeto.components import finger
from japeto.components import hand


class Biped(rig.Rig):
    def __init__(self, name):
        super(Biped, self).__init__(name)

        self.__rootJoint = '%s_root_%s_%s' % (common.CENTER,
            common.SKINCLUSTER,
            common.JOINT)

        self.__hipJoint = '%s_hip_%s_%s' % (common.CENTER,
            common.SKINCLUSTER,
            common.JOINT)

    @property
    def rootJoint(self):
        return self.__rootJoint

    @property
    def hipJoint(self):
        return self.__hipJoint

    def initialize(self):
        '''
        this where you register you Modules and Functions to the build
        '''
        super(Biped,self).initialize()
        #center
        self.register('Spine',
            chain.Chain('c_spine'),
            position = [0,15,0],
            numJoints = 4)

        #left side
        self.register('Left Leg',
            leg.Leg('l_leg'),
            position = [1, 0 ,0 ],
            parent = 'c_startspine_sc_jnt')

        self.register('Left Foot',
            foot.Foot('l_foot'),
            position = [1,0,0],
            parent = 'l_tipLeg_sc_jnt')

        self.register('Left Arm',
            arm.Arm('l_arm'),
            position = [0,25,0],
            parent = 'c_endspine_sc_jnt')

        self.register('Left Hand',
            hand.Hand('l_hand'),
            position = [0,25,0],
            parent = 'l_tipArm_sc_jnt')

        #right side
        self.register('Right Leg',
            leg.Leg('r_leg'),
            position = [-1, 0, 0],
            parent = 'c_startspine_sc_jnt')

        self.register('Right Foot',
            foot.Foot('r_foot'),
            position = [-1,0,0],
            parent = 'r_tipLeg_sc_jnt')

        self.register('Right Arm',
            arm.Arm('r_arm'),
            position = [0,25,0],
            parent = 'c_endspine_sc_jnt')

        self.register('Right Hand',
            hand.Hand('r_hand'),
            position = [0,25,0],
            parent = 'r_tipArm_sc_jnt')

    def mirror(self, side = common.LEFT):
        super(Biped, self).mirror(side)
        super(Biped, self).mirror(side)

    def preBuild(self):
        '''
        Set up the scene for the build
        '''
        super(Biped, self).preBuild()
        pass

    def build(self):
        super(Biped,self).build()

        spineCtrlSize = self.components['Spine'].controlScale

        #create the root joint and control
        joint.create(self.rootJoint,
            position = self.components['Spine'].position)

        cmds.parent(self.rootJoint, self.jointsGrp)

        rootCtrl = control.create(self.rootJoint.replace('_%s' % common.JOINT,''),
            type = 'square',
            parent = self._trsCtrl,
            color = 'yellow')

        control.scaleShape(rootCtrl,
            scale = [spineCtrlSize + 2,
                    spineCtrlSize + 2,
                    spineCtrlSize + 2])

        cmds.xform(common.getParent(rootCtrl),
            ws = True,
            t = self.components['Spine'].position)

        cmds.parentConstraint(rootCtrl,
            self.rootJoint,
            mo = True)

        #create the hip joint and control
        joint.create(self.hipJoint,
            position = self.components['Spine'].position)

        cmds.parent(self.hipJoint,self.jointsGrp)

        hipCtrl = control.create(self.hipJoint.replace('_%s' % common.JOINT, ''),
            type = 'square',
            parent = rootCtrl,
            color = 'yellow')

        control.scaleShape(hipCtrl,
            scale = [spineCtrlSize + 1,
            spineCtrlSize + 1,
            spineCtrlSize + 1])

        cmds.xform(common.getParent(hipCtrl), ws = True, t = self.components['Spine'].position)
        cmds.parentConstraint(hipCtrl, self.hipJoint, mo = True)

        #connect fingers
        leftFingers = self.components['Left Hand'].getFingers
        for finger in self.components['Left Hand'].fingers:
            cmds.parent(leftFingers[finger].controlsGrp, self.controlsGrp)
            cmds.parent(leftFingers[finger].jointsGrp, self.jointsGrp)
            cmds.delete(cmds.parent(leftFingers[finger].rigGrp))

        rightFingers = self.components['Right Hand'].getFingers
        for finger in self.components['Right Hand'].fingers:
            cmds.parent(rightFingers[finger].controlsGrp, self.controlsGrp)
            cmds.parent(rightFingers[finger].jointsGrp, self.jointsGrp)
            cmds.delete(cmds.parent(rightFingers[finger].rigGrp))

        #connect left ikfk attributes to the leg
        cmds.setAttr('%s.ikfk' % self.components['Left Leg'].ikfkGroup, l = False)
        attribute.connect('%s.ikfk' % self.components['Left Foot'].footCtrl, '%s.ikfk' % self.components['Left Leg'].ikfkGroup)

        #connect right ikfk attributes to the leg
        cmds.setAttr('%s.ikfk' % self.components['Right Leg'].ikfkGroup, l = False)
        attribute.connect('%s.ikfk' % self.components['Right Foot'].footCtrl, '%s.ikfk' % self.components['Right Leg'].ikfkGroup)

        #copy and connect attributes from foot control to the ik control
        for part in [self.components['Left Foot'], self.components['Right Foot']]:
            for attrPath in part.footRollAttrs:
		attrPathSplit = attrPath.split('.')
		node = attrPathSplit[0]
		attr = attrPathSplit[1]
            if attr == 'ikfk':
                continue
            #end if

            if cmds.objExists(attrPath):
                if part._getSide() == common.LEFT:
		    attribute.copy(attr, node, destination = self.components['Left Leg'].controls['ik'][0], connect = True,reverseConnect = False)
                elif part._getSide() == common.RIGHT:
		    attribute.copy(attr, node, destination = self.components['Right Leg'].controls['ik'][0], connect = True,reverseConnect = False)
		    attribute.hide(attrPath)

        #setup ikfk attr on the arms
        for part in [self.components['Right Hand'], self.components['Left Hand']]:
            if part._getSide() == common.LEFT:
                cmds.setAttr('%s.ikfk' % self.components['Left Arm'].ikfkGroup, l = False)
                attribute.copy('ikfk', self.components['Left Arm'].ikfkGroup, destination = part.handCtrl, connect = True,reverseConnect = False)
            elif part._getSide() == common.RIGHT:
                cmds.setAttr('%s.ikfk' % self.components['Right Arm'].ikfkGroup, l = False)
                attribute.copy('ikfk', self.components['Right Arm'].ikfkGroup, destination = part.handCtrl, connect = True,reverseConnect = False)


        for part in [self.components['Left Leg'], self.components['Right Leg']]:
            for shape in common.getShapes(part.controls['fk'][-1]):
	        attrPath = '%s.v' % shape
		attrConnections = attribute.getConnections (attrPath, incoming = True, outgoing = False, plugs = True)
            if attrConnections:
                for attr in attrConnections:
		    cmds.disconnectAttr(attr,attrPath)

            cmds.setAttr(attrPath, 0)


    def postBuild(self):
        super(Biped, self).postBuild()
        pass

    def connectHooks(self):
        #delete constraints that are no longer needed
        cmds.delete(cmds.listRelatives(self.components['Left Foot'].hookRoot[-1],c = True, type = 'constraint'))
        cmds.delete(cmds.listRelatives(self.components['Right Foot'].hookRoot[-1],c = True, type = 'constraint'))
        cmds.delete(cmds.listRelatives(self.components['Left Leg'].hookRoot[-1],c = True, type = 'constraint'))
        cmds.delete(cmds.listRelatives(self.components['Right Leg'].hookRoot[-1],c = True, type = 'constraint'))

        #connect arms and hands
        for hook in self.components['Left Hand'].hookRoot:
            cmds.parentConstraint(self.components['Left Arm'].hookPoint[0], hook, mo = True)
        for hook in self.components['Right Hand'].hookRoot:
            cmds.parentConstraint(self.components['Right Arm'].hookPoint[0], hook, mo = True)

        #spine to arms
        cmds.parentConstraint(self.components['Spine'].hookPoint[0], self.components['Left Arm'].hookRoot[0], mo = True)
        cmds.parentConstraint(self.components['Spine'].hookPoint[0], self.components['Right Arm'].hookRoot[0], mo = True)

        #hip to legs
        cmds.parentConstraint(self.hipJoint, self.components['Left Leg'].hookRoot[0], mo = True)
        cmds.parentConstraint(self.hipJoint, self.components['Right Leg'].hookRoot[0], mo = True)

        #root to spine
        cmds.parentConstraint(self.rootJoint, self.components['Spine'].hookRoot[0],mo = True)
        cmds.parentConstraint(self.rootJoint, self.components['Spine'].hookRoot[1],mo = True)

        #legs to feet
        cmds.parentConstraint(self.components['Left Leg'].hookPoint[0], self.components['Left Foot'].hookRoot[1], mo = True)
        cmds.parentConstraint(self.components['Right Leg'].hookPoint[0], self.components['Right Foot'].hookRoot[1], mo = True)
        cmds.parentConstraint(self.components['Right Leg'].hookRoot[2], self.components['Right Foot'].hookRoot[0], mo = True)
        cmds.parentConstraint(self.components['Left Leg'].hookRoot[2], self.components['Left Foot'].hookRoot[0], mo = True)

        #feet to legs
        cmds.parentConstraint(self.components['Left Foot'].hookPoint[0], self.components['Left Leg'].hookRoot[-1], mo = True)
        cmds.parentConstraint(self.components['Right Foot'].hookPoint[0], self.components['Right Leg'].hookRoot[-1], mo = True)

    def getControls(self):
        pass