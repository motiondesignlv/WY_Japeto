'''
This is the arm component 

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
import japeto.components.component as  component
import japeto.components.limb as limb

class Arm(limb.Limb):
	@component.overloadArguments
	def initialize(self,**kwargs):
		super(Arm,self).initialize(**kwargs)
		
		self.addArgument('clavicleJoint','%s_clavicle%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT), 5)
		self.addArgument('startJoint', '%s_upArm_%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT), 6)
		self.addArgument('midJoint', '%s_loArm_%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT), 7)
		self.addArgument('tipJoint', '%s_tipArm_%s_%s' % (self._getPrefix(), common. SKINCLUSTER, common.JOINT), 8)
		
		self.removeArgument('endJoint')
		
	def setupRig(self):
		if super(Arm,self).setupRig():
			return True
		
		self.skinClusterJnts.remove(self.endJoint)
		self.skinClusterJnts.insert(0,self.clavicleJoint)
		
		#delete end joint and end guide
		endJntGuide = self.endJoint.replace(common.JOINT, common.GUIDES)
		if common.isValid(self.endJoint):
			cmds.delete(self.endJoint)
		if common.isValid(endJntGuide):
			cmds.delete(endJntGuide)
			

		if self._getSide() == common.LEFT:
			positions = (
				[self.position[0] + .5, self.position[1], self.position[2] + 1],
				[self.position[0] + 2, self.position[1], self.position[2]],
				[self.position[0] + 5, self.position[1], self.position[2] - 1],
				[self.position[0] + 8, self.position[1], self.position[2]]
				)
		elif self._getSide() == common.RIGHT:
			positions = (
				[self.position[0] + -.5, self.position[1], self.position[2] + 1],
				[self.position[0] - 2, self.position[1], self.position[2]],
				[self.position[0] - 5, self.position[1], self.position[2] - 1],
				[self.position[0] - 8, self.position[1], self.position[2]]
				)
		else:
			positions = (
				[self.position[0] + .5, self.position[1], self.position[2] + 1],
				[self.position[0] + 2, self.position[1], self.position[2]],
				[self.position[0] + 5, self.position[1], self.position[2] - 1],
				[self.position[0] + 8, self.position[1], self.position[2]]
				)


		#create pelvis joint and parent leg under pelvis
		if not common.isValid(self.clavicleJoint):
			joint.create(name = self.clavicleJoint, parent = self.skeletonGrp, position = positions[0])
		
		cmds.parent(self.startJoint, self.clavicleJoint)
		
		#declare guides
		clavicleJointGuide = self.setupCtrl(self.clavicleJoint.replace('_%s' % common.JOINT, ''),self.clavicleJoint)
		startJointGuide  = self.startJoint.replace(common.JOINT, common.GUIDES)
		midJointGuide    = self.midJoint.replace(common.JOINT, common.GUIDES)
		tipJointGuide    = self.tipJoint.replace(common.JOINT, common.GUIDES)
		
		#move master guide to clavicle position
		for i, guide in enumerate([clavicleJointGuide,startJointGuide,midJointGuide, tipJointGuide]):
			zeroGroup = common.getParent(guide)
			if i == 0:
				cmds.xform(common.getParent(self.masterGuide), ws = True, t = positions[i])
			cmds.xform(zeroGroup, ws = True, t = positions[i])
		
		
	def rig(self):
		if super(Arm,self).rig():
			return True
		'''
		if common.isValid(self.clavicleJoint.replace('_%s' % common.JOINT,common.CONTROL)):
			return True
		'''
		#create pelvis control
		clavicleCtrl = control.create(
							name = self.clavicleJoint.replace('_%s' % common.JOINT,''),
							type = 'cube',
							parent = self.controlsGrp,
							color = common.SIDE_COLOR[self._getSide()])
		
		common.setColor(clavicleCtrl, color = common.SIDE_COLOR[self._getSide()])
		clavicleCtrlZero = common.getParent(clavicleCtrl)
		transform.matchXform(self.clavicleJoint, clavicleCtrlZero, type = 'pose')
		cmds.parentConstraint(clavicleCtrl, self.clavicleJoint, mo = True)
		
		#parent fkCtrls under the pelvis control
		cmds.parent(common.getParent(self.controls['fk'][0]), clavicleCtrl)
		
		#parent constraint ik/fk joints to the pelvis control
		cmds.parentConstraint(self.clavicleJoint,self.joints['ik'][0], mo = True)
		cmds.parentConstraint(self.clavicleJoint, self.joints['target'][0], mo = True)
		
		#add joints to the joints dictionary
		self.joints['fk'].insert(0, self.clavicleJoint)
		
		#add controls to the control dictionary
		self.controls['fk'].insert(0,clavicleCtrl)
		
		
		self.hookRoot.pop(0)
		self.hookRoot.insert(0, clavicleCtrlZero)