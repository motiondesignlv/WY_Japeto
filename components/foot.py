'''
This is the foot component 

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    July 2013
'''
#import maya modules------
import maya.cmds as cmds

#import package modules------
#import libs
import japeto.libs.common as common
import japeto.libs.attribute as attribute
import japeto.libs.ikfk as ikfk
import japeto.libs.control as control
import japeto.libs.transform as transform

#import components
import japeto.components.component as component


class Foot(component.Component):
    def __init__(self, name):
        super(Foot, self).__init__(name)

        #create controls
        self.__footCtrl = str()
        self.__bankInCtrl = str()
        self.__bankOutCtrl = str()

        #foot roll groups
        self.__bankIn        = 'bankIn'
        self.__bankInZero    = 'bankInZero'
        self.__bankOut       = 'bankOut'
        self.__bankOutZero   = 'bankOutZero'
        self.__heelPivotName = 'heelPivot'
        self.__heelRoll      = 'heelRoll'
        self.__heelRollZero  = 'heelRollZero'
        self.__toePivot      = 'toePivot'
        self.__toeRoll       = 'toeRoll'
        self.__toeBend       = 'toeBend'
        self.__ballRoll      = 'ballRoll'

        #foot roll groups that will get passed into the IkFkFoot class
        self.__footRollGroups = [self.__bankIn,
                 self.__bankInZero,
                 self.__bankOut,
                 self.__bankOutZero,
                 self.__heelPivotName,
                 self.__heelRoll,
                 self.__heelRollZero,
                 self.__toePivot,
                 self.__toeRoll,
                 self.__ballRoll,
                 self.__toeBend]

        self.__footRollAttrs = list()

    @property
    def footCtrl(self):
        return self.__footCtrl

    @property
    def footRollGroups(self):
        return self.__footRollGroups

    @property
    def footRollAttrs(self):
        return self.__footRollAttrs

    @component.overloadArguments
    def initialize(self, **kwargs):
        super(Foot,self).initialize(**kwargs)

        self.addArgument('ankleJoint',
                '%s_ankle_%s_%s' % (self._getPrefix(),
                common.SKINCLUSTER,
                common.JOINT), 5)

        self.addArgument('ballJoint',
                '%s_ball_%s_%s' % (self._getPrefix(),
                common.SKINCLUSTER,
                common.JOINT), 6)

        self.addArgument('toeJoint',
                '%s_toe_%s_%s' % (self._getPrefix(),
                common. SKINCLUSTER,
                common.JOINT), 7)

    def setupRig(self):
        super(Foot, self).setupRig()

        self.skinClusterJnts = [ self.ankleJoint,
                                 self.ballJoint,
                                 self.toeJoint ]

        if self._getSide() == common.LEFT:
            positions = (
            [self.position[0] + 2, self.position[1] + 2, self.position[2]],
            [self.position[0] + 2, self.position[1], self.position[2] + 2],
            [self.position[0] + 2, self.position[1], self.position[2] + 4]
            )

            #create offset position depending on which side it's on
            bankInOffset = -1
            bankOutOffset = 1
        elif self._getSide() == common.RIGHT:
            positions = (
            [self.position[0] - 2, self.position[1] + 2, self.position[2]],
            [self.position[0] - 2, self.position[1], self.position[2] + 2],
            [self.position[0] - 2, self.position[1], self.position[2] + 4]
            )

            #create offset position depending on which side it's on
            bankInOffset = 1
            bankOutOffset = -1
        else:
            positions = (
            [self.position[0], self.position[1] + 2, self.position[2]],
            [self.position[0], self.position[1], self.position[2] + 2],
            [self.position[0], self.position[1], self.position[2] + 4]
            )

            #create offset position depending on which side it's on
            bankInOffset = -1
            bankOutOffset = 1
        #end elif

        for i,jnt in enumerate(self.skinClusterJnts):
            cmds.joint(n = jnt,position = positions[i])

            if i == 0:
                cmds.parent(jnt, self.skeletonGrp)
                #place Master Guide control in the same position as the first joint
                transform.matchXform(jnt,
                    common.getParent(self.masterGuide),
                    type = 'position')
            else:
                cmds.parent(jnt, self.skinClusterJnts[i - 1])
            #end else

            ctrl = self.setupCtrl(jnt.replace('_%s' % common.JOINT, ''),jnt)
            #create template control
            #control.createTemplate(ctrl)
            cmds.select(cl = True)
        #end loop

        #create pivots for setup
        self.__bankInPivot = cmds.createNode('joint',
                n = '%s_bankIn_%s' % (self._getPrefix(),
                common.PIVOT))

        self.__bankOutPivot = cmds.createNode('joint',
                n = '%s_bankOut_%s' % (self._getPrefix(),
                common.PIVOT))

        self.__heelPivot = cmds.createNode('joint',
                n = '%s_heel_%s' % (self._getPrefix(),
                common.PIVOT))

        #move pivots into position
        x,y,z = positions[1]
        cmds.xform(self.__bankInPivot, ws = True, t = [x + bankInOffset, y, z])
        cmds.xform(self.__bankOutPivot, ws = True, t = [x + bankOutOffset, y, z])
        cmds.xform(self.__heelPivot, ws = True, t = [x, y, z  - 4])

        #parent pivots
        for pivot in [self.__bankInPivot, self.__bankOutPivot, self.__heelPivot]:
            cmds.parent(pivot, self.skeletonGrp)
        #end loop


        # ----------------------------------------------------------------------
        # CREATE GUIDES
        ankleJointGuide = self.ankleJoint.replace(common.JOINT, common.GUIDES)
        ballointGuide   = self.ballJoint.replace(common.JOINT, common.GUIDES)
        toeJointGuide   = self.toeJoint.replace(common.JOINT, common.GUIDES)
        bankInPivotGuide   = \
                self.setupCtrl(self.__bankInPivot.replace('_%s' % common.JOINT, ''),
                self.__bankInPivot,
                color = common.SIDE_COLOR_SECONDARY[self._getSide()])

        bankOutPivotGuide   = \
                self.setupCtrl(self.__bankOutPivot.replace('_%s' % common.JOINT,''),
                self.__bankOutPivot,
                color = common.SIDE_COLOR_SECONDARY[self._getSide()])

        heelPivotGuide   = \
                self.setupCtrl(self.__heelPivot.replace('_%s' % common.JOINT, ''),
                self.__heelPivot,
                color = common.SIDE_COLOR_SECONDARY[self._getSide()])


        cmds.pointConstraint(self.ballJoint,
                common.getParent(bankOutPivotGuide), mo = True)

        cmds.pointConstraint(self.ballJoint,
                common.getParent(bankInPivotGuide), mo = True)

        #resize pivot controls
        for ctrl in [heelPivotGuide, bankOutPivotGuide, bankInPivotGuide]:
            cmds.setAttr('%s.radius' % common.getShapes(ctrl)[0],
                    self.controlScale * .5)

    def postSetupRig(self):
        super(Foot, self).postSetupRig()

    def rig(self):
        if not self._puppetNode:
            self.runSetupRig()
        cmds.parent([self.__bankInPivot,
                self.__bankOutPivot,
                self.__heelPivot],
                w = True)

        super(Foot,self).rig()

        #create foot ik/fk chain and parent group to joints group
        self.__footIkFk = \
                ikfk.IkFkFoot(self.ankleJoint,
                        self.toeJoint,
                        name = self.name())

        #list the groups for the foot ik setup
        self.__footRollGroups.insert(0, 'anklePivot')
        footRollGrpList = self.__footRollGroups

        #create foot setup
        self.__footIkFk.create(searchReplace = '%s' % common.SKINCLUSTER,
                footRollGrpList = footRollGrpList)

        #parent to joints group
        cmds.parent(self.__footIkFk.group, self.jointsGrp)

        #get position of joints
        anklePosition    = \
            cmds.xform(self.ankleJoint, q = True, ws = True, rp = True)

        ballPosition     = \
            cmds.xform(self.ballJoint, q = True, ws = True, rp = True)

        toePosition      = \
            cmds.xform(self.toeJoint, q = True, ws = True, rp = True)

        bankInPosition   = \
            cmds.xform(self.__bankInPivot, q = True, ws = True, rp = True)

        bankOutPosition  = \
            cmds.xform(self.__bankOutPivot, q = True, ws = True, rp = True)

        heelPosition     = \
            cmds.xform(self.__heelPivot, q = True, ws = True, rp = True)

        #delete pivot joints
        for jnt in (self.__heelPivot,self.__bankOutPivot, self.__bankInPivot):
            cmds.delete(jnt)
        #end loop

        #get foot roll groups
        footRollGroups = self.__footIkFk.getFootRolls()
        handles = self.__footIkFk.getIkHandles()

        #position foot roll groups
        for grp in footRollGroups:
            if grp in ['ballRoll', 'toeBend']:
                cmds.xform(footRollGroups[grp], ws = True, rp = ballPosition)
            elif grp in ['heelRoll', 'heelPivot']:
                if grp == self.__heelPivotName:
                    cmds.setAttr('%s.rotateOrder' % footRollGroups[grp], 2)
                cmds.xform(footRollGroups[grp], ws = True, rp = heelPosition)
            elif grp in ['toeRoll', 'toePivot']: 
                cmds.xform(footRollGroups[grp], ws = True, rp = toePosition)
            elif grp in ['bankIn', self.__bankInZero]: 
                cmds.xform(footRollGroups[grp], ws = True, rp = bankInPosition)
            elif grp in ['bankOut', self.__bankOutZero]: 
                cmds.xform(footRollGroups[grp], ws = True, rp = bankOutPosition)
                cmds.setAttr('%s.rotateOrder' % footRollGroups[grp], 2)
            elif grp in ['anklePivot']: 
                cmds.xform(footRollGroups[grp], ws = True, rp = anklePosition)
        #end loop


        #create controls
        self.__footCtrl      = \
            control.create(name= self.name(),
                    type = 'implicitSphere',
                    parent = self.controlsGrp,
                    color = common.SIDE_COLOR[self._getSide()])

        self.__bankInCtrl    = \
            control.create(name= footRollGroups[self.__bankIn] ,
                    type = 'implicitSphere',
                    parent = self.controlsGrp,
                    color = common.SIDE_COLOR_SECONDARY[self._getSide()])

        self.__bankOutCtrl   = \
            control.create(name= footRollGroups[self.__bankOut] ,
                    type = 'implicitSphere',
                    parent = self.controlsGrp,
                    color = common.SIDE_COLOR_SECONDARY[self._getSide()])

        self.__heelPivotCtrl = \
            control.create(name= footRollGroups[self.__heelPivotName] ,
                    type = 'implicitSphere',
                    parent = self.controlsGrp,
                    color = common.SIDE_COLOR_SECONDARY[self._getSide()])

        #parent of controls
        parentBankOutCtrl   = common.getParent(self.__bankOutCtrl)
        parentBankInCtrl    = common.getParent(self.__bankInCtrl)
        parentHeelPivotCtrl = common.getParent(self.__heelPivotCtrl)

        #scale controls
        for ctrl in [self.__footCtrl,self.__bankOutCtrl, self.__bankInCtrl, self.__heelPivotCtrl]:
            for i in range(len(common.getShapes(ctrl))):
                control.scaleShape (ctrl, scale = [.3, .3, .3], index = i)


        #place controls in correct positions
        transform.matchXform(self.ankleJoint,
                common.getParent(self.__footCtrl),
                type = 'pose')

        cmds.xform(common.getParent(self.__footCtrl),
                ws = True,
                r = True,
                t = [0,0,-2])

        cmds.delete(cmds.parentConstraint(footRollGroups['bankIn'],
                parentBankInCtrl))

        cmds.delete(cmds.parentConstraint(footRollGroups['bankOut'],
                parentBankOutCtrl))

        cmds.delete(cmds.parentConstraint(footRollGroups['heelPivot'],
                parentHeelPivotCtrl))

        #Decompose matrix nodes for pivots and connect the controls to them
        for ctrl, grp in zip([self.__bankInCtrl, self.__bankOutCtrl, self.__heelPivotCtrl] , [footRollGroups['bankIn'], footRollGroups['bankOut'], footRollGroups[self.__heelRoll]]):
            grpZero = common.getChildren(grp)[0]

            dcm = cmds.createNode('decomposeMatrix',
                    n = '%s_%s' % (grp, common.DECOMPOSEMATRIX))

            mdn = cmds.createNode('multiplyDivide',
                    n = '%s_%s' % (grp, common.MULTIPLYDIVIDE))

            attribute.connect('%s.worldMatrix[0]' % ctrl, '%s.inputMatrix' % dcm)

            #connect controls to pivots
            attribute.connect('%s.outputTranslate' % dcm, '%s.rotatePivot' % grp)
            attribute.connect('%s.outputTranslate' % dcm, '%s.rotatePivot' % grpZero)
            #Change attributes on Multiply divide node and make connections
            cmds.setAttr('%s.input2Y' % mdn, -1)
            attribute.connect('%s.ry' % ctrl, '%s.input1Y' % mdn)
            attribute.connect('%s.outputY' % mdn, '%s.ry' % grpZero)
            attribute.connect('%s.ry' % ctrl, '%s.ry' % grp)


        #parent constrain the foot control to the ankle joint
        for node in [self.__footCtrl,parentBankOutCtrl,  parentBankInCtrl, parentHeelPivotCtrl]:
            cmds.parentConstraint(footRollGroups['anklePivot'], node, mo = True)


        #add attributes to the foot control and connect them to the pivots
        ikfkAttr      = \
            attribute.addAttr(self.__footCtrl,
                    'ikfk' ,
                    attrType = 'enum',
                    defValue = ['off', 'on'],
                    value = 0)

        bankAttr      = \
            attribute.addAttr(self.__footCtrl,
                    'bank' ,
                    attrType = 'double',
                    defValue = 0,
                    min = -10,
                    max = 10)

        ballRollAttr  = \
            attribute.addAttr(self.__footCtrl,
                    self.__ballRoll ,
                    attrType = 'double',
                    defValue = 0,
                    min = 0,
                    max = 10)

        toeRollAttr   = \
            attribute.addAttr(self.__footCtrl,
                    self.__toeRoll ,
                    attrType = 'double',
                    defValue = 0,
                    min = 0,
                    max = 10)

        toePivotAttr  = \
            attribute.addAttr(self.__footCtrl,
                    self.__toePivot ,
                    attrType = 'double',
                    defValue = 0,
                    min = -10,
                    max = 10)

        toeBendAttr   = \
            attribute.addAttr(self.__footCtrl,
                    self.__toeBend ,
                    attrType = 'double',
                    defValue = 0,
                    min = -10,
                    max = 10)

        heelRollAttr  = \
            attribute.addAttr(self.__footCtrl,
                    self.__heelRoll ,
                    attrType = 'double',
                    defValue = 0,
                    min = -10,
                    max = 0)

        heelPivotAttr = \
            attribute.addAttr(self.__footCtrl,
                    self.__heelPivotName ,
                    attrType = 'double',
                    defValue = 0,
                    min = -10,
                    max = 10)

        self.__footRollAttrs.extend([ikfkAttr,
                bankAttr,
                ballRollAttr,
                toeRollAttr ,
                toePivotAttr,
                toeBendAttr,
                heelRollAttr,
                heelPivotAttr])

        #create remap dictionary to place remap nodes in based on foot roll group names
        ramapNodes = dict()

        #create remap nodes and connect them to foot roll groups
        for attr in [bankAttr,toePivotAttr,toeBendAttr,heelPivotAttr]:
            node, attrName = attr.split('.')
            ramapNodes[attrName] = \
                cmds.createNode('remapValue',
                        n = '%s_%s_%s' % (node, attrName, common.REMAP))

            attribute.connect(attr, '%s.inputValue' % ramapNodes[attrName])
            cmds.setAttr('%s.outputMax' % ramapNodes[attrName], 100)
            cmds.setAttr('%s.outputMin' % ramapNodes[attrName], -100)
            cmds.setAttr('%s.inputMax' % ramapNodes[attrName], 10)
            cmds.setAttr('%s.inputMin' % ramapNodes[attrName], -10)
        #end loop

        for attr in [ballRollAttr,toeRollAttr, heelRollAttr]:
            node, attrName = attr.split('.')
            ramapNodes[attrName] = \
                cmds.createNode('remapValue',
                        n = '%s_%s_%s' % (node, attrName, common.REMAP))
            attribute.connect(attr, '%s.inputValue' % ramapNodes[attrName])
            cmds.setAttr('%s.outputMax' % ramapNodes[attrName], 100)
            cmds.setAttr('%s.outputMin' % ramapNodes[attrName], 0)
            cmds.setAttr('%s.inputMax' % ramapNodes[attrName], 10)
            cmds.setAttr('%s.inputMin' % ramapNodes[attrName], 0)

            if attr == heelRollAttr:
                cmds.setAttr('%s.outputMax' % ramapNodes[attrName], 0)
                cmds.setAttr('%s.outputMin' % ramapNodes[attrName], -100)
                cmds.setAttr('%s.inputMax' % ramapNodes[attrName], 0)
                cmds.setAttr('%s.inputMin' % ramapNodes[attrName], -10)
            #end if
        #end loop

        #connect remap nodes to roll groups    
        #---Bank In/Out---
        if self._getSide() == common.LEFT:
            attribute.connect('%s.outValue' % ramapNodes['bank'],
                              '%s.rz' % footRollGroups[self.__bankIn])

            attribute.connect('%s.outValue' % ramapNodes['bank'],
                              '%s.rz' % footRollGroups[self.__bankOut])

            cmds.transformLimits(footRollGroups[self.__bankIn],
                    rz =[0, 100],
                    erz = [1, 1])

            cmds.transformLimits(footRollGroups[self.__bankOut],
                    rz =[-100, 0],
                    erz = [1, 1])
        elif self._getSide() == common.RIGHT:
            invertMDN = \
                cmds.createNode('multiplyDivide',
                        n = '%s_bankInvert_%s' % (self._getSide(),
                        common.MULTIPLYDIVIDE))

            cmds.setAttr('%s.input2X' % invertMDN, -1)
            attribute.connect('%s.outValue' % ramapNodes['bank'],
                    '%s.input1X' % invertMDN)

            attribute.connect('%s.outputX' % invertMDN,
                    '%s.rz' % footRollGroups[self.__bankIn])

            attribute.connect('%s.outputX' % invertMDN,
                    '%s.rz' % footRollGroups[self.__bankOut])

            cmds.transformLimits(footRollGroups[self.__bankIn],
                    rz =[-100, 0],
                    erz = [1, 1])

            cmds.transformLimits(footRollGroups[self.__bankOut],
                    rz =[0, 100],
                    erz = [1, 1])

        #---Ball Roll---
        attribute.connect('%s.outValue' % ramapNodes[self.__ballRoll],
                '%s.rx' % footRollGroups[self.__ballRoll])
        #---Toe Roll---
        attribute.connect('%s.outValue' % ramapNodes[self.__toeRoll],
                '%s.rx' % footRollGroups[self.__toeRoll])
        #---Toe Pivot---
        attribute.connect('%s.outValue' % ramapNodes[self.__toePivot],
                '%s.ry' % footRollGroups[self.__toePivot])
        #---Heel Roll---
        attribute.connect('%s.outValue' % ramapNodes[self.__heelRoll],
                '%s.rx' % footRollGroups[self.__heelRoll])
        #---Heel Pivot---
        attribute.connect('%s.outValue' % ramapNodes[self.__heelPivotName],
                '%s.ry' % footRollGroups[self.__heelPivotName])
        #---IK/FK---
        attribute.connect(ikfkAttr,
                '%s.ikfk' % self.__footIkFk.group)
        #---Ball Roll---
        attribute.connect('%s.outValue' % ramapNodes[self.__toeBend],
                '%s.rx' % footRollGroups[self.__toeBend])

        #connect fk joints to the ankle pivot
        #cmds.parentConstraint(footRollGroups['anklePivot'], self.__footIkFk.fkJoints[0], mo = True)

        #connecting visibility of control shapes to the controls
        ikfkReverse = \
            cmds.createNode('reverse', n = '%s_%s' % (self.name(),common.REVERSE))

        attribute.connect(ikfkAttr, '%s.inputX' % ikfkReverse)

        for ikCtrl in [self.__bankInCtrl,self.__bankOutCtrl,self.__heelPivotCtrl]:
            cmds.setAttr('%s.rotateOrder' % ikCtrl, 2)
            for shape in common.getShapes(ikCtrl):
                if shape:
                    attribute.connect('%s.outputX' % ikfkReverse, '%s.v' % shape)

        #----FK Setup---
        fkCtrls = list()
        parent = self.controlsGrp
        for jnt in self.__footIkFk.fkJoints:
            if jnt == self.__footIkFk.fkJoints[-1]:
                continue
            #end if

            ctrl = \
                control.create(name= jnt.split('_%s' % common.JOINT)[0],
                        type = 'circle',
                        parent = parent,
                        color = common.SIDE_COLOR[self._getSide()])

            ctrlParent = common.getParent(ctrl)
            transform.matchXform(jnt, ctrlParent, type = 'pose')
            cmds.parentConstraint(ctrl, jnt, mo = True) #----> might change this to connect rotations and not use translation
            if jnt == self.__footIkFk.fkJoints[0]:
                cmds.parentConstraint(footRollGroups['anklePivot'],
                    ctrlParent,
                    mo = True)
            #end if

            #connect visibility of shapes to foot control
            for shape in common.getShapes(ctrl):
                attribute.connect(ikfkAttr, '%s.v' % shape)
            #end for    
            parent = ctrl
            fkCtrls.append(ctrl)

        #assign hooks
        self.hookRoot.extend([footRollGroups['anklePivot'], common.getParent(fkCtrls[0])])
        self.hookPoint.extend([footRollGroups['ballRoll']])

    def postRig(self):
        super(Foot, self).postRig()

        #lock bank controls
        for node in (self.__bankInCtrl,self.__bankOutCtrl, self.__heelPivotCtrl):
            if common.isValid(node):
                attribute.lockAndHide(['rx','s', 'v'], node)
            #end if
        #end loop

        #lock and hide foot control attributes
        attribute.lockAndHide(['t', 'r', 's', 'v'], self.__footCtrl)

        for handle in self.__footIkFk.getIkHandles():
            cmds.setAttr('%s.v' % handle, 0 )
        #end loop

        cmds.setAttr('%s.v' % self.__footIkFk.ikJoints[0], 0)
        cmds.setAttr('%s.v' % self.__footIkFk.fkJoints[0], 0)
        cmds.setAttr('%s.v' % self.__footIkFk.blendJoints[0], 0)


