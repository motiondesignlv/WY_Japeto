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
import japeto.libs.common as common
import japeto.libs.attribute as attribute
import japeto.libs.control as control
import japeto.libs.ordereddict as ordereddict

#import components
import japeto.components.component as component
import japeto.components.finger as finger

class Hand(component.Component):
    def __init__(self, name):
        super(Hand, self).__init__(name)

        #create controls
        self.__handCtrl = '%s_hand_%s' % (self._getSide(), common.CONTROL)
        self.__fingers = ordereddict.OrderedDict()
        self.__handPosition = list()

    @component.overloadArguments
    def initialize(self, **kwargs):
        super(Hand,self).initialize(**kwargs)

        self.addArgument('fingers', ['thumb', 'index', 'middle', 'ring', 'pinky'])
        self.addArgument('numJoints', 4)

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

        return self.__handPosition

    def setupRig(self):
        super(Hand, self).setupRig()

        if self._getSide() == common.LEFT:
        #move master  guide into position
            cmds.xform(common.getParent(self.masterGuide), ws = True, t = self.handPosition)

            for i,obj in enumerate(self.fingers):
                self.__fingers[obj] = finger.Finger('%s_%s' % (self._getSide(), obj))
                self.__fingers[obj].initialize(numJoints = self.numJoints, position = [self.position[0] + 10, self.position[1], (self.position[2] + 2 )- i], parent = self.parent)
                self.__fingers[obj].setupRig()

                cmds.parentConstraint(self.masterGuide, common.getParent(self.__fingers[obj].masterGuide), mo = True)
                for guide in self.__fingers[obj].getGuides():
                    #tag the guide control with a tag_guides attribute
                    tagAttr = attribute.addAttr(guide, 'hand_guides', attrType = 'message')
                    attribute.connect('%s.tag_guides' % self.setupRigGrp, tagAttr)
                #end loop
            #end loop
        #end if

        elif self._getSide() == common.RIGHT:
        #move master  guide into position
            cmds.xform(common.getParent(self.masterGuide), ws = True, t = self.handPosition)

            for i,obj in enumerate(self.fingers):
                self.__fingers[obj] = finger.Finger('%s_%s' % (self._getSide(), obj))
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

    def postSetupRig(self):
        super(Hand, self).postSetupRig()

        #TODO: Place build code for fingers here
        for obj in self.fingers:
            self.__fingers[obj].postSetupRig()

    def rig(self):
        super(Hand, self).rig()

        #TODO: Put build code here
        control.create(self.name, type = 'implicitSphere',
                       parent = self.controlsGrp,
                       color = common.SIDE_COLOR[self._getSide()])
        
        for i in range(len(common.getShapes(self.handCtrl))):
            control.scaleShape (self.handCtrl,scale = [.3,.3,.3],index = i)
        #end loop
        handCtrlZero = common.getParent(self.handCtrl)
        cmds.xform(handCtrlZero, ws = True, t = self.handPosition)
        cmds.xform(handCtrlZero, r = True, t = [0,1,0])

        #TODO: Place build code for fingers here
        for obj in self.fingers:
            self.__fingers[obj].rig()


    def postRig(self):
        super(Hand, self).postRig()


        #TODO: Place build code for fingers here
        for obj in self.fingers:
            self.__fingers[obj].postRig()
            self.skinClusterJnts.extend(self.__fingers[obj].skinClusterJnts)
            #assign hooks
            self.hookRoot.extend(self.__fingers[obj].hookRoot)

        self.hookRoot.append(common.getParent(self.__handCtrl))
        attribute.lockAndHide(['t', 'r', 's', 'v'], self.__handCtrl)
        
        
        