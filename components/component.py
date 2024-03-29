'''
This is the base component for all the rig components

:author: Walter Yoder
:contact: walteryoder:gmail.com
:date: October 2012
'''

#import python modules
from functools import wraps

#import maya modules
import maya.cmds as cmds

#import package modules
#libs
from japeto.libs import common 
from japeto.libs import attribute
from japeto.libs import joint
from japeto.libs import control
from japeto.libs import fileIO
from japeto.mlRig import ml_node
reload(ml_node)
reload(control)

#components
import japeto.components.puppet as puppet
reload(puppet)

#import decompose matrix plugin
fileIO.loadPlugin('matrixNodes.bundle')


# Overload Arguments Decorator
def overloadArguments (func):
    '''
    Overload default arguments decorator

    :param func: Function to decorate
    :type func: *Function*

    :return: Return function
    :rtype: *Function*
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
                    for attr in self.attributes():
                        if key == attr.name():
                            attr.setValue(kwargs[key])
                            break

        # Return function output
        return result
    return wrapper


class Component(ml_node.MlNode):
    def __init__(self, name):
        super(Component, self).__init__(name)
        self.setName(name)
        
        self.skinClusterJnts  = list()
        self.joints           = dict()
        self.controls         = dict()
        self.hookRoot         = list()
        self.hookPoint        = list()
        self.setupConstraints = list()
        self._buildArguments  = dict()
        self._puppetNode      = str()
        self.setColor((113,193,113))
        

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
        self.__side = common.getSide(self.name())
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
    
    def getParent(self):
        return super(Component, self).parent()
    
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
        #declare group names of variables
        self.setupRigGrp = '%s_setup_%s' % (self.name(), common.GROUP)
        self.skeletonGrp = '%s_skeleton_%s' %(self.name(),common.GROUP)
        self.guidesGrp   = '%s_guides_%s' % (self.name(), common.GROUP)
        
        self.rigGrp   = '%s_rig_%s' % (self.name(), common.GROUP)
        self.jointsGrp   = '%s_joints_%s' % (self.name(), common.GROUP)
        self.controlsGrp   = '%s_controls_%s' % (self.name(), common.GROUP)
        self.__side = common.getSide(self.name()) #checks if there is a side based off name template
        self.__location  = common.getLocation(self.name()) #checks if there is a location based off name template
        self.masterGuide = '%s_master_%s' % (self.name(), common.GUIDES)
        
        self.addArgument('position', [0,0,0], 0)
        self.addArgument('controlScale', 1, 1)
        self.addArgument('parentHook', str(), 2)

    #----------------------------------
    #SETUP FUNCTIONS
    #----------------------------------    
    def setupRig(self):
        if common.isValid(self.name()):
            return True
        
        self.setupConstraints = []
        #makes component a puppet node
        self.puppetNode = puppet.create(self.name())
        
        #Create master guide control and 
        control.createSetup('{0}_master'.format(self.name()), type = 'square')
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
        if common.isValid('%s.displayAxis' % self.masterGuide) or common.isValid(self.masterGuide) != True:
            return True
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
        attribute.copy('displayAxis', self.masterGuide, self.name(), reverseConnect = True)
        
        #parent setup under puppet node
        self._puppetNode.addChild(self.setupRigGrp)
        
        if self.parentHook:
            if cmds.objExists(self.parentHook):
                displayLine = control.displayLine(self.masterGuide, self.parentHook, name = self.masterGuide.replace('_%s' % common.GUIDES, '_%s' % common.CURVE))
                cmds.parent(displayLine, self.guidesGrp)

        #set build args on puppet node
        attrs = dict()
        for attr in self.attributes():
            attrs[attr.name()] = attr.value()
        self.puppetNode.storeArgs(**attrs)
        
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
        if common.isValid(self.controlsGrp):
            return True
        
        if not self._puppetNode:
            self.runSetupRig()
        
        #resolve build arguments
        if not self.puppetNode == self.name():
            self.puppetNode = puppet.Puppet(self.name())
        
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
        
        #delete the setup rig group
        cmds.delete(self.setupRigGrp)
        
        for jnt in self.skinClusterJnts:
            if cmds.objExists(jnt):
                #turn display axis off
                cmds.setAttr('%s.displayLocalAxis' % jnt, 0)
                #take the rotations of the joint and make the orientation
                joint.rotateToOrient(jnt)


    def postRig(self):
        '''
        clean up for the rig build.
        '''
        if common.isValid('%s.jointVis' % self.rigGrp):
            return True
        
        if cmds.ls(type = 'rig') and common.isValid(self.controlsGrp) and not common.isValid(self.rigGrp):
            return True
        
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
        :param name: The name of control created
        :type name: *str*	
        
        :param obj: object to be controled
        :type obj: str
        
        :param color: object to be controled
        :type color: str
        
        :return: Guide control
        :rtype: str	
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
        '''
        Grabs the guides from the guides group created from the setup process
        '''
        guides = list()
        guideAttrs = attribute.getConnections('tag_guides', self.setupRigGrp)
        if guideAttrs:
            for attr in guideAttrs:
                guides.append(attr.split('.')[0])
        return guides


    def getSkeletonJnts(self):
        '''
        This grabs all teh skeleton joints from the skeleton group in the
        setup function
        '''
        skeletonJnts = list()
        skeletonRels = cmds.listRelatives(self.skeletonGrp, ad = True, type = 'joint')
        
        if skeletonRels:
            for jnt in skeletonRels:
                if cmds.objExists(jnt):
                    if cmds.nodeType(jnt) == 'joint':
                        skeletonJnts.append(jnt)
                        
        return skeletonJnts
        

    def addArgument(self, name, value, index = -1):
        '''
        this is how it's done
        '''
        #adds key and value to __dict__ attribute, which is a dictionary.
        vars(self) [name] = value
        self.addAttribute(name, value, index)
        
    def removeArgument(self, name):
        '''
        This removes the attribute but does not remove the class attibute
        since the build still needs certain attributes to run from parent
        classes. This will ensure that the builds are stable, but attributes
        shown in the ui can be added and removed.
        
        :param name: Name of the attribute you wish to remove
        :type name: str
        '''
        #del(vars(self)[name])
        attr = self.getAttributeByName(name)
        self.removeAttribute(attr)
