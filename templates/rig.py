'''
This is the rig template for all the rig templates

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
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

#import libs
import japeto.libs.common as common
import japeto.libs.attribute as attribute
import japeto.libs.joint as joint
import japeto.libs.control as control
import japeto.libs.ordereddict as ordereddict

#import components
import japeto.components.component as component

class Rig(object):
    def __init__(self, name):
        self.__name = name

        #declare group names of variables
        self.rigGrp      = name
        self.noXformGrp  = 'noXform'
        self.jointsGrp   = 'joints'
        self.controlsGrp = 'controls'
        self.modelGroup  = 'model'
        self.__trsCtrl   = 'trs_%s' % common.CONTROL
        self.__shotCtrl  = 'shot_%s' % common.CONTROL
        self.components  = ordereddict.OrderedDict()

        self.controls = list()

    #GETTERS
    @property
    def name(self):
        return self.__name

    @property
    def _shotCtrl(self):
        return self.__shotCtrl

    @property
    def _trsCtrl(self):
        return self.__trsCtrl

    def initialize(self):
        return True

    def mirror(self, side = common.LEFT):
        if side == common.LEFT:
            for component in self.components:
                if self.components[component]._getSide() == side:
                    guides = self.components[component].getGuides()

                    for guide in guides:
                        description = common.getDescription(guide)
                        joint.mirror(guide, '%s_%s' % (common.LEFT, description), '%s_%s' % (common.RIGHT, description))
        elif side == common.RIGHT:
            for component in self.components:
                if self.components[component]._getSide() == side:
                    guides = self.components[component].getGuides()

                    for guide in guides:
                        description = common.getDescription(guide)
                        joint.mirror(guide,
                                     '%s_%s' % (common.RIGHT, description),
                                     '%s_%s' % (common.LEFT, description))


    def register(self,name,object, **kwargs):
        '''
        Register build components to the user interface
        Example:
          ..python:
            register("Left Arm", limb.arm(), position = [20,10,10])

        @param name: Nice name for user interface
        @type name: *str*

        @param object: python object to be called when run() is called
        @type object: *method* or *function*
        '''
        if not inspect.ismethod (object) and not inspect.isfunction (object):
            # Check if object is a component
            if isinstance (object, component.Component):
                self.components[name] = object
                self.components[name].initialize(**kwargs)

    def setup(self):
        '''
        Runs the setup rig for each component registered to the system
        '''
        if self.components:
            for component in self.components:
                print component
                self.components[component].runSetupRig()

    def run(self):
        '''
        build each individual component registered to the build
        '''

        #loops through components and runs their runRig function
        if self.components:
            for component in self.components:
                self.components[component].runRig()
                if self.components[component].controls:
                    for ctrls in self.components[component].controls.values():
                        self.controls.extend(ctrls)

    def newScene(self):
        '''
        creates a fresh scene to start building an asset
        '''
        cmds.file(new = True, force = True)

    def preBuild(self):
        '''
        sets up the hierachry
        '''
        #create hierachy
        cmds.createNode('transform', n = self.rigGrp)
        cmds.createNode('transform', n = self.noXformGrp)
        cmds.createNode('transform', n = self.jointsGrp)
        cmds.createNode('transform', n = self.controlsGrp)

        #create shot and trs controls
        control.create(self._shotCtrl.replace('_%s' % common.CONTROL, ''), parent = self.controlsGrp, color = common.WHITE)
        control.create(self._trsCtrl.replace('_%s' % common.CONTROL, ''), parent = self._shotCtrl, color = common.WHITE)
        shotZero = common.getParent(self._shotCtrl)
        trsZero = common.getParent(self._trsCtrl)
        cmds.parent(self._shotCtrl, self.controlsGrp)
        cmds.parent(self._trsCtrl,self._shotCtrl)
        control.scaleShape(self._shotCtrl, [2,2,2])
        cmds.delete([shotZero, trsZero])
        #cmds.createNode('transform', n = self.modelGroup)

        cmds.parent([self.noXformGrp, self.jointsGrp, self.controlsGrp], self.rigGrp)

        #turn off inherit transforms on the noXformGrp
        cmds.setAttr('%s.inheritsTransform' % self.noXformGrp, 0)

        self.controls.extend([self._shotCtrl, self._trsCtrl])

    def build(self):
        '''
        build rig hiearchy and attatch components
        '''
        #create nodes on the rigGrp node
        tagAttr = control.tag_as_control(self.rigGrp)

        if self.controls:
            for ctrl in self.controls:
                attribute.connect(tagAttr, '%s.%s' % (ctrl, tagAttr.split('.')[1]))

        for component in self.components:
            cmds.parent(self.components[component].controlsGrp, self._trsCtrl)
            cmds.parent(self.components[component].jointsGrp, self.jointsGrp)
            cmds.delete(self.components[component].rigGrp)


    def postBuild(self):
        '''
        clean up rig asset
        '''
        attribute.lockAndHide(['s', 'v'], [self._shotCtrl, self._trsCtrl])
        pass
