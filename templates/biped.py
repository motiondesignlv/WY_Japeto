'''
This is the biped template for all the biped characters

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: Sepember 2013
'''
#import maya modules
import maya.cmds as cmds

#import package modules
import japeto.templates.rig as rig
reload(rig)

#import libs
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import joint
from japeto.libs import control
from japeto.libs import spaces
from japeto.libs import transform

#import components
from japeto.components import component
from japeto.components import limb
from japeto.components import leg
from japeto.components import arm
from japeto.components import foot
from japeto.components import chain, spine , neck
from japeto.components import finger
from japeto.components import hand
reload(component)
reload(limb)
reload(leg)
reload(arm)
reload(foot)
reload(chain)
reload(spine)
reload(neck)
reload(finger)
reload(hand)


class Biped(rig.Rig):
    def __init__(self, name):
        super(Biped, self).__init__(name)

        self.__rootJoint = '%s_root_%s_%s' % (common.CENTER,
                                              common.SKINCLUSTER,
                                              common.JOINT)

        self.__hipJoint = '%s_hip_%s_%s' % (common.CENTER,
                                            common.SKINCLUSTER,
                                            common.JOINT)

        self.__rootCtrl  = '%s_root_%s' % (common.CENTER,
                                            common.CONTROL)
        
        self.__hipCtrl  = '%s_hip_%s' % (common.CENTER,
                                            common.CONTROL)

    @property
    def rootJoint(self):
        return self.__rootJoint

    @property
    def hipJoint(self):
        return self.__hipJoint
    
    @property
    def hipCtrl(self):
        return self.__hipCtrl
    
    @property
    def rootCtrl(self):
        return self.__rootCtrl

    def initialize(self):
        '''
        This where you register you Modules and Functions to the build
        '''
        super(Biped,self).initialize() #<---calling the parent class

        #center
        self.register('Spine',
                      spine.Spine('c_spine'),
                      position = [0,15,0],
                      numJoints = 4, 
                      numControls = 2)
        
        self.register('Neck',
                      neck.Neck('c_neck'),
                      position = [0,27,0],
                      numJoints = 4, 
                      numControls = 2,
                      parent = 'c_endspine_sc_jnt')

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
        '''
        Mirror from one side to the other
        
        @todo: Fix so we don't have to call the function twice
        '''
        super(Biped, self).mirror(side)
        super(Biped, self).mirror(side)

    def preBuild(self):
        '''
        Set up the scene for the build
        '''
        super(Biped, self).preBuild()

    def build(self):
        '''
        Build code for the asset
        '''
        super(Biped,self).build()

        displayAttr = '%s.displayJnts' % self.name
        #get the control size of the spine
        spineCtrlSize = self.components['Spine'].controlScale

        #create the root joint and control
        #-----------------------------------------------
        joint.create(self.rootJoint,
            position = self.components['Spine'].position)

        cmds.parent(self.rootJoint, self.jointsGrp)

        rootCtrl=control.create(self.rootCtrl.replace('_%s'%common.CONTROL,''),
                                type = 'square',
                                parent = self._trsCtrl,
                                color = 'yellow')

        control.scaleShape(rootCtrl,scale = [spineCtrlSize + 2,
                                             spineCtrlSize + 2,
                                             spineCtrlSize + 2])

        cmds.xform(common.getParent(rootCtrl), ws = True,
                   t = self.components['Spine'].position)

        cmds.parentConstraint(rootCtrl,self.rootJoint,mo = True)

        #create the hip joint and control
        #-----------------------------------------------
        joint.create(self.hipJoint,position =self.components['Spine'].position)

        #parent the joint to 
        cmds.parent(self.hipJoint,self.jointsGrp)
        
        hipCtrl = control.create(self.hipCtrl.replace('_%s' % common.CONTROL, ''),
                               type = 'square',
                               parent = rootCtrl,
                               color = 'yellow')
        #resize control
        control.scaleShape(hipCtrl,scale = [spineCtrlSize + 1,
                                            spineCtrlSize + 1,
                                            spineCtrlSize + 1])
        
        #move the controls into position
        cmds.xform(common.getParent(hipCtrl), ws = True,
                   t = self.components['Spine'].position)
        
        #constrain the hip joint the the hip control
        cmds.parentConstraint(hipCtrl, self.hipJoint, mo = True)
        
        for jnt in [self.rootJoint, self.hipJoint]:
            cmds.setAttr('%s.overrideEnabled' % jnt, 1)
            attribute.connect(displayAttr, '%s.overrideDisplayType' % jnt)

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
        cmds.setAttr('%s.ikfk' % self.components['Left Leg'].ikfkGroup,
                     l = False)
        attribute.connect('%s.ikfk' % self.components['Left Foot'].footCtrl,
                          '%s.ikfk' % self.components['Left Leg'].ikfkGroup)
        
        #attribute.unlockAndUnhide(['t', 'r'], node)

        #connect right ikfk attributes to the leg
        cmds.setAttr('%s.ikfk' % self.components['Right Leg'].ikfkGroup, l = False)
        attribute.connect('%s.ikfk' % self.components['Right Foot'].footCtrl,
                          '%s.ikfk' % self.components['Right Leg'].ikfkGroup)

        #copy and connect attributes from foot control to the ik control
        for part in [self.components['Left Foot'], 
                     self.components['Right Foot']]:
            for attrPath in part.footRollAttrs:
                attrPathSplit = attrPath.split('.')
                node = attrPathSplit[0]
                attr = attrPathSplit[1]
                if attr == 'ikfk':
                    continue
                #end if

                if cmds.objExists(attrPath):
                    if part._getSide() == common.LEFT:
                        attribute.copy(attr, node, destination = self.components
                                       ['Left Leg'].controls['ik'][0],
                                       connect = True,reverseConnect = False)
                    elif part._getSide() == common.RIGHT:
                        attribute.copy(attr, node,destination = self.components
                                       ['Right Leg'].controls['ik'][0],
                                       connect = True,reverseConnect = False)
                    #end elif
                    footCtrlChildren = common.getChildren(part.footCtrl) or []
                    if footCtrlChildren:
                        for child in footCtrlChildren:
                            if common.isType(child, 'parentConstraint'):
                                cmds.delete(child)      
                                break     
                            #end if
                        #end loop
                    #end if            

                    attribute.hide(attrPath)
                #end if
            #end loop
        #end loop

        #setup ikfk attr on the arms
        for part in [self.components['Right Hand'],
                     self.components['Left Hand']]:
            if part._getSide() == common.LEFT:
                cmds.setAttr('%s.ikfk' % self.components['Left Arm'].ikfkGroup,
                             l = False)
                attribute.copy('ikfk', self.components['Left Arm'].ikfkGroup,
                               destination = part.handCtrl,connect = True,
                               reverseConnect = False)
            elif part._getSide() == common.RIGHT:
                cmds.setAttr('%s.ikfk'%self.components['Right Arm'].ikfkGroup,
                             l = False)
                attribute.copy('ikfk', self.components['Right Arm'].ikfkGroup,
                               destination = part.handCtrl, connect = True,
                               reverseConnect = False)
            #end elif
        #end loop


        for part in [self.components['Left Leg'], self.components['Right Leg']]:
            for shape in common.getShapes(part.controls['fk'][-1]):
                attrPath = '%s.v' % shape
                attrConnections = attribute.getConnections (attrPath,
                                                            incoming = True,
                                                            outgoing = False,
                                                            plugs = True)
                if attrConnections:
                    for attr in attrConnections:
                        cmds.disconnectAttr(attr,attrPath)
                    #end loop
                #end if
                cmds.setAttr(attrPath, 0)
            #end loop
        #end loop
        attribute.copy('ikfk', self.components['Spine'].ikFkGroup,
                               destination = rootCtrl,connect = True,
                               reverseConnect = False)
        
        '''
        Create some spaces
        @warning: this will change 
        
        @todo: need to write a module for this
        '''
        #cmds.createNode('transform', n = )
        #cmds.parentConstraint(common.getParent(self.components['Neck'].controls['ik'][-1]))

    def postBuild(self):
        super(Biped, self).postBuild()
        '''
        Clean up the rig
        
        @todo: Figure out where things will go and scaling
        '''
        for ctrl in [self.rootCtrl, self.hipCtrl]:
            attribute.lockAndHide(['v','s'], ctrl)
        
        if common.isValid('Puppet'):
            cmds.delete('Puppet')

    def connectHooks(self):
        '''
        connectHooks takes care of connecting hooks. Connects the rig together
        
        @todo: Figure out where things will go and scaling.
        @todo: Make this more procedural
        '''
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
        cmds.parentConstraint(self.components['Spine'].hookPoint[0], self.components['Neck'].hookRoot[0], mo = True)
        cmds.parentConstraint(self.components['Spine'].hookPoint[0], self.components['Neck'].hookRoot[1], mo = True)

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
        cmds.parentConstraint(self.components['Left Leg'].hookPoint[0], common.getParent(self.components['Left Foot'].footCtrl), mo = True)
        cmds.parentConstraint(self.components['Right Leg'].hookPoint[0], common.getParent(self.components['Right Foot'].footCtrl), mo = True)

        #feet to legs
        cmds.parentConstraint(self.components['Left Foot'].hookPoint[0], self.components['Left Leg'].hookRoot[-1], mo = True)
        cmds.parentConstraint(self.components['Right Foot'].hookPoint[0], self.components['Right Leg'].hookRoot[-1], mo = True)
        
    def createSpaces(self):
        spineEndIk      = self.components['Spine'].controls['ik'][-1]
        spineStartIk    = self.components['Spine'].controls['ik'][0]
        neckIk          = self.components['Neck'].controls['ik'][-1]
        leftArmIk       = self.components['Left Arm'].controls['ik'][0]
        leftArmPv       = self.components['Left Arm'].controls['ik'][1]
        leftLegPv       = self.components['Left Leg'].controls['ik'][1]
        rightArmIk      = self.components['Right Arm'].controls['ik'][0]
        rightArmPv      = self.components['Right Arm'].controls['ik'][1]
        rightLegPv      = self.components['Right Leg'].controls['ik'][1]
        
        #create space groups
        #SPINE SPACE
        #-----------------------------
        spineEndIkGrp = cmds.createNode('transform',
                                       n = self.components['Spine'].name + '_end_space_grp',
                                       parent = common.getParent(spineEndIk))
        transform.matchXform(spineEndIkGrp, spineEndIk, 'pose')
        cmds.parent(spineEndIk, spineEndIkGrp)
        spaces.create( spaceNode = spineEndIkGrp, spaceAttrNode = spineEndIk, parent=self._trsCtrl)
        spineEndIkSpace = spaces.Spaces(spineEndIkGrp)
        spineEndIkSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        spineEndIkSpace.switch(1)
        
        #HIP SPACE
        #-----------------------------
        hipGrp = cmds.createNode('transform',
                                       n = 'hip_space_grp',
                                       parent = common.getParent(self.hipCtrl))
        transform.matchXform(hipGrp, self.hipCtrl, 'pose')
        cmds.parent(self.hipCtrl, hipGrp)
        spaces.create( spaceNode = hipGrp, spaceAttrNode = self.hipCtrl, parent=self.rootJoint)
        hipSpace = spaces.Spaces(hipGrp)
        hipSpace.addSpace(self.components['Spine'].skinClusterJnts[0], name='Spine', mode='parent')
        hipSpace.switch(1)
        
        
        #NECK SPACE
        #-----------------------------
        neckIkGrp = cmds.createNode('transform',
                                       n = self.components['Neck'].name + '_space_grp',
                                       parent = common.getParent(neckIk))
        transform.matchXform(neckIkGrp, neckIk, 'pose')
        cmds.parent(neckIk, neckIkGrp)
        spaces.create( spaceNode = neckIkGrp, spaceAttrNode = neckIk, parent=self._trsCtrl)
        neckIkGrpSpace = spaces.Spaces(neckIkGrp)
        neckIkGrpSpace.addSpace(self.components['Spine'].skinClusterJnts[-1], name='Chest', mode='parent')
        neckIkGrpSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        neckIkGrpSpace.switch(1)
        
        
        
        #LEFT ARM SPACE
        #-----------------------------
        #arm ik control
        leftArmIkGrp = cmds.createNode('transform',
                                       n = leftArmIk.replace('_%s' % common.CONTROL, '_space_grp'),
                                       parent = common.getParent(leftArmIk))
        transform.matchXform(leftArmIkGrp, leftArmIk, 'pose')
        cmds.parent(leftArmIk, leftArmIkGrp)
        spaces.create( spaceNode = leftArmIkGrp, spaceAttrNode = leftArmIk, parent=self._trsCtrl)
        leftArmIkSpace = spaces.Spaces(leftArmIkGrp)
        leftArmIkSpace.addSpace(self.components['Spine'].skinClusterJnts[-1], name='Chest', mode='parent')
        leftArmIkSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        
        #arm pv control
        leftArmPvGrp = cmds.createNode('transform',
                                       n = leftArmPv.replace('_%s' % common.CONTROL, '_space_grp'),
                                       parent = common.getParent(leftArmPv))
        transform.matchXform(leftArmPvGrp, leftArmPv, 'pose')
        cmds.parent(leftArmPv, leftArmPvGrp)
        spaces.create( spaceNode = leftArmPvGrp, spaceAttrNode = leftArmPv, parent=self._trsCtrl)
        leftArmPvSpace = spaces.Spaces(leftArmPvGrp)
        leftArmPvSpace.addSpace(self.components['Spine'].skinClusterJnts[-1], name='Chest', mode='parent')
        leftArmPvSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        
        #LEFT LEG SPACE
        #-----------------------------
        #leg pv control
        leftLegPvGrp = cmds.createNode('transform',
                                       n = leftLegPv.replace('_%s' % common.CONTROL, '_space_grp'),
                                       parent = common.getParent(leftLegPv))
        transform.matchXform(leftLegPvGrp, leftLegPv, 'pose')
        cmds.parent(leftLegPv, leftLegPvGrp)
        spaces.create( spaceNode = leftLegPvGrp, spaceAttrNode = leftLegPv, parent=self._trsCtrl)
        leftLegPvSpace = spaces.Spaces(leftLegPvGrp)
        leftLegPvSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        #leftLegPvSpace.addSpace(self.components['Left Foot'].controls['ik'][0], name='Ankle', mode='parent')
        
        #RIGHT ARM SPACE
        #-----------------------------
        rightArmIkGrp = cmds.createNode('transform',
                                       n = rightArmIk.replace('_%s' % common.CONTROL, '_space_grp'),
                                       parent = common.getParent(rightArmIk))
        transform.matchXform(rightArmIkGrp, rightArmIk, 'pose')
        cmds.parent(rightArmIk, rightArmIkGrp)
        spaces.create( spaceNode = rightArmIkGrp, spaceAttrNode = rightArmIk, parent=self._trsCtrl)
        rightArmIkSpace = spaces.Spaces(rightArmIkGrp)
        rightArmIkSpace.addSpace(self.components['Spine'].skinClusterJnts[-1], name='Chest', mode='parent')
        rightArmIkSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        
        #arm pv control
        rightArmPvGrp = cmds.createNode('transform',
                                       n = rightArmPv.replace('_%s' % common.CONTROL, '_space_grp'),
                                       parent = common.getParent(rightArmPv))
        transform.matchXform(rightArmPvGrp, rightArmPv, 'pose')
        cmds.parent(rightArmPv, rightArmPvGrp)
        spaces.create( spaceNode = rightArmPvGrp, spaceAttrNode = rightArmPv, parent=self._trsCtrl)
        rightArmPvSpace = spaces.Spaces(rightArmPvGrp)
        rightArmPvSpace.addSpace(self.components['Spine'].skinClusterJnts[-1], name='Chest', mode='parent')
        rightArmPvSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        
        #RIGHT LEG SPACE
        #-----------------------------
        #leg pv control
        rightLegPvGrp = cmds.createNode('transform',
                                       n = rightLegPv.replace('_%s' % common.CONTROL, '_space_grp'),
                                       parent = common.getParent(rightLegPv))
        transform.matchXform(rightLegPvGrp, rightLegPv, 'pose')
        cmds.parent(rightLegPv, rightLegPvGrp)
        spaces.create( spaceNode = rightLegPvGrp, spaceAttrNode = rightLegPv, parent=self._trsCtrl)
        rightLegPvSpace = spaces.Spaces(rightLegPvGrp)
        rightLegPvSpace.addSpace(self.rootJoint, name='Root', mode='parent')
        #rightLegPvSpace.addSpace(self.components['Right Foot'].controls['ik'][0], name='Ankle', mode='parent')

