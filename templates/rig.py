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
from japeto import PLUGINDIR

#import libs
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import joint
from japeto.libs import control
from japeto.libs import ordereddict
from japeto.libs import fileIO

#import components
from japeto.components import component
from japeto.mlRig import ml_graph
from japeto.mlRig import ml_node

fileIO.loadPlugin(os.path.join(PLUGINDIR, 'rigNode.py'))

reload(ml_graph)

class Rig(ml_graph.MlGraph):
    @classmethod
    def getControls(cls, asset):
        '''
        Get controls based on whether or not the given asset has
        a tag_controls attribute.
        
        :param asset: Asset you want to get controls from
        :type asset: str
        
        :return: Returns controls on the given asset
        :rtype: list | None
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
        
        :param controls: controls that will be written out 
                        if they're nurbsCurves
        :type controls: list | str | tuple
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
        super(Rig, self).__init__(name)

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
        self.filePath    = os.path.join(os.path.dirname(__file__), 
                                        '%s.%s' % (self.name(), common.CONTROL))
        
        self.__registeredItems = list()
        self.skinClusterJoints = list()

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
        self.register('New Scene', self.newScene)
        self.register('Pre-Build', self.preBuild)
        self.register('Build', self.build)
        self.register('Post-Build', self.postBuild)
        #self.register(name, obj, parent)
        return True

    def mirror(self, side = common.LEFT):
        '''
        This will mirror across from side given to the opposite side
        
        :see: japeto.libs.joint.mirror
        
        :param side: Side to use to mirror from
        :type side: str
        '''
        if side == common.LEFT:
            for node in self.nodes():
                if not isinstance(node, component.Component):
                    continue
                if node._getSide() == side:
                    guides = node.getGuides()

                    for guide in guides:
                        description = common.getDescription(guide)
                        joint.mirror(guide, '%s_%s' % (common.LEFT, description), 
                                     '%s_%s' % (common.RIGHT, description))
        elif side == common.RIGHT:
            for node in self.nodes():
                if not isinstance(node, component.Component):
                    continue
                if node._getSide() == side:
                    guides = node.getGuides()

                    for guide in guides:
                        description = common.getDescription(guide)
                        joint.mirror(guide,
                                     '%s_%s' % (common.RIGHT, description),
                                     '%s_%s' % (common.LEFT, description))

    def register(self, name, obj, parent = str(), after = None, before = None, **kwargs):
        '''
        Register build components to the user interface
        :example:
            >>> register("Left Arm", limb.arm(), position = [20,10,10])
            
        :param name: Nice name for user interface
        :type name: str

        :param object: python object to be called when run() is called
        :type object: method | function
        '''
        #construct variables
        index = None
        searchNode = None
        increment = 0
        parent = self.getNodeByName(parent)
        
        #check if where the object we're registering is 
        #before or after the given node
        if after:
            searchNode = after
            increment = 1
        elif before:
            searchNode = before
            increment = -1
        
        #set the index
        if parent:
            index = parent.childCount()
            #if there is a searchNode, place the object before or after
            #the given node.
            if searchNode:
                for node in parent.nodes():
                    if searchNode == node.name():
                        index = node.index() + increment
                        break

        if not inspect.ismethod (obj) and not inspect.isfunction (obj):
            # Check if object is a component
            if isinstance (obj, component.Component):
                node = self.addNode(obj, parent, index)
                node.initialize(**kwargs)
                self.components[name] = node
        elif inspect.ismethod(obj) or inspect.isfunction(obj):
            node = ml_node.MlNode(obj.__func__.__name__)
            self.addNode(node, parent, index)
            #node.setParent(parent)
            node.execute = obj

    def setup(self):
        '''
        Runs the setup rig for each component registered to the system
        '''
        if self.nodes():
            for node in self.nodes():
                if not isinstance(node, component.Component):
                    continue
                attrDict = dict()
                for attr in node.attributes():
                    attrDict[attr.name()] = attr.value()
                    
                node.initialize(**attrDict)
                node.runSetupRig()
                
    def run(self):
        '''
        build each individual component, or function in the order it was
        registered to the build
        '''

        #loops through components and runs their runRig function
        if self.nodes():
            for node in self.nodes():
                if not isinstance(node, component.Component):
                    continue
                node.runRig()
                if node.controls:
                    for ctrls in node.controls.values():
                        for ctrl in ctrls:
                            if ctrl not in self.controls:
                                self.controls.append(ctrl)
                            #end if
                        #end loop
                    #end loop
                    for jnt in node.skinClusterJnts:
                        if jnt not in self.skinClusterJoints:
                                self.skinClusterJoints.append(jnt)

    def newScene(self):
        '''
        creates a fresh scene to start building an asset
        '''
        cmds.file(new = True, force = True)

    def preBuild(self):
        '''
        sets up the hierachry
        '''
        #if there is no puppet node in the scene, we will run the setup first
        if not cmds.ls(type = "puppet"):
            self.setup()
            
        #create hierachy
        cmds.createNode('rig', n = self.rigGrp)
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
        build rig hierarchy and attach components
        '''
        #if there is no rig node in the scene, we will run the setup first
        if not cmds.ls(type = "rig"):
            self.preBuild()
            self.run()

        for node in self.nodes():
            if not isinstance(node, component.Component):
                    continue
                
            if not common.isValid(node.rigGrp):
                node.runRig()
                
            cmds.parent(node.controlsGrp, self._trsCtrl)
            cmds.parent(node.jointsGrp, self.jointsGrp)
            for attr in ['displayJnts', 'jointVis']:
                fullAttrPath  = '%s.%s' % (self.name(), attr)
                componentAttr = '%s.%s' % (node.rigGrp, attr)
                if cmds.objExists(componentAttr):
                    if not cmds.objExists(fullAttrPath):
                        attribute.copy(attr, node.rigGrp, self.name(), reverseConnect=False)
                    #end if
                    
                    connectedAttrs = attribute.getConnections(attr, node.rigGrp, incoming = False)
                    if connectedAttrs:
                        for connectedAttr in connectedAttrs:
                            cmds.disconnectAttr(componentAttr, connectedAttr)
                            attribute.connect(fullAttrPath, connectedAttr)
                        #end for
                    #end if
                #end if
            #end for
            cmds.delete(node.rigGrp)
        #end loop


    def postBuild(self):
        '''
        clean up rig asset
        
        .. todo: Finish complete cleanup of the rig
        '''
        #create nodes on the rigGrp node
        tagControlsAttr = control.tag_as_control(self.rigGrp)
        cmds.addAttr(self.rigGrp, ln = 'deform_joints', at = 'message')
        tagJointsAttr  = '%s.deform_joints' % self.rigGrp

        if self.controls:
            for ctrl in self.controls:
                print ctrl, tagControlsAttr.split('.')[1]
                attribute.connect(tagControlsAttr, '%s.%s' % (ctrl, tagControlsAttr.split('.')[1]))
            #end loop
        #end if

        if self.skinClusterJoints:
            for jnt in self.skinClusterJoints:
                if common.isValid(jnt):
                    cmds.addAttr(jnt, ln = 'deform_joints', at = 'message')
                    attribute.connect(tagJointsAttr, '%s.deform_joints' % jnt)
                #end if
            #end loop
        #end if

        #lock and hide attributes
        attribute.lockAndHide(['s', 'v'], [self._shotCtrl, self._trsCtrl])
        attribute.lockAndHide(['t', 'r', 's', 'v'], self.name())
        
        #clear selection
        cmds.select(cl = True)

    def _runFunction(self, name):
        '''
        Check to see if the given name is a key in self.functions ordereddict
        
        ..warning: This function should not be used outside of this class
                  unless it's a subclass
        
        :see: Rig.register() and Rig.__init__()
        
        :param name: Name of the key which the function was registered
        :type name: str
        
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
        
        :see: Rig.saveControls(controls, filePath)
        
        .. warning: This will put any control you try to export in the current 
                  directory of this file. It should be exporting to an asset directory
        
        .. todo: Find out where the controls will be saved.
        .. todo: Figure out how we will store the file path for an asset
        '''
        Rig.saveControls(Rig.getControls(self.name()),
                         filePath = os.path.join(os.path.dirname(__file__),
                                                 '%s.%s' % (self.name(),
                                                            common.CONTROL)))
