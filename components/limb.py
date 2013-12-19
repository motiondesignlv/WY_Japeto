'''
This is the limb component 

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    October 2012
'''
import maya.cmds as cmds

#import package modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import ikfk
from japeto.libs import control
from japeto.libs import transform
from japeto.libs import joint

import japeto.components.component as component

class Limb(component.Component):
    def __init__(self, name):
        super(Limb, self).__init__(name)

        self.__upVector = list()
        self.__aimVector = list()


    #getters
    def __fkOrient(self):
        return cmds.getAttr('%s.fk_orient' % self.masterGuide, asString = True)

    def __ikOrient(self):
        return cmds.getAttr('%s.ik_orient' % self.masterGuide, asString = True)

    @property
    def upVector(self):
        choice = cmds.listConnections('%s.upVector' % self.masterGuide)[0]
        self.__upVector = cmds.getAttr('%s.output' % choice)[0]
        return self.__upVector

    @property
    def upVectorStr(self):
        return cmds.getAttr('%s.upVector' % self.masterGuide, asString = True)

    @property
    def aimVector(self):
        choice = cmds.listConnections('%s.aimVector' % self.masterGuide)[0]
        self.__aimVector = cmds.getAttr('%s.output' % choice)[0]
        return self.__aimVector

    @property
    def aimVectorStr(self):
        return cmds.getAttr('%s.aimVector' % self.masterGuide, asString = True)

    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Limb,self).initialize(**kwargs)

        self.addArgument('startJoint',
                '%s_upLimb_%s_%s' % (self._getPrefix(),common. SKINCLUSTER, common.JOINT))

        self.addArgument('midJoint',
                '%s_loLimb_%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT))

        self.addArgument('tipJoint',
                '%s_tipLimb_%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT))

        self.addArgument('endJoint',
                '%s_endLimb_%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT))

        self.addArgument('numSegments', 1)
        self.addArgument('stretch', True)


    def setupRig(self):
        if super(Limb,self).setupRig():
            return True

        self.skinClusterJnts.extend([self.startJoint,
                self.midJoint,
                self.tipJoint,
                self.endJoint])

        if self._getSide() == common.LEFT:
            positions = (
            [self.position[0] + 2, self.position[1], self.position[2]],
            [self.position[0] + 5, self.position[1], self.position[2] - 1],
            [self.position[0] + 8, self.position[1], self.position[2]],
                [self.position[0] + 9, self.position[1], self.position[2]]
            )
        elif self._getSide() == common.RIGHT:
            positions = (
            [self.position[0] - 2, self.position[1], self.position[2]],
            [self.position[0] - 5, self.position[1], self.position[2] - 1],
            [self.position[0] - 8, self.position[1], self.position[2]],
            [self.position[0] - 9, self.position[1], self.position[2]]
            )
        else:
            positions = (
            [self.position[0] - 2, self.position[1], self.position[2]],
            [self.position[0] - 5, self.position[1], self.position[2] - 1],
            [self.position[0] - 8, self.position[1], self.position[2]],
            [self.position[0] - 9, self.position[1], self.position[2]]
            )

        for i,jnt in enumerate(self.skinClusterJnts):
            cmds.joint(n = jnt,position = positions[i])

            if i == 0:
                cmds.parent(jnt, self.skeletonGrp)
                #place Master Guide control in the same position as the first joint
                transform.matchXform(jnt, common.getParent(self.masterGuide), type = 'position')
            else:
                cmds.parent(jnt, self.skinClusterJnts[i - 1])

            ctrl = self.setupCtrl(jnt.replace('_%s' % common.JOINT, ''),jnt)
            #create template control
            #control.createTemplate(ctrl)
            cmds.select(cl = True)


        # ----------------------------------------------------------------------
        # CREATE GUIDES
        startJointGuide = self.startJoint.replace(common.JOINT, common.GUIDES)
        midJointGuide   = self.midJoint.replace(common.JOINT, common.GUIDES)
        tipJointGuide   = self.tipJoint.replace(common.JOINT, common.GUIDES)
        endJointGuide   = self.endJoint.replace(common.JOINT, common.GUIDES)

        #templateNullGroup = cmds.createNode('transform', n = endJointGuide.replace(common.GUIDES, common.GROUP))
        #transform.matchXform(locator, endJointGuide, type = 'position')
        #cmds.pointConstraint(tipJointGuide, templateNullGroup)
        #cmds.parent(templateNullGroup, self.guidesGrp)
        #control.createTemplate(templateNullGroup, defaultType = 'implicitSphere')


        # ----------------------------------------------------------------------
        # ORIENTATION 
        #
        if self._getSide() == common.RIGHT:
            aimVectorAttr = \
                attribute.switch ('aimVector',
                    node= self.masterGuide,
                    value=4,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])

            upVectorAttr  = \
                attribute.switch ('upVector',
                    node=self.masterGuide,
                    value=3,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])
        else:
            aimVectorAttr = \
                attribute.switch ('aimVector',
                    node=self.masterGuide,
                    value=1,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])

            upVectorAttr  = \
                attribute.switch ('upVector',
                    node=self.masterGuide,
                    value=3,
                    choices=['x','y','z','-x','-y','-z'],
                    outputs=[(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)])

        #Get Vectors for the cross product
        #Decompose matrix nodes 
        startJointDcm = \
            cmds.createNode('decomposeMatrix',
                name = self.startJoint.replace('%s_%s' % (common.SKINCLUSTER, common.JOINT), common.DECOMPOSEMATRIX ))

        attribute.connect('%s.worldMatrix' % startJointGuide,'%s.inputMatrix' % startJointDcm)

        midJointDcm = \
            cmds.createNode('decomposeMatrix', name = self.midJoint.replace('%s_%s' % (common.SKINCLUSTER, common.JOINT), common.DECOMPOSEMATRIX ))

        attribute.connect('%s.worldMatrix' % midJointGuide, '%s.inputMatrix' % midJointDcm)

        tipJointDcm = \
            cmds.createNode('decomposeMatrix', name = self.tipJoint.replace('%s_%s' % (common.SKINCLUSTER, common.JOINT), common.DECOMPOSEMATRIX ))
        attribute.connect('%s.worldMatrix' % tipJointGuide, '%s.inputMatrix' % tipJointDcm)

        #plus minus average nodes
        v1Node = cmds.createNode('plusMinusAverage')
        v2Node = cmds.createNode('plusMinusAverage')
        cmds.setAttr('%s.operation' % v1Node, 2)
        cmds.setAttr('%s.operation' % v2Node, 2)

        #connect Decompose Matrix and Plus Minus Average nodes
        attribute.connect('%s.outputTranslate' % tipJointDcm, '%s.input3D[0]' % v1Node)
        attribute.connect('%s.outputTranslate' % startJointDcm, '%s.input3D[1]' % v1Node)
        attribute.connect('%s.outputTranslate' % midJointDcm, '%s.input3D[0]' % v2Node)
        attribute.connect('%s.outputTranslate' % startJointDcm, '%s.input3D[1]' % v2Node)

        #Get the cross product
        crossNode = cmds.createNode('vectorProduct')
        cmds.setAttr( '%s.%s' % (crossNode,'operation') , 2 )
        attribute.connect( '%s.%s' % (v1Node,'output3D'), '%s.%s' % (crossNode,'input1') )
        attribute.connect( '%s.%s' % (v2Node,'output3D'), '%s.%s' % (crossNode,'input2') )
        crossVectorAttr = '%s.%s' % (crossNode,'output')

        #Aim start joint to the middle joint
        constraint = \
            cmds.aimConstraint(midJointGuide,
                    self.startJoint,
                    aimVector = (1,0,0),
                    upVector = (0,1,0),
                    worldUpType = 'vector',
                    worldUpVector = (0,1,0))[0]

        attribute.connect(aimVectorAttr, '%s.aimVector' % constraint)
        attribute.connect(upVectorAttr, '%s.upVector' % constraint)
        attribute.connect(crossVectorAttr, '%s.worldUpVector' % constraint)
        self.setupConstraints.append(constraint)

        #Aim middle joint to the tip joint
        constraint = \
            cmds.aimConstraint(tipJointGuide,
                    self.midJoint,
                    aimVector = (1,0,0),
                    upVector = (0,1,0),
                    worldUpType = 'vector',
                    worldUpVector = (0,1,0))[0]

        attribute.connect(aimVectorAttr, '%s.aimVector' % constraint)
        attribute.connect(upVectorAttr, '%s.upVector' % constraint)
        attribute.connect(crossVectorAttr, '%s.worldUpVector' % constraint)
        self.setupConstraints.append(constraint)

        constraint = cmds.orientConstraint(self.midJoint, self.tipJoint)[0]
        self.setupConstraints.append(constraint)

        cmds.setAttr('%s.normalizeOutput' % crossNode, True)

        self.upTwistJnts = list()
        step   = 1.0 / (self.numSegments + 1)
        parent = self.startJoint
        for i in range( 1, self.numSegments + 1 ):
            j = joint.create( name='%s' % (self.startJoint.replace('_%s' % common.SKINCLUSTER, 'Twist_%s_%s' % (common.padNumber(i,3), common.SKINCLUSTER))), parent=parent )
            transform.matchXform( self.startJoint,j, type='rotate' )
            constraint = cmds.pointConstraint( self.startJoint, self.midJoint, j )[0]
            weightAliasList = cmds.pointConstraint( constraint, q=True, weightAliasList=True )
            cmds.setAttr( '%s.%s' % (constraint, weightAliasList[0]), 1-(step*i) )
            cmds.setAttr( '%s.%s' % (constraint, weightAliasList[1]),  step*i )
            self.upTwistJnts.append(j)
            self.skinClusterJnts.append(j) #adding the joint to skincluster joints list

        # Create MiddleJoint Segments
        self.loTwistJnts = list()
        parent = self.midJoint
        for i in range( 1, self.numSegments + 1):
            j = joint.create( name='%s' % (self.midJoint.replace('_%s' % common.SKINCLUSTER, 'Twist_%s_%s' % (common.padNumber(i,3), common.SKINCLUSTER))), parent=parent )
            transform.matchXform( self.midJoint,j, type='rotate' )
            constraint = cmds.pointConstraint( self.midJoint, self.tipJoint, j )[0]
            weightAliasList = cmds.pointConstraint( constraint, q=True, weightAliasList=True )
            cmds.setAttr( '%s.%s' % (constraint, weightAliasList[0]), 1-(step*i) )
            cmds.setAttr( '%s.%s' % (constraint, weightAliasList[1]),  step*i )
            self.loTwistJnts.append(j)
            self.skinClusterJnts.append(j) #adding the joint to skincluster joints list

    def postSetupRig(self):
        if super(Limb, self).postSetupRig():
            return True

        #Add attributes to the master guide to control the orientation of the ik and fk controls
        attribute.addAttr(self.masterGuide, 'fk_orient', attrType = 'enum', defValue = 'World:Local', value = 1)
        attribute.addAttr(self.masterGuide, 'ik_orient', attrType = 'enum', defValue = 'World:Local', value = 0)


    def rig(self):
        if cmds.objExists('%s.master_guide' % self.setupRigGrp):
            self.masterGuide = attribute.getConnections('master_guide', self.setupRigGrp)[0].split('.')[0]

        #get orientations for controls
        fkOrient = self.__fkOrient()
        ikOrient = self.__ikOrient()
        upVector = self.upVector
        aimVector = self.aimVector

        #call parent class rig function
        super(Limb, self).rig()

        #create ik fk switch
        ikfkDict = ikfk.create(jointChain = [self.startJoint, self.midJoint, self.tipJoint], stretch = self.stretch)
        ikfkDict['group'] = cmds.rename(ikfkDict['group'], '%s_%s' % (self.name(),ikfkDict['group']))

        #set the visibility on the ik/fk/blend joints to off
        cmds.setAttr('%s.v' % ikfkDict['fkJoints'][0], 0)
        cmds.setAttr('%s.v' % ikfkDict['ikJoints'][0], 0)
        cmds.setAttr('%s.v' % ikfkDict['blendJoints'][0], 0)

        ikfkAttr = attribute.addAttr(self.rigGrp, attr = 'ikfk', attrType = 'enum', defValue = ['off','on'],value = 0)

        cmds.connectAttr(ikfkAttr, '%s.ikfk' % ikfkDict['group'], l = True, f = True)

        #parent ikfk group under joints group
        cmds.parent(ikfkDict['group'], self.jointsGrp)

        #rename all ik and blend joints
        for i,jnt in enumerate(ikfkDict['ikJoints']):
            jnt = cmds.rename(jnt, jnt.replace('%s_%s_%s' % (common.SKINCLUSTER,common.JOINT, common.IK), '%s_%s' % (common.IK, common.JOINT)))
            ikfkDict['ikJoints'][i] = jnt

        for i,jnt in enumerate(ikfkDict['blendJoints']):
            jnt = cmds.rename(jnt, jnt.replace('%s_%s_%s' % (common.SKINCLUSTER,common.JOINT, common.BLEND), '%s_%s' % (common.BLEND, common.JOINT)))
            ikfkDict['blendJoints'][i] = jnt

        #create ik setup
        ikCtrl = control.create(name = ikfkDict['ikJoints'][2].replace('_%s' % common.JOINT, ''),type = 'cube', parent = self.controlsGrp, color = common.SIDE_COLOR[self._getSide()])
        ikCtrlZero = common.getParent(ikCtrl)
        attribute.copy('stretch', ikfkDict['group'], destination = ikCtrl, connect = True,reverseConnect = False)
        attribute.copy('stretchTop', ikfkDict['group'], destination = ikCtrl, connect = True,reverseConnect = False)
        attribute.copy('stretchBottom', ikfkDict['group'], destination = ikCtrl, connect = True,reverseConnect = False)

        if ikOrient == 'Local':
            transform.matchXform(ikfkDict['ikJoints'][2], ikCtrlZero, type = 'pose')
        else:
            transform.matchXform(ikfkDict['ikJoints'][2], ikCtrlZero, type = 'position')
            cmds.orientConstraint(ikCtrl, ikfkDict['ikJoints'][2], mo = True)
            common.setColor(ikCtrl, common.SIDE_COLOR[self._getSide()])

            #setup poleVector
            pvCtrl = control.create(name = ikfkDict['ikJoints'][2].replace('_%s' % common.JOINT, '_%s' % common.POLEVECTOR),type = 'cube', parent = self.controlsGrp, color = common.SIDE_COLOR[self._getSide()])
            #size polevector control

        for i in range(len(common.getShapes(pvCtrl))):
            control.scaleShape(pvCtrl, scale = [self.controlScale * .5, self.controlScale * .5, self.controlScale * .5], index = i)

        pvCtrlZero = common.getParent(pvCtrl)
        pvDisplayLineAttr = attribute.addAttr(pvCtrl, attr = 'pvLine', attrType = 'enum', defValue = 'off:on', value = 1)
        transform.matchXform(ikfkDict['ikJoints'][1], pvCtrlZero, type = 'position')
        #cmds.parent(ikfkDict['ikHandle'], w = True)
        pvPos = ikfk.getPoleVectorPosition(ikfkDict['ikJoints'][1], ikfkDict['ikHandle'])
        cmds.xform(pvCtrlZero, ws = True, t = pvPos)
        common.setColor(pvCtrlZero, common.SIDE_COLOR[self._getSide()])

        #create polevector constraint and parent under control
        cmds.poleVectorConstraint(pvCtrl, ikfkDict['ikHandle'])
        targetConstraint = cmds.pointConstraint(ikCtrl, ikfkDict['targetJnts'][1], mo = True) #ikhandle is under target joint
        pvDisplayLine = control.displayLine(ikfkDict['ikJoints'][0], pvCtrl, name = pvCtrl.replace(common.CONTROL, common.DISPLAYLINE), parent = self.controlsGrp)


        cmds.orientConstraint(ikCtrl,ikfkDict['ikJoints'][0], mo = True)

        #adding attribute to ik ctrl
        ikTwistAttr = attribute.addAttr(ikCtrl, attr = 'twist')
        cmds.connectAttr(ikTwistAttr, '%s.twist' % ikfkDict['ikHandle'], f = True)

        #connecting to shapes
        ikfkReverse = cmds.createNode('reverse', n = ikCtrl.replace('%s_%s' % (common.IK, common.CONTROL), '%s_%s' % (common.REVERSE, common.UTILITY)))
        attribute.connect('%s.ikfk' % ikfkDict['group'], '%s.inputX' % ikfkReverse)
        for shape in common.getShapes(ikCtrl):
            attribute.connect('%s.outputX' % ikfkReverse,'%s.v' % shape)

        for shape in common.getShapes(pvCtrl):
            attribute.connect('%s.outputX' % ikfkReverse,'%s.v' % shape)

        #connect pvDisplayLineAttr in pvDisplayLine visibility
        displayLineMultiply = cmds.createNode('multiplyDivide', n = pvDisplayLine.replace(common.DISPLAYLINE, common.MULTIPLYDIVIDE))
        attribute.connect(pvDisplayLineAttr, '%s.input1X' % displayLineMultiply)
        attribute.connect('%s.outputX' % ikfkReverse, '%s.input2X' % displayLineMultiply)
        attribute.connect('%s.outputX' % displayLineMultiply, '%s.v' % common.getChildren(pvDisplayLine)[0])

        #create fk setup
        fkCtrls = list()
        parent = self.controlsGrp
        for i,jnt in enumerate(ikfkDict['fkJoints']):
            cmds.select(cl = True)
            #rename fk joint
            jnt = cmds.rename(jnt,jnt.replace('%s_%s_%s' % (common.SKINCLUSTER,common.JOINT,common.FK), '%s_%s' % (common.FK,common.JOINT)))
            ikfkDict['fkJoints'][i] = jnt #re-assign fk joint intop ikfkDict
            #create controls, set color, and make connections
            fkCtrl = control.create(name = jnt.replace('_%s' % common.JOINT, ''),type = 'circle', parent = parent, color = common.SIDE_COLOR[self._getSide()])
            fkCtrlZero = common.getParent(fkCtrl)
            
            if fkOrient == 'Local':
                transform.matchXform(jnt, fkCtrlZero, type = 'pose')
            #end if
            else:
                transform.matchXform(jnt, fkCtrlZero, type = 'position')
            #end else
            
            cmds.connectAttr('%s.ikfk' % ikfkDict['group'], '%s.v' % common.getShapes(fkCtrl)[0], f = True)
            cmds.parentConstraint(fkCtrl, jnt, mo = True)
            attribute.lockAndHide('t', fkCtrl)
            attribute.lockAndHide('s', fkCtrl)
            attribute.lockAndHide('v', fkCtrl)
            #get joint rotate order and apply to control and parent group
            rotateOrder = attribute.getValue('rotateOrder', jnt)
            for node in [fkCtrl, fkCtrlZero]:
                cmds.setAttr('%s.rotateOrder' % node, rotateOrder)
    
                fkCtrls.append(fkCtrl)
                parent = fkCtrl
            #end loop
        #end loop

        aimAxis = transform.getAimAxis(ikfkDict['blendJoints'][0], allowNegative = False)    
        #Up Twist Joint Setup
        if self.upTwistJnts:
            noTwistJnt = common.duplicate(self.startJoint, name = self.startJoint.replace('%s' % common.SKINCLUSTER, 'NoTwist_%s' % common.SKINCLUSTER), parent = self.startJoint)

            inverseMultNode = cmds.createNode('multiplyDivide', n = noTwistJnt.replace('%s_%s' % (common.SKINCLUSTER,common.JOINT), '%s_%s' % (common.UTILITY, common.MULTIPLYDIVIDE)))
            cmds.connectAttr('%s.r%s' % (ikfkDict['blendJoints'][0], aimAxis), '%s.input1X' % inverseMultNode, f = True)
            cmds.setAttr('%s.input2X' % inverseMultNode, -1)
            cmds.connectAttr('%s.outputX' % inverseMultNode, '%s.r%s' % (noTwistJnt, aimAxis), f = True)


            step   = 1.0 / (len(self.upTwistJnts) +1)
            for i in range( 1, (len(self.upTwistJnts)+1) ):
                twsitMultNode = cmds.createNode('multiplyDivide', n = self.upTwistJnts[i - 1].replace('%s_%s' % (common.SKINCLUSTER,common.JOINT), '%s_%s' % (common.UTILITY, common.MULTIPLYDIVIDE)))
                cmds.connectAttr('%s.r%s' % (ikfkDict['blendJoints'][0], aimAxis), '%s.input1X' % twsitMultNode, f = True)
                cmds.setAttr('%s.input2X' % twsitMultNode, -(1-(step*i))  )
                cmds.connectAttr('%s.outputX' % twsitMultNode, '%s.r%s' % (self.upTwistJnts[i -1], aimAxis),f = True)
            #end loop

            self.upTwistJnts.insert(0, noTwistJnt)
        #end if

        if self.loTwistJnts:
            twistJnt = common.duplicate(self.midJoint, name = self.midJoint.replace('%s' % common.SKINCLUSTER, 'loTwist_%s' % common.SKINCLUSTER), parent = self.midJoint)
            constraint = cmds.aimConstraint(ikfkDict['blendJoints'][2],twistJnt,aimVector =  aimVector, upVector  = upVector,  worldUpType ="objectrotation", worldUpVector = upVector, worldUpObject = self.tipJoint)
            cmds.setAttr('%s.v' % twistJnt, 0)
        #end if

        step   = 1.0 / (len(self.loTwistJnts) +1)
        for i in range( 1, (len(self.loTwistJnts)+1) ):
            twsitMultNode = cmds.createNode('multiplyDivide', n = self.loTwistJnts[i - 1].replace('%s_%s' % (common.SKINCLUSTER,common.JOINT), '%s_%s' % (common.UTILITY, common.MULTIPLYDIVIDE)))
            cmds.connectAttr('%s.r%s' % (ikfkDict['blendJoints'][2], aimAxis), '%s.input1X' % twsitMultNode, f = True)
            cmds.setAttr('%s.input2X' % twsitMultNode, 1-(step*i) )
            cmds.connectAttr('%s.outputX' % twsitMultNode, '%s.r%s' % (self.loTwistJnts[i -1], aimAxis),f = True)
        #end loop

        #------------------------
        #Add to class variables
        #------------------------
        #assign joints to the joints list
        self.joints.update({'ik' : ikfkDict['ikJoints'], 'fk' : ikfkDict['fkJoints'], 'blend' : ikfkDict['blendJoints'], 'target' : ikfkDict['targetJnts']})
        #assign controls to the controls list
        #assign fkCtrls into the controls dictionary 
        self.controls.update({'ik' : [ikCtrl, pvCtrl],'fk' : fkCtrls })
        self.ikfkGroup = ikfkDict['group']
        #assign hooks
        self.hookRoot.extend([ikfkDict['ikJoints'][0], common.getParent(fkCtrls[0]), ikCtrl, ikfkDict['targetJnts'][-1]])
        self.hookPoint.extend([ikfkDict['blendJoints'][-1]])
        #add no twist joint to the skincluster list
        self.skinClusterJnts.append(noTwistJnt)


    def postRig(self):
        super(Limb, self).postRig()
        attribute.lockAndHide(['s', 'v'],self.controls['ik'][0])
        attribute.lockAndHide(['r','s', 'v'],self.controls['ik'][1])