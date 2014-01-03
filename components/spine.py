'''
This is the Spine component.

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    September 2013
'''
#import maya modules
from maya import cmds

#import package modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import ikfk
from japeto.libs import control
from japeto.libs import transform

from japeto.components import component
from japeto.components import chain

class Spine(chain.Chain):
    def __init__(self, name):
        super(Spine, self).__init__(name)
        self.__spineIkFk       = str()
        self.controls['tweak'] = list()
        self.controls['ik']    = list()
        self.controls['fk']    = list()
        self.curve             = str()
        self.driverJoints      = list()
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Spine,self).initialize(**kwargs)
        
        self.addArgument('numControls', 2, 4)
        
        #TODO: Place builds arguments specific to the spine

    def setupRig(self):
        if super(Spine, self).setupRig():
            return True
        
    def rig(self):
        if component.Component.rig(self):
            return True
        
        self.__spineIkFk = ikfk.SplineIk(self.startJoint,
            self.endJoint,
            name = self.name())
        
        if self.numControls == 2:
            self.__spineIkFk.create([0, -1])
        elif self.numControls == 3:
            self.__spineIkFk.create([0, 2, -1])
            #torsoDriverJnt = self.__spineIkFk.driverJoints[1] 
        
        self.ikFkGroup    = self.__spineIkFk.group
        self.curve        = self.__spineIkFk.curve
        #ikHipJnt          = self.__spineIkFk.ikJoints[0]
        #ikChest           = self.__spineIkFk.ikJoints[-1]
        self.ikJoints     = self.__spineIkFk.ikJoints
        self.fkJoints     = self.__spineIkFk.fkJoints
        self.blendJoints  = self.__spineIkFk.blendJoints
        self.driverJoints = self.__spineIkFk.driverJoints
        #upAxis            = self.__spineIkFk.upAxis
        aimAxis           = self.__spineIkFk.aimAxis
        #hipDriverJnt      = self.__spineIkFk.driverJoints[0]
        #chestDriverJnt    = self.__spineIkFk.driverJoints[-1]
        
        #FK Control Setup
        self.controls['fk'] = self._fkControlSetup(self.__spineIkFk.fkJoints)    
        
        #IK Controls setup
        self.controls['ik'] = self._ikControlSetup(self.driverJoints)
        
        if len(self.controls['ik']) == 3:
            cmds.pointConstraint(self.controls['ik'][0],
                                 self.controls['ik'][-1],
                                 common.getParent(self.controls['ik'][1]),
                                 mo = True)
        #end if
        
        #stretch spine
        ikfk.IkFkSpline.addParametricStretch(crv= self.curve.name,
                                             scaleCompensate= False,
                                             scaleAxis= aimAxis,uniform= False,
                                             useTranslationStretch= False)
    
    def postRig(self):
        if super(Spine, self).postRig():
            return True
        
        cmds.setAttr('%s.ikfk' % self.ikFkGroup, 0)
        
        cmds.setAttr('%s.v' % self.curve.fullPathName,0)
        cmds.setAttr('%s.v' % self.__spineIkFk.ikHandle,0)
        
        #add roots and point hooks
        self.hookRoot.pop(0)
        self.hookRoot.insert(0,common.getParent(self.controls['ik']))
        
        for jnt in self.__spineIkFk.splineJoints:
            cmds.setAttr('%s.v' % jnt, 0)
        
        for jnt in self.__spineIkFk.driverJoints:
            cmds.setAttr('%s.v' % common.getParent(jnt), 0)
        
        #----------------------------------        
    
    def _ikControlSetup(self, drivers):
        '''
        Takes driver joints that drive the IK spine and create controls for them
        
        @param drivers: list of drivers you want to put controls on
        @type drivers: *list* or *tuple* or *str* 
        
        @return: IK controls which were created to drive the driver joints passed in
        @rtype: *list*
        '''
        #create an empty list to store ik controls in so we can return them
        ikControls = list()
        
        drivers = common.toList(drivers)
        
        for i,driver in enumerate(drivers):
            nameDescription = common.getDescription(driver)
            ctrlName = '%s_%s_%s' % (self._getSide(),nameDescription,common.IK)
            ctrl = control.create(ctrlName, type = 'cube',
                                  parent = self.controlsGrp,
                                  color = common.SIDE_COLOR[self._getSide()])
            ctrlZero = common.getParent(ctrl)
            #driverParent = common.getParent(driver)
            #move control in to position of driver jnt
            transform.matchXform(driver, ctrlZero, 'pose')
            #cmds.parent(ctrlZero, driverParent)
            #cmds.parent(driver, ctrl)
            cmds.parentConstraint(ctrl, driver,mo = True)
            
            
            #connect ik/fk attr from group to  visibility of shapes
            reverse = cmds.createNode('reverse', n = '%s_%s_%s' % (self.name(),
                                                                common.IK,
                                                                common.REVERSE
                                                                ))
            attribute.connect('%s.ikfk' % self.ikFkGroup,'%s.inputX' % reverse)
            for shape in common.getShapes(ctrl):
                if self.ikFkGroup:
                    attribute.connect('%s.outputX' % reverse,
                                      '%s.v' % shape)
                #end if
            #end loop
            
            ikControls.append(ctrl)
            
            
            
        #end loop
            
        return ikControls
        