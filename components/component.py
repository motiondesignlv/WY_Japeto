'''
This is the base component for all the rig components

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#import python modules
from functools import partial
from functools import wraps
import inspect
import copy
import sys
import os

#import maya modules
import maya.cmds as cmds

#import package modules
#libs
from japeto.libs import common, attribute, joint, control
#components
import japeto.components.puppet as puppet

#import decompose matrix plugin
try:
    cmds.loadPlugin('matrixNodes.bundle')
except:
    pass


# Overload Arguments Decorator
def overloadArguments (func):
    '''
    Overload default arguments decorator

    @param func: Function to decorate
    @type func: *Function*

    @return: Return function
    @rtype: *Function*
    '''
    # Define wrapper
    @wraps (func)
    def wrapper (self, *args, **kwargs):
        # Run function
        result = func (self, *args, **kwargs)
        
        # Check if default arguments were given
        if kwargs:
            # Loop through keyword arguments
            for key in kwargs.keys ():
                # Check if key is in arguments
                if vars(self).has_key(key):
                    # Overload argument value
                    vars (self) [key] = kwargs [key]
                    self._buildArguments [key] = kwargs [key]

        # Return function output
        return result
    return wrapper


class Component(object):
    def __init__(self, name):
	self.name = name
	
	#declare group names of variables
	self.setupRigGrp = '%s_setup_%s' % (name, common.GROUP)
	self.skeletonGrp = '%s_skeleton_%s' %(name,common.GROUP)
	self.guidesGrp   = '%s_guides_%s' % (name, common.GROUP)
	
	self.rigGrp   = '%s_rig_%s' % (name, common.GROUP)
	self.jointsGrp   = '%s_joints_%s' % (name, common.GROUP)
	self.controlsGrp   = '%s_controls_%s' % (name, common.GROUP)
	self.setupConstraints = list()
	self.__side = common.getSide(name) #checks if there is a side based off name template
	self.__location = common.getLocation(name) #checks if there is a location based off name template
	self.skinClusterJnts = list()
	self.joints = dict()
	self.controls = dict()
	self.hookRoot = list()
	self.hookPoint = list()
	self._buildArguments = dict()
	self._puppetNode = str()
    
    #----------------------------------
    #GETTERS
    #----------------------------------
    @property
    def buildArguments(self):
	return self._buildArguments
    
    @property
    def puppetNode(self):
	return self._puppetNode
    
    def _getSide(self):
	'''
	Returns side from naming template
	'''
	return self.__side
    
    def _getLocation(self):
	'''
	Returns location from naming template
	'''
	return self.__location
    
    def _getPrefix(self):
	'''
	Returns the prefix based off of both side and location
	'''
	location = self._getLocation()
	side = self._getSide()
	if location:
	    return ('%s_%s' % (side, location))
	
	return side
    
    
    #----------------------------------
    #SETTERS
    #----------------------------------
    @puppetNode.setter
    def puppetNode(self, value):
	self._puppetNode = value
	
    def _setSide(self, value):
	self.__side = value
	
    def _setLocation(self, value):
	self.__location = value
	
    def _addSetupConstraints(self, constraint):
	self.setupConstraints.append(constraint)


    #Initialize
    @overloadArguments
    def initialize(self, **kwargs):
	self.addArgument('position', [0,0,0])
	self.addArgument('controlScale', 1)
	self.addArgument('parent', str())

    #----------------------------------
    #SETUP FUNCTIONS
    #----------------------------------    
    def setupRig(self):
	#makes component a puppet node
	self.puppetNode = puppet.create(self.name)
	
	#Create master guide control and 
	self.masterGuide = control.createSetup('%s_master' % self.name, type = 'square')
	common.setColor(self.masterGuide, 'darkred')
	
	#create hierarchy
	cmds.createNode('transform', n = self.setupRigGrp)
	cmds.createNode('transform', n = self.skeletonGrp)
	cmds.createNode('transform', n = self.guidesGrp)
	
	cmds.parent(self.skeletonGrp, self.setupRigGrp)
	cmds.parent(self.guidesGrp, self.setupRigGrp)
	cmds.parent(common.getParent(self.masterGuide),self.guidesGrp)
	
	#add attributes to groups
	attribute.addAttr(self.setupRigGrp, 'tag_guides', attrType = 'message')
	masterGuideAttr = attribute.addAttr(self.setupRigGrp, 'master_guide', attrType = 'message')
	attribute.connect(masterGuideAttr, '%s.tag_controls' % self.masterGuide)

    
    def postSetupRig(self):
	'''
	clean up section for the setup rig
	'''
	#create attributes and lock/hide attrs on top nodes as well as masterGuide control
	displayAttr = attribute.addAttr(self.masterGuide, 'displayAxis', attrType = 'enum', defValue = 'off:on')	
	attribute.lockAndHide(['r','t','s','v'], [self.setupRigGrp, self.skeletonGrp,self.guidesGrp, common.getParent(self.masterGuide)])
	attribute.lockAndHide('v', self.masterGuide)
	
	#resize guide controls
	for guide in self.getGuides():
	    cmds.setAttr('%s.radius' % common.getShapes(guide, 0), self.controlScale * .5)
	
	#resize masterGuide control
	control.scaleShape(self.masterGuide, scale = [self.controlScale * 2, self.controlScale * 2, self.controlScale * 2])
	
	#declaring skeleton joints
	skeletonJnts = self.getSkeletonJnts()
	
	#connect joints to the attributes on the masterGuide control
	for jnt in skeletonJnts:
	    if cmds.objExists(jnt):
		attribute.connect(displayAttr , '%s.displayLocalAxis' % jnt)
		common.setDisplayType(jnt, 'reference')	
		
	#parent all constraints to guides group
	if self.setupConstraints:
	    cmds.parent(self.setupConstraints, self.guidesGrp)

	#Put the build attributes onto setup rigs
	'''
	cmds.addAttr(self.setupRigGrp, ln = 'kwargs', dt = "string")
	cmds.setAttr('%s.kwargs' % self.setupRigGrp, str(self._buildAttrs), type = "string")
	'''
	attribute.copy('displayAxis', self.masterGuide, self.name, reverseConnect = True)
	
	#parent setup under puppet node
	self._puppetNode.addChild(self.setupRigGrp)
	
	if self.parent:
	    if cmds.objExists(self.parent):
		displayLine = control.displayLine(self.masterGuide, self.parent, name = self.masterGuide.replace('_%s' % common.GUIDES, '_%s' % common.CURVE))
		cmds.parent(displayLine, self.guidesGrp)
		
	#set build args on puppet node
	self.puppetNode.storeArgs(**self.buildArguments)
	
    def runSetupRig(self):
	'''
	runs both the setup and postSetup for the rig. 
	'''
	self.setupRig()
	self.postSetupRig()
	
    
    #----------------------------------
    #BUILD FUNCTIONS
    #----------------------------------		    
    def rig(self):
	'''
	this is the build section for the rig.
	'''
	#resolve build arguments
	self.puppetNode.restoreArgs(self)
	
	cmds.createNode('transform', n = self.rigGrp)
	cmds.createNode('transform', n = self.jointsGrp)
	cmds.createNode('transform', n = self.controlsGrp)
	
	cmds.parent([self.jointsGrp, self.controlsGrp], self.rigGrp)
	
	if not self.skinClusterJnts:
		self.skinClusterJnts.extend(self.getSkeletonJnts())
	
	for jnt in self.skinClusterJnts:
	    if cmds.objExists(jnt):
		common.setDisplayType(jnt, 'normal')
		#get parent jnt 
		parent = cmds.listRelatives(jnt, p = True)
		if parent:
		    if parent[0] == self.skeletonGrp:
			cmds.parent(jnt, self.jointsGrp)
					
	cmds.delete(self.setupRigGrp)
	
	for jnt in self.skinClusterJnts:
	    if cmds.objExists(jnt):
		#turn display axis off
		cmds.setAttr('%s.displayLocalAxis' % jnt, 0)
		#take the rotations of the joint and make the orientaion
		joint.rotateToOrient(jnt)
		
	    
    def postRig(self):
	'''
	clean up for the rig build.
	'''
	jointVisAttr     = attribute.addAttr(self.rigGrp, 'jointVis', attrType = 'enum', defValue = 'off:on')
	scaleAttr        = attribute.addAttr(self.rigGrp, 'uniformScale', attrType = 'double', defValue = 1, min = 0)
	jointDisplayAttr = attribute.addAttr(self.rigGrp, 'displayJnts', attrType = 'enum', defValue = 'Normal:Template:Reference')
	
	cmds.setAttr(jointDisplayAttr, 2)
	
	#setup attribute for uniform scale
	attribute.connect(scaleAttr, '%s.sx' % self.rigGrp)
	attribute.connect(scaleAttr, '%s.sy' % self.rigGrp)
	attribute.connect(scaleAttr, '%s.sz' % self.rigGrp)
	    
	if self.skinClusterJnts:
	    for jnt in self.skinClusterJnts:
		if cmds.objExists(jnt):
		    attribute.connect(jointVisAttr , '%s.v' % jnt)
		    cmds.setAttr('%s.overrideEnabled' % jnt, 1)
		    attribute.connect(jointDisplayAttr , '%s.overrideDisplayType' % jnt)
				    
				    
	#set joint visibility attribute
	cmds.setAttr(jointVisAttr, 1)
	
	for grp in [self.rigGrp, self.jointsGrp, self.controlsGrp]:
	    attribute.lockAndHide(['t', 'r', 's', 'v'], grp)
	
    
    def runRig(self):
	self.rig()
	self.postRig()
	
	
    #-------------------------------
    #utility functions
    #-------------------------------
    def setupCtrl(self, name, obj, color = None):
	'''
	@param name: The name of control created
	@type name: *str*	
	
	@param obj: object to be controled
	@type obj: *str*
	
	@param color: object to be controled
	@type color: *str*
	
	@return: Guide control
	@rtype: *str*	
	'''
	#create hierarchy
	guideZero = cmds.createNode('transform', n = '%s_%s' % (name, common.ZERO))
	guideShape = cmds.createNode('implicitSphere',n = '%s_%sShape' % (name,common.GUIDES))
	guide = common.getParent(guideShape)
	guide = cmds.rename(guide, name + '_' + common.GUIDES)
	
	#set color
	if color:
	    common.setColor(guideShape, color)
	else:
	    common.setColor(guideShape, common.SIDE_COLOR[self._getSide()])
	
	#parent guide to zero group
	cmds.parent(guide, guideZero)
	
	cmds.delete(cmds.parentConstraint(obj, guideZero, mo = False))
	
	constraint = cmds.pointConstraint(guide, obj)
	
	cmds.parent([guideZero, constraint[0]],self.masterGuide)
	
	#lock and hide attributes
	attribute.lockAndHide(['r','s', 'v'], guide)
	
	#tag the guide control with a tag_guides attribute
	tagAttr = attribute.addAttr(guide, 'tag_guides', attrType = 'message')
	
	#connect attribute to the setupRigGrp
	attribute.connect('%s.tag_guides' % self.setupRigGrp, tagAttr)
	
	return guide


    def getGuides(self):
	guides = list()
	guideAttrs = attribute.getConnections('tag_guides', self.setupRigGrp)
	for attr in guideAttrs:
	    guides.append(attr.split('.')[0])
	    
	return guides

	    
    def getSkeletonJnts(self):
	skeletonJnts = list()
	skeletonRels = cmds.listRelatives(self.skeletonGrp, ad = True, type = 'joint')
	
	if skeletonRels:
	    for jnt in skeletonRels:
		if cmds.objExists(jnt):
		    if cmds.nodeType(jnt) == 'joint':
			skeletonJnts.append(jnt)
					
	return skeletonJnts
        

    def addArgument(self, name, value):
	'''
	this is how it's done
	'''
	#adds key and value to __dict__ attribute, which is a dictionary.
	vars(self) [name] = value
	self._buildArguments[name] = value
	
	
    def _getBuildAttrs(self):
	pass
