'''
This is the rig template for all the rig templates

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#import python modules
import inspect
import os

#import maya modules
from maya import cmds
#import package modules

#import libs
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import joint
from japeto.libs import control 
from japeto.libs import ordereddict

#import components
from japeto.components import component


class Rig(object):
    @classmethod
    def getControls(cls, asset):
        '''
        Get controls based on whether or not the given asset has
        a tag_controls attribute.
        
        @param asset: Asset you want to get controls from
        @type asset: *str*
        
        @return: Returns controls on the given asset
        @rtype: *list* or *None*
        '''
        controlAttr = '%s.tag_controls' % asset
        
        if common.isValid(controlAttr):
            return attribute.getConnections(controlAttr, plugs = False)
        #end if
            
        return None
    
    @classmethod
    def saveControls(cls, controls, filePath):
        '''
        Save the controls for the asset
        
        @param controls: controls that will be written out 
                        if they're nurbsCurves
        @type controls: *list* or *str* or *tuple*
        '''
        #declare list that will be used to gather controls to save
        savedControls = list()
        #make sure controls is a list before proceeding
        controls = common.toList(controls)
        
        if not isinstance(controls, list):
            raise RuntimeError('%s must be a list' % controls)
        #end if
        
        for ctrl in controls:
            if common.isValid(ctrl):
                if common.isType(ctrl, 'nurbsCurve') or common.isType(common.getShapes(ctrl, 0), 'nurbsCurve'):
                    savedControls.append(ctrl)
            #end if
        #end loop
        
        #save the controls in savedControls list
        control.save(savedControls, filepath = filePath)
    
    
    def __init__(self, name):
        self.__name = name

        #declare group names of variables
        self.rigGrp      = name
        self.noXformGrp  = 'noXform'
        self.jointsGrp   = 'joints'
        self.controlsGrp = 'controls'
        self.modelGroup  = 'model'
        self.__trsCtrl   = 'world_trs_%s' % common.CONTROL
        self.__shotCtrl  = 'shot_trs_%s' % common.CONTROL
        self.components  = ordereddict.OrderedDict() 
        self.functions   = ordereddict.OrderedDict() 
        self.controls    = list()
        
        self.__registeredItems = list()


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
    
    @property
    def registeredItems(self):
        return self.__registeredItems

    def initialize(self):
        return True

    def mirror(self, side = common.LEFT):
        '''
        This will mirror across from side given to the opposite side
        
        @see: japeto.libs.joint.mirror()
        
        @param side: Side to use to mirror from
        @type side: *str*  
        '''
        if side == common.LEFT:
            for component in self.components:
                if self.components[component]._getSide() == side:
                    guides = self.components[component].getGuides()

                    for guide in guides:
                        description = common.getDescription(guide)
                        joint.mirror(guide, '%s_%s' % (common.LEFT, description), 
                                     '%s_%s' % (common.RIGHT, description))
        elif side == common.RIGHT:
            for component in self.components:
                if self.components[component]._getSide() == side:
                    guides = self.components[component].getGuides()

                    for guide in guides:
                        description = common.getDescription(guide)
                        joint.mirror(guide,
                                     '%s_%s' % (common.RIGHT, description),
                                     '%s_%s' % (common.LEFT, description))


    def register(self,name, obj, **kwargs):
        '''
        Register build components to the user interface
        @example:
            >>> register("Left Arm", limb.arm(), position = [20,10,10])
            
        @param name: Nice name for user interface
        @type name: *str*

        @param object: python object to be called when run() is called
        @type object: *method* or *function*
        '''
        if not inspect.ismethod (obj) and not inspect.isfunction (obj):
            # Check if object is a component
            if isinstance (obj, component.Component):
                self.components[name] = obj
                self.components[name].initialize(**kwargs)
                self.__registeredItems.append(name)
        elif inspect.isfunction(obj) or inspect.ismethod (obj):
            self.functions[name] = (obj,kwargs)
            self.__registeredItems.append(name)

    def setup(self):
        '''
        Runs the setup rig for each component registered to the system
        '''
        if self.components:
            for component in self.components:
                self.components[component].runSetupRig()
            #end loop
        #end if

    def run(self):
        '''
        build each individual component, or function in the order it was
        registered to the build
        '''

        #loops through components and runs their runRig function
        if self.__registeredItems:
            print self.__registeredItems
            for item in self.__registeredItems:
                if self.components.has_key(item):
                    self.components[item].runRig()
                    if self.components[item].controls:
                        for ctrls in self.components[item].controls.values():
                            for ctrl in ctrls:
                                if ctrl not in self.controls:
                                    self.controls.append(ctrl)
                                #end if
                            #end loop
                        #end loop
                    #end if
                #end if
                elif self.functions.has_key(item):
                    self._runFunction(item)
                #end elif
            #end loop
        #end if

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
        control.create(self._shotCtrl.replace('_%s' % common.CONTROL, ''),
                       parent = self.controlsGrp, color = common.WHITE)
        control.create(self._trsCtrl.replace('_%s' % common.CONTROL, ''),
                       parent = self._shotCtrl, color = common.WHITE)
        #get the parents of the controls
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
            #end loop
        #end if

        for component in self.components:
            cmds.parent(self.components[component].controlsGrp, self._trsCtrl)
            cmds.parent(self.components[component].jointsGrp, self.jointsGrp)
            cmds.delete(self.components[component].rigGrp)
        #end loop


    def postBuild(self):
        '''
        clean up rig asset
        '''
        attribute.lockAndHide(['s', 'v'], [self._shotCtrl, self._trsCtrl])

    def _runFunction(self, name):
        '''
        Check to see if the given name is a key in self.functions ordereddict
        
        @warning: This function should not be used outside of this class
                  unless it's a subclass
        
        @see: Rig.register() and Rig.__init__()
        
        @param name: Name of the key which the function was registered
        @type name: *str* 
        
        '''
        #check to see if function exists
        if self.functions.has_key(name):
            #parse dictionary for values
            func   = self.functions[name][0]
            kwargs = self.functions[name][1]
            
            #run function
            func(**kwargs)
        
        return

    def exportControls(self):
        '''
        This will export controls for the asset
        
        @see: Rig.saveControls(controls, filePath)
        
        @warning: This will put any control you try to export in the current 
                  directory of this file. It should be exporting to an asset directory
        
        @todo: Find out where the controls will be saved.
        @todo: Figure out how we will store the file path for an asset
        '''
        Rig.saveControls(Rig.getControls(self.name), filePath = os.path.join(os.path.dirname(__file__), '%s.%s' % (self.name, common.CONTROL)))
