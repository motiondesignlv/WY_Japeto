'''
This is the Hand component 

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    July 2013
'''
#import maya modules------
import maya.cmds as cmds

#import package modules------
#import libs
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import control
from japeto.libs import ordereddict
from japeto.libs import joint
from japeto.libs import transform

#import components
from japeto.components import component
from japeto.components import finger

class Hand(component.Component):
    def __init__(self, name):
        super(Hand, self).__init__(name)
        self.__fingers = ordereddict.OrderedDict()
        self.__handPosition = list()

    @component.overloadArguments
    def initialize(self, **kwargs):
        super(Hand,self).initialize(**kwargs)

        #create controls
        self.__handCtrl = '%s_hand_%s' % (self._getPrefix(), common.CONTROL)
        self.handJoint  = '%s_hand_%s' % (self._getPrefix(), common.JOINT)

        self.addArgument('fingers', ['thumb', 'index', 'middle', 'ring', 'pinky'], 1)
        self.addArgument('numJoints', 4, 2)

    #getters
    @property
    def getFingers(self):
        return self.__fingers

    @property
    def handCtrl(self):
        return self.__handCtrl

    @property
    def handPosition(self):
        #get hand control position
        if self._getSide() == common.LEFT:
            self.__handPosition = \
                    [self.position[0] + 8, self.position[1], self.position[2]]
        elif self._getSide() == common.RIGHT:
            self.__handPosition = \
                    [self.position[0] - 8, self.position[1], self.position[2]]
        else:
            self.__handPosition = \
                    [self.position[0], self.position[1], self.position[2]]

        return self.__handPosition

    def setupRig(self):
        if super(Hand, self).setupRig():
            return True
        

        if self._getSide() == common.LEFT:
        #move master  guide into position
            cmds.xform(common.getParent(self.masterGuide), ws = True,
                       t = self.handPosition)

            for i,obj in enumerate(self.fingers):
                self.__fingers[obj] = finger.Finger('%s_%s' % (self._getPrefix(),
                                                               obj))
                self.__fingers[obj].initialize(numJoints = self.numJoints,
                                               position=[self.position[0] + 10,
                                                 self.position[1],
                                                 (self.position[2] + 2 )- i],
                                               parent = self.parent)
                self.__fingers[obj].setupRig()

                cmds.parentConstraint(self.masterGuide,
                            common.getParent(self.__fingers[obj].masterGuide),
                            mo = True)
                for guide in self.__fingers[obj].getGuides():
                    #tag the guide control with a tag_guides attribute
                    tagAttr = attribute.addAttr(guide, 'hand_guides',
                                                attrType = 'message')
                    attribute.connect('%s.tag_guides' % self.setupRigGrp,
                                      tagAttr)
                #end loop
            #end loop
        #end if

        elif self._getSide() == common.RIGHT:
        #move master  guide into position
            cmds.xform(common.getParent(self.masterGuide), ws = True, t = self.handPosition)

            for i,obj in enumerate(self.fingers):
                self.__fingers[obj] = finger.Finger('%s_%s' % (self._getPrefix(), obj))
                self.__fingers[obj].initialize(numJoints = self.numJoints, position = [self.position[0] - 10, self.position[1], (self.position[2] + 2 ) - i], parent = self.parent)
                self.__fingers[obj].setupRig()
            
                cmds.parentConstraint(self.masterGuide, common.getParent(self.__fingers[obj].masterGuide), mo = True)
        
                for guide in self.__fingers[obj].getGuides():
                    #tag the guide control with a tag_guides attribute
                    tagAttr = attribute.addAttr(guide, 'hand_guides', attrType = 'message')
                    attribute.connect('%s.tag_guides' % self.setupRigGrp, tagAttr)
                #end loop
            #end loop
        #end elif
        
        #create joint and guide
        joint.create(self.handJoint, self.skeletonGrp, self.handPosition)
        self.handGuide = self.setupCtrl(self.handJoint.replace(common.JOINT,
                                                               common.CONTROL),
                                        self.handJoint,
                                        common.SIDE_COLOR[self._getSide()])

    def postSetupRig(self):
        if super(Hand, self).postSetupRig():
            return True

        #TODO: Place build code for fingers here
        for obj in self.fingers:
            self.__fingers[obj].postSetupRig()

    def rig(self):
        if not self._puppetNode:
            self.runSetupRig()
        #TODO: Place build code for fingers here
        for obj in self.fingers:
            self.__fingers[obj].rig()
        
        if super(Hand, self).rig():
            return True
        
        #TODO: Put build code here
        control.create(self.handCtrl.replace('_%s' % common.CONTROL, ''),
                       type = 'implicitSphere',
                       parent = self.controlsGrp,
                       color = common.SIDE_COLOR[self._getSide()])
        
        for i in range(len(common.getShapes(self.handCtrl))):
            control.scaleShape (self.handCtrl,scale = [.3,.3,.3],index = i)
        #end loop
        handCtrlZero = common.getParent(self.handCtrl)
        transform.matchXform(self.handJoint,handCtrlZero, 'pose')
        #cmds.xform(handCtrlZero, ws = True, t = self.handPosition)
        cmds.xform(handCtrlZero, ws = True, r = True, t = [0,1,0])

        


    def postRig(self):
        if super(Hand, self).postRig():
            return True

        #TODO: Place build code for fingers here
        for obj in self.fingers:
            self.__fingers[obj].postRig()
            self.skinClusterJnts.extend(self.__fingers[obj].skinClusterJnts)
            #assign hooks
            self.hookRoot.extend(self.__fingers[obj].hookRoot)

        cmds.delete(self.handJoint)

        self.hookRoot.append(common.getParent(self.__handCtrl))
        attribute.lockAndHide(['t', 'r', 's', 'v'], self.__handCtrl)

        
        
        