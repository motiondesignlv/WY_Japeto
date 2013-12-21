'''
This is the leg component 

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    October 2012
'''
#import maya modules
import maya.cmds as cmds

#import package modules
#import libs
from japeto.libs import common
from japeto.libs import control
from japeto.libs import transform
from japeto.libs import joint

#import components
from japeto.components import component
from japeto.components import limb

class Leg(limb.Limb):
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Leg,self).initialize(**kwargs)

        self.addArgument('pelvisJoint',
                '%s_pelvis_%s_%s' % (self._getPrefix(),
                common. SKINCLUSTER,
                common.JOINT))

        self.addArgument('startJoint',
                '%s_upLeg_%s_%s' % (self._getPrefix(),
                 common. SKINCLUSTER,
                 common.JOINT))

        self.addArgument('midJoint',
                '%s_loLeg_%s_%s' % (self._getPrefix(),
                 common. SKINCLUSTER,
                 common.JOINT))

        self.addArgument('tipJoint',
                '%s_tipLeg_%s_%s' % (self._getPrefix(),
                common. SKINCLUSTER,
                common.JOINT))

    def setupRig(self):
        if super(Leg,self).setupRig():
            return True
        
        self.skinClusterJnts.remove(self.endJoint)
        self.skinClusterJnts.insert(0,self.pelvisJoint)

        #delete end joint and end guide
        cmds.delete(
            [self.endJoint, self.endJoint.replace(common.JOINT, common.GUIDES)]
        )

        if self._getSide() == common.LEFT:
            positions = (
                [self.position[0] + .5, self.position[1] + 14, self.position[2]],
                [self.position[0] + 2, self.position[1] + 12, self.position[2]],
                [self.position[0] + 2, self.position[1] + 7 , self.position[2] + 1],
                [self.position[0] + 2, self.position[1] + 2 , self.position[2]]
                )
        elif self._getSide() == common.RIGHT:
            positions = (
                [self.position[0] - .5, self.position[1] + 14, self.position[2]],
                [self.position[0] - 2, self.position[1] + 12, self.position[2]],
                [self.position[0] - 2, self.position[1] + 7, self.position[2] +1],
                [self.position[0] - 2, self.position[1] + 2, self.position[2]]
                )
        else:
            positions = (
                [self.position[0], self.position[1] + 14, self.position[2]],
                [self.position[0], self.position[1] + 12, self.position[2]],
                [self.position[0], self.position[1] + 7, self.position[2] +1],
                [self.position[0], self.position[1] + 2, self.position[2]]
                )


        #create pelvis joint and parent leg under pelvis
        joint.create(name = self.pelvisJoint,
                parent = self.skeletonGrp,
                position = positions[0])

        cmds.parent(self.startJoint, self.pelvisJoint)

        #declare guides
        pelvisJointGuide = \
            self.setupCtrl(
                self.pelvisJoint.replace('_%s' % common.JOINT, ''),
                self.pelvisJoint
            )
        startJointGuide  = self.startJoint.replace(common.JOINT, common.GUIDES)

        midJointGuide    = self.midJoint.replace(common.JOINT, common.GUIDES)

        tipJointGuide    = self.tipJoint.replace(common.JOINT, common.GUIDES)

        #change guide positions
        for i, guide in enumerate([pelvisJointGuide,startJointGuide,midJointGuide, tipJointGuide]):
            zeroGroup = common.getParent(guide)
            if i == 0:
                cmds.xform(
                    common.getParent(self.masterGuide),
                    ws = True,
                    t = positions[i]
                )
            cmds.xform(zeroGroup, ws = True, t = positions[i])

        cmds.delete(self.loTwistJnts)
        #clearing the loTwist jnts
        self.loTwistJnts = []

    def rig(self):
        if super(Leg,self).rig():
            return True

        #create pelvis control
        pelvisCtrl = \
            control.create(name = self.pelvisJoint.replace('_%s' % common.JOINT, ''),
                    type = 'cube',
                    parent = self.controlsGrp,
                    color = common.SIDE_COLOR[self._getSide()])
        #end loop

        common.setColor(pelvisCtrl, color = common.SIDE_COLOR[self._getSide()])
        pelvisCtrlZero = common.getParent(pelvisCtrl)
        transform.matchXform(self.pelvisJoint, pelvisCtrlZero, type = 'pose')
        cmds.parentConstraint(pelvisCtrl, self.pelvisJoint, mo = True)

        #parent fkCtrls under the pelvis control
        cmds.parent(common.getParent(self.controls['fk'][0]), pelvisCtrl)

        #parent constraint ik/fk joints to the pelvis control
        cmds.parentConstraint(self.pelvisJoint,self.joints['ik'][0], mo = True)
        cmds.parentConstraint(self.pelvisJoint, self.joints['target'][0], mo = True)

        #add joints to the joints dictionary
        self.joints['fk'].insert(0, self.pelvisJoint)

        #add controls to the control dictionary
        self.controls['fk'].insert(0,pelvisCtrl)


        self.hookRoot.pop(0)
        self.hookRoot.insert(0, pelvisCtrlZero)