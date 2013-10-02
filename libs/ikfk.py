'''
This is the common module for all the ikfk utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#import maya modules
from maya import cmds
from maya import OpenMaya

#import package modules
import japeto
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import transform 
from japeto.libs import ordereddict
from japeto.libs import curve
from japeto.libs import surface
from japeto.libs import joint
from japeto.libs import fileIO

#load plugins
fileIO.loadPlugin('%sdecomposeRotation.py' % japeto.PLUGINDIR)

#------------------------------------------------------------
#                      IK/FK Base CLASS
#------------------------------------------------------------
class IkFk(object):
    @classmethod
    def createIkHandle(cls,startJoint, endJoint, type = 'ikRPsolver', name = None, parent = None, crv = None):
        '''
        Example:
        ..python
        createIkHandle("l_upArm_ik_jnt", "l_wrist_ik_jnt", name = "l_arm_ik_hdl", parent = "ikfk_grp")
        #Return: ["l_arm_ik_hdl
        
        @param startJoint: first joint in the chain for the ikHandle to effect
        @type startJoint: *str*
        
        @param endJoint: last joint in the chain for the ikHandle to effect
        @type endJoint: *str*
        
        @param type: The type of ikHandle used on creation
        @type type: *str*
        :options: 'ikRPsolver', ikSCSolver
        
        @param name: Name given to the ikHandle
        @type name: *str*
        
        @param parent: Parent object for the ikHandle
        @type parent: *str*
        
        @return ikHandle: Name of the ikHandle
        @rtype ikHandle: *str*
        
        @return effector: Name of the effector of the ikHandle
        @rtype effector: *str*
        
        '''
        if not name:
            name = common.IKHANDLE
            
        if type == 'ikSplineSolver':
            if crv:
                ikHandle = cmds.ikHandle(n = name, sj = startJoint, ee = endJoint, c = crv, sol = type, ccv = False, roc = True, pcv = True)
            else:
                ikHandle = cmds.ikHandle(n = name, sj = startJoint, ee = endJoint, sol = type, ccv = True, roc = True, pcv = True)
        else:
            ikHandle = cmds.ikHandle(n = name, sj = startJoint, ee = endJoint, sol = type)

        effector = ikHandle[1]
        ikHandle = ikHandle[0]
        
        if parent:
            cmds.parent(ikHandle, parent)
            
        return ikHandle, effector
    
    
    
    def __init__(self, startJoint, endJoint, name = str(), parent = str()):
        super(IkFk, self).__init__()
        
        #private 
        self.__startJoint = startJoint
        self.__endJoint   = endJoint
        self.__parent     = parent
        self.__name       = name
        self.__group      = '%s%s' % (common.IK, common.FK)
        self._aimAxis     = str()
        self.upAxis       = str()
        
        #public 
        self.originalJoints = self.__getJointChain()
        self.ikJoints     = list()
        self.fkJoints     = list()
        self.blendJoints  = list()
    
    #GETTERS
    @property
    def name(self):
        return self.__name
    
    @property
    def group(self):
        return self.__group
    
    @property
    def aimAxis(self):
        if not self._aimAxis:
            if cmds.objExists(self.__startJoint):
                self._aimAxis = transform.getAimAxis(self.__startJoint)
        
        return self._aimAxis
    
    
    #SETTERS
    @group.setter
    def group(self, value):
        if cmds.objExists(self.__group):
            cmds.rename(self.__group, value)
            
        self.__group = value
    
    def __getJointChain(self):
        '''
        This returns all the joints in the chain 
        '''
        origJnts = list()
        
        #getting all joints inbetween start and end joint
        inbetweeenJnts = common.getInbetweenNodes(self.__startJoint, self.__endJoint, list())
        
        #declare origJnts as inbetweeenJnts
        origJnts = inbetweeenJnts
            
        #inserting start and end
        origJnts.insert(0, self.__startJoint)
        origJnts.insert(len(origJnts), self.__endJoint)
        
        #declaring class attribute list of original joints
        return tuple(origJnts)
    
    

    def create(self, searchReplace = str()):
        #check group attribute
        if self.name:
            self.group = ('%s_%s' % (self.name, self.group))
            
        #create ik/fk group node and add attribute
        cmds.createNode('transform', n = self.group)
        attribute.addAttr(self.group, attr = 'ikfk', attrType = 'enum', defValue = ['off','on'],value = 0)
        #cmds.addAttr(self.group, ln = 'ikfk', at = 'double', min = 0, max = 1, dv = 0, keyable = True)
        
        #check parent attribute
        if self.__parent:
            cmds.parent(self.group, self.__parent)
        #end if
        elif common.getParent(self.group):
            cmds.parent(self.group, w = True)
        #end elif
        
        #create IK joints
        parent = self.group
        for jnt in self.originalJoints:
            if searchReplace:
                ikJnt = common.duplicate(jnt, jnt.replace(searchReplace, 'ik'), parent = parent)
            else:
                ikJnt = common.duplicate(jnt, '%s_ik' % jnt, parent = parent)
            #end if/else
            
            #set joint colors
            cmds.setAttr('%s.overrideEnabled' % ikJnt, 1)
            cmds.setAttr('%s.overrideColor' % ikJnt, 6)
            
            #re-connect the inverse scale
            if self.ikJoints:
                if not attribute.isConnected('inverseScale', ikJnt, True, False):
                    attribute.connect('%s.scale' % parent, '%s.inverseScale' % ikJnt)
            
            self.ikJoints.append(ikJnt)
            parent = ikJnt
        #end loop
            
        #create FK joints
        parent = self.group        
        for jnt in self.originalJoints:
            if searchReplace:
                fkJnt = common.duplicate(jnt, jnt.replace(searchReplace, 'fk'), parent = parent)
            else:
                fkJnt = common.duplicate(jnt, '%s_fk' % jnt, parent = parent)
            #end if/else
            
            #set joint colors
            cmds.setAttr('%s.overrideEnabled' % fkJnt, 1)
            cmds.setAttr('%s.overrideColor' % fkJnt, 13)
            
            if self.fkJoints:
                if not attribute.isConnected('inverseScale', fkJnt, True, False):
                    attribute.connect('%s.scale' % parent, '%s.inverseScale' % fkJnt)
            
            self.fkJoints.append(fkJnt)
            parent = fkJnt
        #end loop
            
        
        #create Blend joints
        parent = self.group
        for i,jnt in enumerate(self.originalJoints):
            if searchReplace:
                blendJnt = common.duplicate(jnt, jnt.replace(searchReplace, 'blend'), parent = parent)
            else:
                blendJnt = common.duplicate(jnt, '%s_blend' % jnt, parent = parent)
            
            #set joint colors
            cmds.setAttr('%s.overrideEnabled' % blendJnt, 1)
            cmds.setAttr('%s.overrideColor' % blendJnt, 14)
            #create and connect blend translate
            blendNode_trans = cmds.createNode('blendColors', n = '%s_trans_bcn' % blendJnt)	    
            cmds.connectAttr('%s.translate' % self.ikJoints[i], '%s.color2' % blendNode_trans, f = True)
            cmds.connectAttr('%s.translate' % self.fkJoints[i], '%s.color1' % blendNode_trans, f = True)
            cmds.connectAttr('%s.output' % blendNode_trans, '%s.translate' % blendJnt, f = True)
            #connect to group node
            cmds.connectAttr('%s.ikfk' % self.group, '%s.blender' % blendNode_trans, f = True)
            
            #create and connect blend translate
            blendNode_rot = cmds.createNode('blendColors', n = '%s_rot_bcn' % blendJnt)
            cmds.connectAttr('%s.rotate' % self.ikJoints[i], '%s.color2' % blendNode_rot, f = True)
            cmds.connectAttr('%s.rotate' % self.fkJoints[i], '%s.color1' % blendNode_rot, f = True)
            cmds.connectAttr('%s.output' % blendNode_rot, '%s.rotate' % blendJnt, f = True)
            #connect to group node
            cmds.connectAttr('%s.ikfk' % self.group, '%s.blender' % blendNode_rot, f = True)
            
            if self.blendJoints:
                if not attribute.isConnected('inverseScale', blendJnt, True, False):
                    attribute.connect('%s.scale' % parent, '%s.inverseScale' % blendJnt)
            
            #add blendJoints to list
            self.blendJoints.append(blendJnt)
            
            #constrain original joints to blend joints
            cmds.parentConstraint(blendJnt, self.originalJoints[i],)
            
            parent = blendJnt
        #end loop
        
    def delete(self):
        cmds.delete(self.group)

#------------------------------------------------------------
#                      IK/FK LIMB CLASS
#------------------------------------------------------------

class IkFkLimb(IkFk):
    @classmethod
    def getPoleVectorPosition(cls,joints = None):
        '''
        This function will return the point in space where the poleVector position should be
        
        @param joints: The three joints you want to get the poleVector position for
        @type joints: *list* or *tuple* 
        
        @return: poleVector position
        @rtype: *tuple*
        '''
        if not joints:
            try:
                joints = cmds.ls(sl =True)
            except:
                raise RuntimeError('Nothing selected')
        #end if        
        if not isinstance(joints, list) and not isinstance(joints, tuple):
            raise RuntimeError('%s must be a list or tuple of 3 joints' % joints)
        #end if
        if len(joints) != 3:
            raise RuntimeError('%s must have 3 joints in the list' % joints)
        #end if
        for jnt in joints:
            if cmds.nodeType(jnt) != 'joint':
                raise TypeError('%s must be a joint' % jnt)
            #end if
        #end loop
        #store the joints in variables
        startJnt  = joints[0]
        middleJnt = joints[1]
        endJnt    = joints[2]
        
        #get joint position in world space
        startPoint  = cmds.xform(startJnt, q = True, ws = True, t = True)
        startVector = OpenMaya.MVector(*startPoint)
        middlePoint = cmds.xform(middleJnt, q = True, ws = True, t = True)
        middleVector = OpenMaya.MVector(*middlePoint)
        endPoint  = cmds.xform(endJnt, q = True, ws = True, t = True)
        endVector = OpenMaya.MVector(*endPoint)
        
        #get the mid way point between start and end joint
        midVector = (startVector + endVector) / 2
        
        #get the difference between the elbowVector and the midVector
        pvOrigin  = middleVector - midVector
        
        #extend the pvOrigin to give it some space from the elbow
        pvExtend  = pvOrigin * 2
        
        #put the pvExtend back at midVector to get pvVector
        pvVector   = midVector + pvExtend
        #return the pvPosition
        return (pvVector.x, pvVector.y, pvVector.z)
    
    @classmethod
    def createStretchIK(cls,ikHandle, grp):
        '''
        creates a stretchy joint chain based off of influences on ikHandle
        
        Example:
    
        ..python:
            createStrecthIK('l_leg_ik_hdl')
            #Return: 
    
        @param ikHandle: ik handle you influencing joint chain you want to stretch
        @type ikHandle: *str*
        
        :retrun targetJnts: Joints that are used to calculate the distance
        @rtype: *list*
        '''
        if not grp or not common.isValid(grp):
            grp = cmds.createNode('transform', n = 'ik_stretch_grp')
    
        #create attributes on grp node
        stretchAttr  = attribute.addAttr(grp, 'stretch', defValue = 1, min = 0, max = 1)
        stretchTopAttr = attribute.addAttr(grp, 'stretchTop', defValue = 1)
        stretchBottomAttr = attribute.addAttr(grp, 'stretchBottom', defValue = 1)
        
        #get joints influenced by the ikHandle
        jnts = cmds.ikHandle(ikHandle, q = True, jl = True)
        jnts.append(common.getChildren(jnts[-1])[0])
        #create tgt joints for distance node
        targetJnt1 = cmds.createNode('joint', n = '%s_%s' % (jnts[0], common.TARGET))
        targetJnt2 = cmds.createNode('joint', n = '%s_%s' % (jnts[2], common.TARGET))
        transform.matchXform(jnts[0], targetJnt1, 'position')
        transform.matchXform(jnts[2], targetJnt2, 'position')
        
        #create distance and matrix nodes
        distanceBetween = cmds.createNode('distanceBetween', n = '%s_%s' % (ikHandle, common.DISTANCEBETWEEN))
        startDecomposeMatrix = cmds.createNode('decomposeMatrix', n = '%s_%s' % (targetJnt1, common.DECOMPOSEMATRIX))
        endDecomposeMatrix = cmds.createNode('decomposeMatrix', n = '%s_%s' % (targetJnt2, common.DECOMPOSEMATRIX))
        
        #create condition and multplyDivide nodes
        multiplyDivide = cmds.createNode('multiplyDivide', n = '%s_%s' % (ikHandle, common.MULTIPLYDIVIDE))
        condition = cmds.createNode('condition', n = '%s_%s' % (ikHandle, common.CONDITION))
        multiplyDivideJnt1 = cmds.createNode('multiplyDivide', n = '%s_%s' % (jnts[1], common.MULTIPLYDIVIDE))
        
        blendColorStretch = cmds.createNode('blendColors', n = '%s_stretch_%s' % (grp, common.BLEND))
        multiplyStretch = cmds.createNode('multiplyDivide', n = '%s_stretch_%s' % (grp, common.MULTIPLYDIVIDE))
        plusMinusStretch = cmds.createNode('plusMinusAverage', n = '%s_stretch_%s' % (grp, common.PLUSMINUSAVERAGE))
        
        #connect matrix nodes to distance between node
        cmds.connectAttr('%s.worldMatrix[0]' % targetJnt1, '%s.inputMatrix' % startDecomposeMatrix, f = True)
        cmds.connectAttr('%s.worldMatrix[0]' % targetJnt2, '%s.inputMatrix' % endDecomposeMatrix, f = True)
        cmds.connectAttr('%s.outputTranslate' % startDecomposeMatrix, '%s.point1' % distanceBetween, f = True)
        cmds.connectAttr('%s.outputTranslate' % endDecomposeMatrix, '%s.point2' % distanceBetween, f = True)
        
        #connect multiplyDivide and condition nodes
        aimAxis = transform.getAimAxis(jnts[1], False)
        jnt1Distance = attribute.getValue('%s.t%s' % (jnts[1], aimAxis))
        jnt2Distance = attribute.getValue('%s.t%s' % (jnts[2], aimAxis))
        jntLength = jnt1Distance + jnt2Distance
        cmds.setAttr('%s.operation' % multiplyDivide, 2)    
        if jntLength < 0:
            negDistanceMultiply = cmds.createNode('multiplyDivide', n = '%s_distanceNeg_%s' % (grp, common.MULTIPLYDIVIDE))
            cmds.connectAttr('%s.distance' % distanceBetween, '%s.input1X' % negDistanceMultiply, f = True)
            cmds.setAttr('%s.input2X' % negDistanceMultiply, -1)
            cmds.connectAttr('%s.outputX' % negDistanceMultiply, '%s.input1X' % multiplyDivide, f = True)
            cmds.connectAttr('%s.outputX' % negDistanceMultiply, '%s.firstTerm' % condition, f = True)
            cmds.setAttr('%s.operation' % condition, 4)
        else:
            cmds.connectAttr('%s.distance' % distanceBetween, '%s.input1X' % multiplyDivide, f = True)
            cmds.connectAttr('%s.distance' % distanceBetween, '%s.firstTerm' % condition, f = True)
            cmds.setAttr('%s.operation' % condition, 2)
    
        cmds.connectAttr('%s.outputX' % multiplyDivide, '%s.input1X' % multiplyDivideJnt1, f = True)
        cmds.connectAttr('%s.outputX' % multiplyDivide, '%s.input1Y' % multiplyDivideJnt1, f = True)
        cmds.connectAttr('%s.outputX' % multiplyDivideJnt1, '%s.colorIfTrueR' % condition, f = True)
        cmds.connectAttr('%s.outputY' % multiplyDivideJnt1, '%s.colorIfTrueG' % condition, f = True)
        cmds.connectAttr('%s.outColorR' % condition, '%s.t%s' % (jnts[1], aimAxis), f = True)
        cmds.connectAttr('%s.outColorG' % condition, '%s.t%s' % (jnts[2], aimAxis), f = True)
    
        attribute.connect(stretchAttr, '%s.blender' % blendColorStretch)
        attribute.connect(stretchTopAttr, '%s.input1X' % multiplyStretch)
        cmds.setAttr('%s.input2X' % multiplyStretch, jnt1Distance)
        attribute.connect(stretchBottomAttr, '%s.input1Y' % multiplyStretch)
        cmds.setAttr('%s.input2Y' % multiplyStretch, jnt2Distance)
        attribute.connect('%s.outputX' % multiplyStretch, '%s.input2D[0].input2Dx' % plusMinusStretch)
        attribute.connect('%s.outputY' % multiplyStretch, '%s.input2D[1].input2Dx' % plusMinusStretch)
        attribute.connect('%s.output2Dx' % plusMinusStretch, '%s.input2X' % multiplyDivide)
        attribute.connect('%s.output2Dx' % plusMinusStretch, '%s.secondTerm' % condition)
        attribute.connect('%s.outputX' % multiplyStretch, '%s.colorIfFalseR' % condition)
        attribute.connect('%s.outputY' % multiplyStretch, '%s.colorIfFalseG' % condition)
        attribute.connect('%s.outputX' % multiplyStretch, '%s.input2X' % multiplyDivideJnt1)
        attribute.connect('%s.outputY' % multiplyStretch, '%s.input2Y' % multiplyDivideJnt1)
        
        attribute.connect('%s.outColorR' % condition, '%s.color1R' % blendColorStretch)
        attribute.connect('%s.outputX' % multiplyStretch, '%s.color2R' % blendColorStretch)
        attribute.connect('%s.outColorG' % condition, '%s.color1G' % blendColorStretch)
        attribute.connect('%s.outputY' % multiplyStretch, '%s.color2G' % blendColorStretch)
        
        attribute.connect('%s.outputR' % blendColorStretch, '%s.t%s' % (jnts[1], aimAxis))
        attribute.connect('%s.outputG' % blendColorStretch, '%s.t%s' % (jnts[2], aimAxis))
        
        #parent ikHandle under targetJnt2
        cmds.parent(ikHandle, targetJnt2)
        
        #turn off visibility of targetJnts and parent under grp node
        for jnt in [targetJnt1, targetJnt2]:
            cmds.setAttr('%s.v' % jnt, 0)
            cmds.parent(jnt, grp)
    
        return [targetJnt1, targetJnt2]
    
    @classmethod
    def ikMatchFk(cls, fkJoints, ikDriver, pvDriver):
        newPvPos = IkFkLimb.getPoleVectorPosition(fkJoints)
        endJntPos = cmds.xform(fkJoints[2], q = True, ws = True, t = True)
        endJntRot = cmds.xform(fkJoints[2], q = True, ws = True, ro = True)
        
        cmds.xform(pvDriver, ws = True, t = newPvPos)
        cmds.xform(ikDriver, ws = True, t = endJntPos)
        #cmds.xform(ikDriver, ws = True, ro = endJntRot)
        
    @classmethod
    def fkMatchIk(cls, joints, ikJoints):
        if not joints:
            try:
                joints = cmds.ls(sl =True)
            except:
                raise RuntimeError('Nothing selected')
        #end if        
        if not isinstance(joints, list) and not isinstance(joints, tuple):
            raise RuntimeError('%s must be a list or tuple of 3 joints' % joints)
        #end if
        if len(joints) != 3:
            raise RuntimeError('%s must have 3 joints in the list' % joints)
        #end if
        for jnt in joints:
            if cmds.nodeType(jnt) != 'joint':
                raise TypeError('%s must be a joint' % jnt)
            
        for jnt, ikJnt in zip(joints, ikJoints):
            trs = cmds.xform(ikJnt, q = True, ws = True, t = True)
            rot = cmds.xform(ikJnt, q = True, ws = True, ro = True)
            
            cmds.xform(jnt, ws = True, t = trs)
            cmds.xform(jnt, ws = True, ro = rot)
        
        
        
    def __init__(self, *args, **kwargs):
        super(IkFkLimb, self).__init__(*args,**kwargs)
    
        #class variables
        self.__ikHandle = '%s_%s' % (common.IK, common.HANDLE)
        self.stretchTargets = list()
        
        
    #---------------------
    #Getters
    #---------------------
    @property    
    def ikHandle(self):
        return self.__ikHandle
        
    def create(self, stretch = False, **kwargs):
        super(IkFkLimb, self).create(**kwargs)
        
        IkFk.createIkHandle(self.ikJoints[0], self.ikJoints[2], name = self.__ikHandle, parent = self.group)
        cmds.setAttr('%s.v' % self.__ikHandle, 0)
        ikDriver = self.__ikHandle
        
        if stretch:
            #ik stretch setup
            self.stretchTargets  = IkFkLimb.createStretchIK(self.__ikHandle, self.group)
            ikDriver = self.stretchTargets[1]
        
        #add message attributes for ik and fk switching
        fkStartAttr = attribute.addAttr(self.group, 'fkStartJnt', attrType = 'message')
        attribute.connect('%s.message' % self.fkJoints[0],fkStartAttr)
        
        fkMiddleAttr = attribute.addAttr(self.group, 'fkMiddleJnt', attrType = 'message')
        attribute.connect('%s.message' % self.fkJoints[1],fkMiddleAttr)
        
        fkEndAttr = attribute.addAttr(self.group, 'fkEndJnt', attrType = 'message')
        attribute.connect('%s.message' % self.fkJoints[2],fkEndAttr)
        
        ikDrvAttr = attribute.addAttr(self.group, 'ikDriver', attrType = 'message')
        attribute.connect('%s.message' % ikDriver,ikDrvAttr)
        
        ikPvAttr = attribute.addAttr(self.group, 'ikDriver', attrType = 'message')
        #attribute.connect('%s.message' % ikDriver, ikPvAttr)


#------------------------------------------------------------
#                      IK/FK FOOT CLASS
#------------------------------------------------------------
class IkFkFoot(IkFk):
    def __init__(self, startJoint, endJoint, name = str(), parent = str()):
        super(IkFkFoot, self).__init__(startJoint, endJoint, name, parent)
        
        #class variables
        self.__footRollGrpDict = ordereddict.OrderedDict()
        self.__ankleDriver = str()
        self.__ikHandles = list()
        
    #GETTERS
    def getFootRolls(self):
        '''
        Returns foot roll groups in a dictionary
        '''
        return self.__footRollGrpDict
    
    def getAnkleDriver(self):
        '''
    	Returns node that is driving the ankle
    	'''
        return self.__ankleDriverNode
    
    def getIkHandles(self):
        return self.__ikHandles
    
    #BUILD FUNCTIONS
    def create(self, searchReplace = str(), footRollGrpList = list()):
        super(IkFkFoot, self).create(searchReplace)
        
        if not footRollGrpList:
            #list the groups for the foot ik setup
            footRollGrpList = ['bankIn','bankOut','heelPivot', 'heelRoll', 'toePivot', 'toeRoll','ballRoll', 'toeBend']
        
        #create ankle driver
        self.__ankleDriver = self.__createAnkleDriver()
        
        #create ik handles for the ik setup
        for i in range(len(self.ikJoints) - 1):
            ikHdl= createIkHandle(self.ikJoints[i], self.ikJoints[i+1],
                                  type = 'ikSCsolver',
                                  name = common.searchReplaceRename(self.ikJoints[i+1],
                                                      '_%s' % common.JOINT,
                                                      '_%s' % common.HANDLE),
                                  parent = self.group)[0]
            #append ik handle to ikHandles list
            self.__ikHandles.append(ikHdl)
        #end loop
        
        #add foot rolls attribute on ik/fk group node
        footRollAttr = attribute.addAttr(self.group, 'footRolls', attrType = 'message')
        
        #create foot roll groups
        parent = self.group
        for grp in footRollGrpList:
            #store each group in the footRollDict
            self.__footRollGrpDict[grp] = cmds.createNode('transform', n = '%s_%s' % (self.name, grp))
            grpFootRollAttr = attribute.addAttr(self.__footRollGrpDict[grp] , 'footRolls', attrType = 'message')
            #connect foot roll attr on ik/fk group to message attribute
            attribute.connect(footRollAttr, grpFootRollAttr)
            #parent grp to parent
            cmds.parent(self.__footRollGrpDict[grp], parent)
            
            if grp == footRollGrpList[-2]:
                cmds.parent(self.__ikHandles[:2], self.__footRollGrpDict[grp])
                continue
            elif grp == footRollGrpList[-1]:
                cmds.parent(self.__ikHandles[-1], self.__footRollGrpDict[grp])
            
            parent = self.__footRollGrpDict[grp]


    def __createAnkleDriver(self):
        '''
        Check for ankle driver, if there is none, then this creates one
        '''
        ikJntConnections = cmds.listConnections('%s.tx' % self.ikJoints[0])
        
        if ikJntConnections:
            for node in ikJntConnections:
                if cmds.nodeType(node) == 'ikEffector':
                    ankleDriver = cmds.listConnections('%s.handlePath[0]' % node)[0]
                #end if
            #end loop
        #end if
        else:
            #get position of ankle node
            position = cmds.xform(self.ikJoints[0], q = True, ws = True, t = True)
            
            #create ankle driver node and position it at ankle joint
            ankleDriver = cmds.createNode('transform', n = '%s_driver' % self.ikJoints[0])
            cmds.xform(ankleDriver, ws = True, t = position)
            cmds.parent(ankleDriver, self.group)
            
            cmds.parentConstraint(ankleDriver, self.ikJoints[0], mo = True)
        #end else
        
        self.__ikHandles.insert(0, ankleDriver)
        return ankleDriver

#------------------------------------------------------------
#                      IK/FK SPLINE CLASS 
#                        (not finished)
#------------------------------------------------------------
class IkFkSpline(IkFk):
    @classmethod
    def addParametricStretch(cls, crv, scaleCompensate=None, scaleAxis='x', uniform=False, useTranslationStretch=False):
        '''
        Add parametric based stretching to a splineIK chain. This uses U sampling of a curve to determine the distance the curve is stretching at
        the given joints. This allows for a non-uniform scaling to be achieved (joints near where the curve is stretching will scale more). This
        will also prevent overshooting of the joints while the curve stretches. You may hook any curve up to this as long as the curve is feeding
        a splineIK handle (which it uses to find the attached joints).
        
        .. todo:: add maintainVolume option
        
        @param curve: the name of the curve transform (or shape) you want to use - This curve must be connected to a splineIK. This can be a live rebuild
        @type curve: str
        @param scaleCompensate: a node to use as the base character scale reference to ensure character scaling is taken into account
        @type scaleCompensate: str
        @param scaleAxis: the axis to scale (or translate) along for stretching
        @type scaleAxis: str (x, y, z)
        @param uniform: whether to use uniform stretching (default is false which means joints most affected by curve distortion will stretch more)
                        This will cause a live uniform rebuild of your source curve to connect it to the splineIK.
                        The uniform rebuild will have the same number of cvs as the source and will be the same degree curve. If you want more control
                        you can always create the live rebuild first, connect it to the splineIK.geometry input and then run this on the rebuild curve
        @type uniform: bool
        @param useTranslationStretch: whether to translate the joints rather than scale (be aware this may cause the joints to overshoot the curve.)
        @type useTranslationStretch: bool
        
        '''
        # arg validation
        curveShape = None
        if cmds.nodeType(crv) == 'nurbsCurve':
            curveShape = crv
            crv = cmds.listRelatives(curveShape, p=True)[0]
            
        elif cmds.nodeType(crv) == 'transform':
            curveShape = cmds.listRelatives(crv, shapes=True)[0] or None
            
        if not curveShape or cmds.nodeType(curveShape) != "nurbsCurve":
            raise Exception('You must provide a valid nurbsCurve shape or transform to addParametricStretch')
        
        # get the joints for the curve
        handle = cmds.listConnections(curveShape, d=True, type='ikHandle')[0] or None
        if not handle:
            raise Exception('The curve provided does not appear to be part of an IkHandle')
            
        # get the joints
        joints = IkFkSpline._getIkJoints(handle)
            
        # handle the rebuild if uniform was specified
        if uniform:
            degree = cmds.getAttr(curveShape + ".degree")
            origCurve = crv
            crv = cmds.rebuildCurve(crv, ch=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, d=degree, tol=.01)[0]
            crv = cmds.rename(crv, origCurve + "_rebuild")
            curveShape = cmds.listRelatives(crv, shapes=True)[0]
            cmds.connectAttr(curveShape + ".worldSpace[0]", handle + ".geometry", f=True)
            
        # determine their uv position first (before we move them)
        uValues = {}
        for joint in joints:
            # get the joint world position
            pos = cmds.xform(joint, q=True, ws=True, a=True, rp=True)
            
            # find the closest u position
            u = curve.getParamFromPosition(curveShape, pos)
            
            uValues[joint] = u
            
            
        # define the poc (pointOnCurveInfo) variable to hold the previous iterations poc node
        prevPoc = None
        
        # cycle over the joints
        for joint in reversed(joints):
            # create the nodes we need
            poc = cmds.createNode('pointOnCurveInfo', n=joint + "_stretch_poc")
            cmds.connectAttr('%s.worldSpace[0]' % curveShape, '%s.inputCurve' % poc)
            cmds.setAttr('%s.parameter' % poc, uValues[joint])
            
            # if this is not the first loop
            if prevPoc:
                # create the distance between node
                dist = cmds.createNode('distanceBetween', n= joint + "_stretch_dst")
                
                # handle scale compensation
                if scaleCompensate:
                    cmds.connectAttr('%s.worldInverseMatrix[0]' % scaleCompensate, '%s.inMatrix1' % dist)
                    cmds.connectAttr('%s.worldInverseMatrix[0]' % scaleCompensate, '%s.inMatrix2' % dist)
                
                # connect the previous poc and the new one to the distance
                cmds.connectAttr('%s.position' % prevPoc, '%s.point2' % dist)
                cmds.connectAttr('%s.position' % poc, '%s.point1' % dist)
                
                # if scale based stretching
                if not useTranslationStretch:
                    # create the multDoubleLinear node to normalize the default distance
                    mdl = cmds.createNode('multDoubleLinear', n=joint + "_stretch_mdl")
                    cmds.connectAttr('%s.distance' % dist, '%s.input1' % mdl)
                    curDist = cmds.getAttr('%s.distance' % dist)
                    curDist = curDist if curDist > .000001 else .000001
                    cmds.setAttr('%s.input2' % mdl, (1.00/curDist))
                    
                    # connect to the joint
                    cmds.connectAttr('%s.output' % mdl, '%s.s%s' % (joint, scaleAxis.lower()))
                    
                # if translation based stretching
                else:
                    cmds.connectAttr('%s.distance' % dist, '%s.t%s' % (joint, scaleAxis.lower()))
                    
                
            # update the previous poc node variable
            prevPoc = poc
            
            
                
        return joints
        
    @classmethod
    def _getIkJoints(cls, ikHandle):
        '''
        '''
        # find information from handle
        endEffector = cmds.listConnections(ikHandle + ".endEffector", s=True, d=False)[0]
        startJoint = cmds.listConnections(ikHandle + ".startJoint", s=True, d=False)[0]
        endJoint = cmds.listConnections(endEffector, s=True, d=False, type='joint')[0]
        
        return IkFkSpline._getContainedChain(startJoint, endJoint)
        
    @classmethod
    def _getContainedChain(cls,currentJoint, targetJoint, _joints=None):
        '''
        '''
        _joints = _joints[:] if _joints else []
        _joints.append(currentJoint)
        
        if currentJoint == targetJoint:
            return _joints
        
        for child in cmds.listRelatives(currentJoint, c=True, type='joint') or []:
            tmp = IkFkSpline._getContainedChain(child, targetJoint, _joints=_joints)
            if tmp:
                return tmp
            else:
                continue
                
        return None

    
    
    def __init__(self, *args, **kwargs):
        super(IkFkSpline,self).__init__(*args,**kwargs)
        pass
    
    def create(self, stretch = False):
        super(IkFkSpline, self).create()
        
        #create the curve for the ikSpline
        crv = curve.createFromTransforms(self.ikJoints, 
                                         degree = 3, 
                                         name = '%s_%s' % (self.name, 
                                                           common.CURVE)
                                         )
        cmds.parent(crv.fullPathName, self.group)
        
        IkFk.createIkHandle(self.ikJoints[0], 
                            self.ikJoints[-1],
                            type = 'ikSplineSolver',
                            name = '%s_%s' % (self.name, common.IKHANDLE),
                            parent = self.group,
                            crv = crv.fullPathName)
        
        aimAxis = transform.getAimAxis(self.ikJoints[0])
        
        if stretch:
            IkFkSpline.addParametricStretch(crv.fullPathName, 
                                            scaleCompensate = None, 
                                            scaleAxis = aimAxis, 
                                            uniform = False, 
                                            useTranslationStretch = True)
            
        
            
#------------------------------------------------------------
#                      IK/FK RIBBON CLASS 
#                (Only works for spine Right now)
#------------------------------------------------------------            
class IkFkRibbon(IkFk):
    def __init__(self, *args, **kwargs):
        super(IkFkRibbon, self).__init__(*args, **kwargs)
        self.surface      = str()
        self.follicles    = list()
        self.driverJoints = {'start':list(),'middle':list(),'end':list()}
        self.upJoint      = str()
        self.aimJoint     = str()
        self.targetJoints = list()
    
    def create(self, *args, **kwargs):
        super(IkFkRibbon, self).create(*args,**kwargs)
        #declare variables for function
        ikStartJoint        = self.ikJoints[0]
        ikEndJoint          = self.ikJoints[-1]
        ikInbetweenJoints   = self.ikJoints[1:-1]
        averagePoint        = transform.averagePosition(ikInbetweenJoints)
        pointList           = list()
        
        #create a point list
        pointList.append(cmds.xform(ikStartJoint,
                                    q = True,
                                    ws = True,
                                    rp = True))

        #gather the position between joints and add to pointList
        for i,jnt in enumerate(self.ikJoints):
            if jnt == self.ikJoints[-1]:
                break
            #end if
            pointList.append(transform.averagePosition([jnt,
                                                        self.ikJoints[i+1]]))
        #end loop
        
        #append to the point list
        pointList.append(cmds.xform(self.ikJoints[-1],
                                    q = True,
                                    ws = True,
                                    rp = True))
        
        #spineCurve = curve.createFromPoints(pointList, degree = 3)
        self.surface = surface.createFromPoints(pointList, 
                                                name = '%s_%s' % 
                                                (self.name,common.SURFACE))
        cmds.parent(self.surface, self.group)
        for i,jnt in enumerate(ikInbetweenJoints):
            #get U and V parameters on the surface 
            jntParam_u, jntParam_v = surface.getParamFromPosition(self.surface,
                                                                   jnt)
            follicle = (surface.createFollicle(self.surface,
                                               '%s_%s'% (jnt,common.FOLLICLE),
                                               jntParam_u,
                                               jntParam_v))
            
            follicleTrans = common.getParent(follicle)
            
            targetJnt = common.duplicate(jnt,
                                         '%s_%s_%s_%s'% 
                                         (self.name,
                                          common.TARGET,
                                          common.padNumber(i, 3),
                                          common.JOINT),
                                         parent = follicleTrans)
            
            #constrain ikJoint to target joint
            cmds.parent(follicleTrans,self.group)
            cmds.parentConstraint(targetJnt, jnt)
            self.follicles.append(follicleTrans)
            self.targetJoints.append(targetJnt)
        #end loop
        
        
        #DRIVER JOINTS
        #------------------------------------------
        parent = self.group
        position = averagePoint
        #create driver joints
        for i in range(1,4):
            jnt = (joint.create('%sMiddle_%s_%s_%s'% 
                                (self.name,common.DRIVER,
                                 common.padNumber(i, 3),
                                 common.JOINT
                                 ),
                                parent = parent,
                                position = position)
                   )
            #append jnt to the middle driver joint dict
            self.driverJoints['middle'].append(jnt)                
                
            #declare parent as the first middle driver joint
            parent = self.driverJoints['middle'][0]
            position = pointList[i + 1]
        #end loop
        
        parentStart = self.group
        parentEnd = self.group
        
        for i in range(1,3):
            self.driverJoints['start'].append(common.duplicate
                                              (ikStartJoint,
                                               '%sStart_%s_%s_%s'% 
                                               (self.name,common.DRIVER,
                                                common.padNumber(i, 3),
                                                common.JOINT),
                                               parent = parentStart))
            #declare parent as the first middle driver joint
            parentStart = self.driverJoints['start'][i - 1]
            
            self.driverJoints['end'].append(common.duplicate
                                            (ikEndJoint,
                                             '%sEnd_%s_%s_%s'%
                                             (self.name,common.DRIVER,
                                              common.padNumber(i, 3),
                                              common.JOINT),
                                             parent = parentEnd))
            
            parentEnd = self.driverJoints['end'][i - 1]
        #end loop

        #VARIABLE DECLERATION FOR JOINTS USED IN REST OF FUNCTION
        #------------------------------------------
        #declare start driver joints
        startDriverJoint1 = self.driverJoints['start'][0]
        startDriverJoint2 = self.driverJoints['start'][1]

        #declare middle driver joints
        middleDriverJoint1 = self.driverJoints['middle'][0]
        middleDriverJoint2 = self.driverJoints['middle'][1]
        middleDriverJoint3 = self.driverJoints['middle'][2]
        
        #declare start driver joints
        endDriverJoint1 = self.driverJoints['end'][0]
        endDriverJoint2 = self.driverJoints['end'][1]


        #START SECONDARY DRIVERS SETUP
        #------------------------------------------
        startUpJoint = common.duplicate(startDriverJoint1,
                                        startDriverJoint1.replace
                                        ('_%s_' % common.DRIVER,
                                         '_%s_' % common.UP),
                                        parent = startDriverJoint1)
        
        
        cmds.xform(startUpJoint, ws = True, relative = True, t = [0,0,1])
        upAxis = transform.getAimAxis(startUpJoint) #<---get up axis
        self.upAxis = upAxis #<---need to have all variables match proceeding
        
        cmds.xform(startDriverJoint2, ws = True, t = pointList[1])
        
        #END SECONDARY DRIVERS SETUP
        #------------------------------------------
        endUpJoint = common.duplicate(endDriverJoint1,
                                        endDriverJoint1.replace
                                        ('_%s_' % common.DRIVER,
                                         '_%s_' % common.UP),
                                        parent = endDriverJoint1)
        
        
        cmds.xform(endUpJoint, ws = True, relative = True, t = [0,0,1])
        
        cmds.xform(endDriverJoint2, ws = True, t = pointList[-2])
        
        
        #MIDDLE SECONDARY DRIVERS SETUP
        #------------------------------------------
        #create up and aim joints
        self.upJoint = common.duplicate(middleDriverJoint1,
                                        middleDriverJoint1.replace
                                        ('_%s_' % common.DRIVER,
                                         '_%s_' % common.UP),
                                        parent = self.group)
        
        self.aimJoint = common.duplicate(middleDriverJoint1,
                                        middleDriverJoint1.replace
                                        ('_%s_' % common.DRIVER,
                                         '_%s_' % common.AIM),
                                        parent = self.group)
        
        #parent middleDriver to aimJoint
        cmds.parent(middleDriverJoint1, self.aimJoint)
        cmds.xform(self.upJoint, relative = True, t = [0,0,1])

        cmds.pointConstraint(self.driverJoints['start'][0],
                             self.driverJoints['end'][0],
                             self.aimJoint,
                             mo = True)
        #parent constraint middle up joint to the start and end joints
        cmds.pointConstraint(startUpJoint, 
                              endUpJoint,
                              self.upJoint,
                              mo = True)
        
        #aim middle driver joint to end driver
        cmds.aimConstraint(self.driverJoints['end'][0],
                           self.aimJoint,
                           aim = transform.AXES[self.aimAxis],
                           u = transform.AXES[upAxis],
                           worldUpObject = self.upJoint,
                           worldUpType = 'object')
        
        
        #MIDDLE DRIVER attributes - ADD and CONNECT 
        #------------------------------------------
        #get translate on the aim axis        
        trsDriver2 = cmds.getAttr('%s.t%s' % (middleDriverJoint3,
                                              self.aimAxis))
        
        #create a multiply divide to invert the attribute
        invertMDN = cmds.createNode('multiplyDivide',
                                    n = middleDriverJoint2.replace
                                    ('_%s' % common.JOINT, 
                                     '_%s' % common.MULTIPLYDIVIDE))
        #set the multiply divide node attributes to invert the direction
        cmds.setAttr('%s.input1X' % invertMDN, -1)
        
        #create the attribute on the main driver joint
        driver1Attr = attribute.addAttr(middleDriverJoint1,
                                        'driver1',
                                        defValue = trsDriver2,
                                        min = 0)
        
        driver2Attr = attribute.addAttr(middleDriverJoint1,
                                        'driver2',
                                        defValue = trsDriver2,
                                        min = 0)
        
        #connect driver attributes to the joints
        attribute.connect(driver1Attr,
                          '%s.input2X' % invertMDN)
        attribute.connect('%s.outputX' % invertMDN,
                          '%s.t%s' % (middleDriverJoint2,
                                      self.aimAxis))
        attribute.connect(driver2Attr,
                          '%s.t%s' % (middleDriverJoint3,
                                      self.aimAxis))
        
        cmds.parentConstraint(startDriverJoint1, self.ikJoints[0])
        cmds.parentConstraint(endDriverJoint1, self.ikJoints[0-1])
        
        #attach skinCluster
        jointList = (self.driverJoints['start'])
        jointList.extend(self.driverJoints['middle'])
        jointList.extend(self.driverJoints['end'])
        cmds.skinCluster(jointList,
                         self.surface,
                         bindMethod = 0,
                         tsb = True,
                         mi = 1, 
                         dr = 1.0,
                         sm = 0,
                         swi = 1,
                         sw = 1.0,
                         omi = True)




class SplineIk(IkFk):
    @classmethod
    def rbf1D (cls,value, values): #<--------Need to put in a util library
        '''
        Function to interpolate data in one dimension.
    
        Example:
    
        >>> rbf1D (2.1, [1, 2, 3, 4, 5])
        [0, 0.9, 0.1, 0, 0]
    
        @param value: Value to be interpolated
        @type value: *int* or *float*
    
        @param values: Key values for interpolation
        @type values: *list* or *tuple*
    
        @return: Weights per each value in values
        @rtype: *list*
        '''
        # get cell
        prev = -1
        next = -1
        prevDist = 999999999999.9
        nextDist = 999999999999.9
        for i in range(len(values)):
        
            # get prev
            if values[i]<=value:
                dist = value-values[i]
                if dist<prevDist:
                    prevDist = dist
                    prev = i
            # get next    
            if values[i]>=value:
                dist = values[i]-value
                if dist<nextDist:
                    nextDist = dist
                    next = i
        
        # get weights
        weights = [0.0]*len(values)
        
        # if out of range
        if prev == -1:
            weights[next] = 1.0
            return weights
        if next == -1:
            weights[prev] = 1.0
            return weights
        
        # if in range
        if prev!=next:
            weights[next] = 1.0 / (values[next]-values[prev]) * ( value - values[prev] )
            weights[prev] = 1.0-weights[next]
            return weights
        else:
            weights[prev] = 1.0
            return weights
    # Create IK Spline Function
    @classmethod
    def createSpline(cls, startJoint, endJoint , indices, parent = None, name = "ikSpline"):
        '''
        Creates ikSpline rig with basic functionality for stretch and twist.
        Use to tool as starting point for your ikSpline rig like: spine, tails, neck, etc.
        
        :param startJoint: First joint of your chain
        :type startJoint: *str*
    
        :param endJoint: Last joint of your chain
        :type endJoint:  *str*
    
        :param indices: Indices where you want to create your driver controls
        :type indices: *list* or *tuple*
    
        :param parent: Parent for the top group
        :type parent: *str*
    
        :param name: IK spline system name
        :type name: *str*
    
        :return: ikSpline group
        :rtype: *str*
    
        .. python:
            import maya.cmds as cmds
        
            for i in range (7):
                cmds.joint (p = (0,2 * i, 0))
            ikSpline ("joint1", "joint7", [0, 3, 6], name = "spineIk")
        '''
        # Load IK Stretch and decompose rotation plugins
        #application.loadPlugin ("ikStretch", quiet = True)
        #fileIO.loadPlugin ("decomposeRotation.py", quiet = True)
        
        # get chain
        joints = [startJoint]
        joints.extend(common.getInbetweenNodes( startJoint, endJoint))
        joints.append(endJoint)
        
        # get aim axis
        aimAxis = transform.getAimAxis( startJoint, allowNegative=False )
        
        # check indices
        if max(indices) > len(joints):
            raise IndexError, 'list index out of range'
        
        # create groups
        grp = cmds.createNode ("transform", name = name, parent = parent)
        
        # duplicate chain
        
        ikJoints = list()
        parent = grp
        for jnt in joints:
            ikJoint = common.duplicate( jnt , name= '%sIK' % jnt, parent=parent )
            if parent != grp:
                if not attribute.isConnected('inverseScale', ikJoint, True, False):
                    attribute.connect('%s.scale' % parent, '%s.inverseScale' % ikJoint)
                #end if
            #end if
            parent = ikJoint
            ikJoints.append(ikJoint)
        #end loop
        
        # --------------------------------------------------------------------------
        # CREATE DRIVERS
        
        numDrivers= len(indices)
        driverGrp = []
        driverJoints = []
        for i in indices:
            j = common.duplicate( joints[i], name='%sDriverGrp' % joints[i], parent = grp )
            jj = common.duplicate( joints[i], name='%sDriver' % joints[i], parent = j )
            driverGrp.append( j )
            driverJoints.append( jj )
        #end loop
        
        # --------------------------------------------------------------------------
        # CREATE NURBS CURVE
        
        nurbsCurve = curve.createFromTransforms (joints, degree = 1, name = "%sCurve" % name)
        cmds.parent( nurbsCurve.name, grp )
        nurbsShape = cmds.listRelatives(nurbsCurve.name,s=True,ni=True)[0]
        cmds.setAttr('%s.%s' % (nurbsShape,'dispCV'), True)
        cmds.setAttr('%s.%s' % (nurbsCurve.name,'inheritsTransform'), False)
        # --------------------------------------------------------------------------
        # CREATE SKINCLUSTER WEIGHTS
        
        # add rebuildCurve pre-skinCluster
        tweakTemp = cmds.deformer(nurbsShape,type='tweak')
        cmds.rebuildCurve(nurbsShape,ch=True,rpo=1,rt=0,end=1,kr=0,kcp=False,kep=False,kt=False,s=len(joints)*2,d=3,tol=0.01,name='linearToCubic_rebuildCurve')
        
        # smooth curve
        cmds.smoothCurve( '%s.cv[*]' % nurbsShape, constructionHistory=True, smoothness=10 )
        
        # add skinCluster
        skinCluster = cmds.skinCluster (driverJoints, nurbsCurve.name, tsb = True, name = "%sScls" % name) [0]
        
        # delete temporal tweak
        cmds.delete(tweakTemp)
        
        # --------------------------------------------------------------------------
        # EDIT SKINCLUSTER WEIGHTS
        
        # get drivers parameter
        parameters = []
        for i in range(numDrivers):
            pos = cmds.xform( driverJoints[i] ,q=True,ws=True,rp=True )
            param = curve.getParamFromPosition( nurbsShape, pos )
            parameters.append( param )
        
        # connect drivers to curve
        cvs = cmds.ls( '%s.cv[*]' % nurbsCurve.name, fl=True )
        for i in range(len(cvs)):
            
            # get cv parameter
            cv      = cvs[i]
            cvPos   = cmds.pointPosition( cv, world=True ) 
            cvParam = curve.getParamFromPosition( nurbsShape,cvPos )
            
            # weights
            weights = SplineIk.rbf1D( cvParam, parameters )
            
            for ii in range(numDrivers):
                cmds.skinPercent(skinCluster, cv,
                                 transformValue=(driverJoints[ii],weights[ii]))
        
        # --------------------------------------------------------------------------
        # CREATE IK-HANDLE
        
        ikHandle = IkFk.createIkHandle (ikJoints[0], ikJoints[-1],
                                        name="%s_%s" % (name,common.IKHANDLE),
                                        type = "ikSplineSolver",
                                        crv = nurbsCurve.name,parent = grp)[0]
        
        # --------------------------------------------------------------------------
        # NORMALIZE CURVE
        #@todo: Normalize curve if need be

        # --------------------------------------------------------------------------
        # ADD TWIST
        
        # create twist driver joints
        for i in range(numDrivers):
            
            for j in [driverGrp[i],driverJoints[i]]:
                attribute.addAttr(j,  'twist', 'double' )
                decomRot = cmds.createNode('decomposeRotation')
                cmds.connectAttr( '%s.%s' % (j,'rotate'), '%s.%s' % (decomRot,'targetRotation') )
                cmds.connectAttr( '%s.%s' % (decomRot,'twist%s' % aimAxis.upper() ), '%s.%s' % (j,'twist') )
        
        # create twist ik joints
        twistJoints = []
        for i in range(len(ikJoints)):
            # create twist joint
            twistJoint = cmds.createNode( 'joint', name='%s_twist' % ikJoints[i], parent=ikJoints[i] )
            cmds.setAttr( '%s.%s' % (twistJoint,'displayScalePivot'), True )
            cmds.setAttr( '%s.%s' % (twistJoint,'displayLocalAxis'), True )
            twistJoints.append( twistJoint )
            
            # get weights
            twistPos = cmds.xform( twistJoint ,q=True,ws=True,rp=True )
            twistParam = curve.getParamFromPosition( nurbsShape, twistPos )
            weights = SplineIk.rbf1D( twistParam, parameters )
            
            # add twist
            plusNode = cmds.createNode('plusMinusAverage')
            for ii in range(numDrivers):
                # add driverGrp twist
                multNode = cmds.createNode('multDoubleLinear')
                cmds.connectAttr( '%s.%s' % (driverGrp[ii],'twist'), '%s.%s' % (multNode,'input1') )
                cmds.setAttr( '%s.%s' % (multNode,'input2'), weights[ii] )
                cmds.connectAttr( '%s.%s' % (multNode,'output'), '%s.%s[%i]' % (plusNode,'input1D',ii) )
            
                # add driverJoint twist
                multNode = cmds.createNode('multDoubleLinear')
                cmds.connectAttr( '%s.%s' % (driverJoints[ii],'twist'), '%s.%s' % (multNode,'input1') )
                cmds.setAttr( '%s.%s' % (multNode,'input2'), weights[ii] )
                cmds.connectAttr( '%s.%s' % (multNode,'output'), '%s.%s[%i]' % (plusNode,'input1D',ii+numDrivers ) )
            
            cmds.connectAttr( '%s.%s' % (plusNode,'output1D'), '%s.%s' % (twistJoint,'rotate%s' % aimAxis.upper()) )
        
        # --------------------------------------------------------------------------
        # CONNECT FIRST & LAST JOINT
        # Needs to be implemented the twist in startJoint
        #
        attribute.addAttr( grp,'startOrient', 'double', min = 0.0, max = 1.0, defValue = 1.0 )
        attribute.addAttr( grp,'endOrient', 'double', min = 0.0, max = 1.0, defValue = 1.0 )
    
        # startOrient
        cmds.disconnectAttr( cmds.listConnections( '%s.%s' % ( twistJoints[0] , 'rotate%s' % aimAxis.upper()), s=True,d=False, plugs=True )[0], '%s.%s' % ( twistJoints[0] , 'rotate%s' % aimAxis.upper()) )
        constraint = cmds.orientConstraint( driverJoints[0], ikJoints[0], twistJoints[0] )[0]
        cmds.setAttr( '%s.%s' % (constraint,'interpType') , 2 )
        attribute.connect( '%s.%s' % (grp,'startOrient'),  '%s.%sW0' % (constraint,driverJoints[0]) )
        inv = cmds.createNode ("reverse", name = "%sStartOrient" % grp)
        attribute.connect( '%s.%s' % (grp,'startOrient'),  '%s.inputX' % inv)
        attribute.connect( '%s.%s' % (inv,'outputX'),  '%s.%sW1' % (constraint,ikJoints[0]))
    
        # endOrient
        cmds.disconnectAttr( cmds.listConnections( '%s.%s' % ( twistJoints[-1] , 'rotate%s' % aimAxis.upper()), s=True,d=False, plugs=True )[0], '%s.%s' % ( twistJoints[-1] , 'rotate%s' % aimAxis.upper()) )
        constraint = cmds.orientConstraint( driverJoints[-1], ikJoints[-1], twistJoints[-1] )[0]
        cmds.setAttr( '%s.%s' % (constraint,'interpType') , 2 )
        attribute.connect( '%s.%s' % (grp,'endOrient'),  '%s.%sW0' % (constraint,driverJoints[-1]) )
        inv = cmds.createNode ("reverse", name = "%sStartOrient" % grp)
        attribute.connect( '%s.%s' % (grp,'endOrient'),  '%s.inputX' % inv)
        attribute.connect( '%s.%s' % (inv,'outputX'),  '%s.%sW1' % (constraint,ikJoints[-1]))
        
        # --------------------------------------------------------------------------
        # CONNECT TO JOINTS
        
        for i in range(len(joints)):
            cmds.parentConstraint( twistJoints[i], joints[i] )
            
        splineInfo = {'group'        : grp,
                      'ikHandle'     : ikHandle,
                      'curve'        : nurbsCurve, #<---This is an instance of the Curve object
                      'driverJoints' : driverJoints,
                      'aimAxis'      : aimAxis,
                      'ikJoints'     : ikJoints
                      }
        
        return splineInfo


    def __init__(self, *args, **kwargs):
        super(SplineIk, self).__init__(*args, **kwargs)
        self.curve = str()
        
    def create(self, indices):
        super(SplineIk, self).create()
        splineInfo        = SplineIk.createSpline(self.ikJoints[0], self.ikJoints[-1], indices, name = self.name, parent = self.group)
        self.curve        = splineInfo['curve'] #<---This is an instance of the Curve object
        self.driverJoints = splineInfo['driverJoints']
        self.ikHandle     = splineInfo['ikHandle']
        self.splineJoints = splineInfo['ikJoints']
        



#---------------------------------------------------------------------
#NEED TO GET RID OF SOME OF THESE DEPRECATED FUNCTIONS
#ONCE THEY ARE TAKEN OUT OF COMPONENT BUILDS!
#---------------------------------------------------------------------

def createIkHandle(startJoint, endJoint, type = 'ikRPsolver', name = None, parent = None):
    '''
    Example:
    ..python
    createIkHandle("l_upArm_ik_jnt", "l_wrist_ik_jnt", name = "l_arm_ik_hdl", parent = "ikfk_grp")
    #Return: ["l_arm_ik_hdl
    
    @param startJoint: first joint in the chain for the ikHandle to effect
    @type startJoint: *str*
    
    @param endJoint: last joint in the chain for the ikHandle to effect
    @type endJoint: *str*
    
    @param type: The type of ikHandle used on creation
    @type type: *str*
    :options: 'ikRPsolver', ikSCSolver
    
    @param name: Name given to the ikHandle
    @type name: *str*
    
    @param parent: Parent object for the ikHandle
    @type parent: *str*
    
    @return ikHandle: Name of the ikHandle
    @rtype ikHandle: *str*
    
    @return effector: Name of the effector of the ikHandle
    @rtype effector: *str*
    
    '''
    if not name:
        name = common.IKHANDLE
    
    ikHandle = cmds.ikHandle(n = name, sj = startJoint, ee = endJoint, sol = type)
    effector = ikHandle[1]
    ikHandle = ikHandle[0]
    
    if parent:
        cmds.parent(ikHandle, parent)
        
    return ikHandle, effector

    
def getPoleVectorPosition(middleJoint, ikHandle):
    '''
    get the correct pole vector position
    
    Example:

	..python:
	    getPoleVectorPosition("l_loArm_jnt", "l_arm_ik_hdl")
	    #Result [4,10,-5]

    '''
    poleVector = cmds.getAttr('%s.poleVector' % ikHandle)[0]
    middleJointPos = cmds.xform(middleJoint, q = True, ws = True, t = True)
    
    return [middleJointPos[i] + poleVector[i] for i in range(len(middleJointPos))]

    
def createStretchIK(ikHandle, grp):
    '''
    creates a stretchy joint chain based off of influences on ikHandle
    
    Example:

	..python:
	    createStrecthIK('l_leg_ik_hdl')
	    #Return: 

    @param ikHandle: ik handle you influencing joint chain you want to stretch
    @type ikHandle: *str*
    
    :retrun targetJnts: Joints that are used to calculate the distance
    @rtype: *list*
    '''
    if not grp or not common.isValid(grp):
        grp = cmds.createNode('transform', n = 'ik_stretch_grp')

    #create attributes on grp node
    stretchAttr  = attribute.addAttr(grp, 'stretch', defValue = 1, min = 0, max = 1)
    stretchTopAttr = attribute.addAttr(grp, 'stretchTop', defValue = 1)
    stretchBottomAttr = attribute.addAttr(grp, 'stretchBottom', defValue = 1)
    
    #get joints influenced by the ikHandle
    jnts = cmds.ikHandle(ikHandle, q = True, jl = True)
    jnts.append(common.getChildren(jnts[-1])[0])
    #create tgt joints for distance node
    targetJnt1 = cmds.createNode('joint', n = '%s_%s' % (jnts[0], common.TARGET))
    targetJnt2 = cmds.createNode('joint', n = '%s_%s' % (jnts[2], common.TARGET))
    transform.matchXform(jnts[0], targetJnt1, 'position')
    transform.matchXform(jnts[2], targetJnt2, 'position')
    
    #create distance and matrix nodes
    distanceBetween = cmds.createNode('distanceBetween', n = '%s_%s' % (ikHandle, common.DISTANCEBETWEEN))
    startDecomposeMatrix = cmds.createNode('decomposeMatrix', n = '%s_%s' % (targetJnt1, common.DECOMPOSEMATRIX))
    endDecomposeMatrix = cmds.createNode('decomposeMatrix', n = '%s_%s' % (targetJnt2, common.DECOMPOSEMATRIX))
    
    #create condition and multplyDivide nodes
    multiplyDivide = cmds.createNode('multiplyDivide', n = '%s_%s' % (ikHandle, common.MULTIPLYDIVIDE))
    condition = cmds.createNode('condition', n = '%s_%s' % (ikHandle, common.CONDITION))
    multiplyDivideJnt1 = cmds.createNode('multiplyDivide', n = '%s_%s' % (jnts[1], common.MULTIPLYDIVIDE))
    
    blendColorStretch = cmds.createNode('blendColors', n = '%s_stretch_%s' % (grp, common.BLEND))
    multiplyStretch = cmds.createNode('multiplyDivide', n = '%s_stretch_%s' % (grp, common.MULTIPLYDIVIDE))
    plusMinusStretch = cmds.createNode('plusMinusAverage', n = '%s_stretch_%s' % (grp, common.PLUSMINUSAVERAGE))
    
    #connect matrix nodes to distance between node
    cmds.connectAttr('%s.worldMatrix[0]' % targetJnt1, '%s.inputMatrix' % startDecomposeMatrix, f = True)
    cmds.connectAttr('%s.worldMatrix[0]' % targetJnt2, '%s.inputMatrix' % endDecomposeMatrix, f = True)
    cmds.connectAttr('%s.outputTranslate' % startDecomposeMatrix, '%s.point1' % distanceBetween, f = True)
    cmds.connectAttr('%s.outputTranslate' % endDecomposeMatrix, '%s.point2' % distanceBetween, f = True)
    
    #connect multiplyDivide and condition nodes
    aimAxis = transform.getAimAxis(jnts[1], False)
    jnt1Distance = attribute.getValue('%s.t%s' % (jnts[1], aimAxis))
    jnt2Distance = attribute.getValue('%s.t%s' % (jnts[2], aimAxis))
    jntLength = jnt1Distance + jnt2Distance
    cmds.setAttr('%s.operation' % multiplyDivide, 2)    
    if jntLength < 0:
        negDistanceMultiply = cmds.createNode('multiplyDivide', n = '%s_distanceNeg_%s' % (grp, common.MULTIPLYDIVIDE))
        cmds.connectAttr('%s.distance' % distanceBetween, '%s.input1X' % negDistanceMultiply, f = True)
        cmds.setAttr('%s.input2X' % negDistanceMultiply, -1)
        cmds.connectAttr('%s.outputX' % negDistanceMultiply, '%s.input1X' % multiplyDivide, f = True)
        cmds.connectAttr('%s.outputX' % negDistanceMultiply, '%s.firstTerm' % condition, f = True)
        cmds.setAttr('%s.operation' % condition, 4)
    else:
        cmds.connectAttr('%s.distance' % distanceBetween, '%s.input1X' % multiplyDivide, f = True)
        cmds.connectAttr('%s.distance' % distanceBetween, '%s.firstTerm' % condition, f = True)
        cmds.setAttr('%s.operation' % condition, 2)

    cmds.connectAttr('%s.outputX' % multiplyDivide, '%s.input1X' % multiplyDivideJnt1, f = True)
    cmds.connectAttr('%s.outputX' % multiplyDivide, '%s.input1Y' % multiplyDivideJnt1, f = True)
    cmds.connectAttr('%s.outputX' % multiplyDivideJnt1, '%s.colorIfTrueR' % condition, f = True)
    cmds.connectAttr('%s.outputY' % multiplyDivideJnt1, '%s.colorIfTrueG' % condition, f = True)
    cmds.connectAttr('%s.outColorR' % condition, '%s.t%s' % (jnts[1], aimAxis), f = True)
    cmds.connectAttr('%s.outColorG' % condition, '%s.t%s' % (jnts[2], aimAxis), f = True)

    attribute.connect(stretchAttr, '%s.blender' % blendColorStretch)
    attribute.connect(stretchTopAttr, '%s.input1X' % multiplyStretch)
    cmds.setAttr('%s.input2X' % multiplyStretch, jnt1Distance)
    attribute.connect(stretchBottomAttr, '%s.input1Y' % multiplyStretch)
    cmds.setAttr('%s.input2Y' % multiplyStretch, jnt2Distance)
    attribute.connect('%s.outputX' % multiplyStretch, '%s.input2D[0].input2Dx' % plusMinusStretch)
    attribute.connect('%s.outputY' % multiplyStretch, '%s.input2D[1].input2Dx' % plusMinusStretch)
    attribute.connect('%s.output2Dx' % plusMinusStretch, '%s.input2X' % multiplyDivide)
    attribute.connect('%s.output2Dx' % plusMinusStretch, '%s.secondTerm' % condition)
    attribute.connect('%s.outputX' % multiplyStretch, '%s.colorIfFalseR' % condition)
    attribute.connect('%s.outputY' % multiplyStretch, '%s.colorIfFalseG' % condition)
    attribute.connect('%s.outputX' % multiplyStretch, '%s.input2X' % multiplyDivideJnt1)
    attribute.connect('%s.outputY' % multiplyStretch, '%s.input2Y' % multiplyDivideJnt1)
    
    attribute.connect('%s.outColorR' % condition, '%s.color1R' % blendColorStretch)
    attribute.connect('%s.outputX' % multiplyStretch, '%s.color2R' % blendColorStretch)
    attribute.connect('%s.outColorG' % condition, '%s.color1G' % blendColorStretch)
    attribute.connect('%s.outputY' % multiplyStretch, '%s.color2G' % blendColorStretch)
    
    attribute.connect('%s.outputR' % blendColorStretch, '%s.t%s' % (jnts[1], aimAxis))
    attribute.connect('%s.outputG' % blendColorStretch, '%s.t%s' % (jnts[2], aimAxis))
    
    #parent ikHandle under targetJnt2
    cmds.parent(ikHandle, targetJnt2)
    
    #turn off visibility of targetJnts and parent under grp node
    for jnt in [targetJnt1, targetJnt2]:
        cmds.setAttr('%s.v' % jnt, 0)
        cmds.parent(jnt, grp)

    return [targetJnt1, targetJnt2]

    
def create(jointChain, stretch = False):
    '''
    create an ik, fk, and blend joint chain. Blend chain switches between ik and fk
    
    Example:
    ..python
    create(["l_upArm_sc_jnt", "l_loArm_sc_jnt", "l_wrist_sc_jnt"])
    
    @param jointChain: Joint chain you want to use to create ik/fk chains from
    @type jointChain: *list* or *tuple*
    
    @param stretch: Makes ikfk chains stretch
    @type stretch: *bool*
    
    @return ikfkDict: dictionary containing joints chains, ikhandle, and group name
    @rtype ikfkDict: *dict*
    '''
    grp = cmds.createNode('transform', name = 'ikfk_%s' % common.GROUP)

    #ik joints
    ikJnts = list()
    parent = grp
    for jnt in jointChain:
        j = common.duplicate(jnt, name = '%s_%s' % (jnt, common.IK), parent = parent)
        ikJnts.append(j)
        parent = j

    #fk joints
    fkJnts = list()
    parent = grp
    for jnt in jointChain:
        j = common.duplicate(jnt, name = '%s_%s' % (jnt,common.FK), parent = parent)
        fkJnts.append(j)
        parent = j
        
    #blend joints
    blendJnts = list()
    parent = grp
    for jnt in jointChain:
        j = common.duplicate(jnt, name = '%s_%s' % (jnt, common.BLEND), parent = parent)
        blendJnts.append(j)
        parent = j
    
    
    #createikfk attr
    ikfkAttr = attribute.addAttr(grp, attr = 'ikfk', attrType = 'enum', defValue = ['off','on'],value = 0)
    
    #attatch blend chain to ik and fk chain
    for i,jnt in enumerate(blendJnts):
        blendNode = cmds.createNode('blendColors', n = jnt.replace(common.JOINT, common.UTILITY))
        cmds.connectAttr('%s.r' % fkJnts[i], '%s.color1' % blendNode)
        cmds.connectAttr('%s.r' % ikJnts[i], '%s.color2' % blendNode)
        cmds.connectAttr(ikfkAttr, '%s.blender' % blendNode)
        cmds.connectAttr('%s.output' % blendNode, '%s.r' % jnt)

        blendNode = cmds.createNode('blendColors', n = jnt.replace(common.JOINT, common.UTILITY))
        cmds.connectAttr('%s.t' % fkJnts[i], '%s.color1' % blendNode)
        cmds.connectAttr('%s.t' % ikJnts[i], '%s.color2' % blendNode)
        cmds.connectAttr(ikfkAttr, '%s.blender' % blendNode)
        cmds.connectAttr('%s.output' % blendNode, '%s.t' % jnt)

        cmds.parentConstraint(jnt, jointChain[i])

    ikHandle = createIkHandle(ikJnts[0], ikJnts[2], name = ikJnts[0].replace(common.JOINT, common.HANDLE), parent = grp)[0]
    cmds.setAttr('%s.v' % ikHandle, 0)
    
    if stretch:
        #ik stretch setup
        targetJnts  = createStretchIK(ikHandle, grp)

    ikfkDict = {'group' : grp, 'ikJoints' : ikJnts, 'fkJoints' : fkJnts, 'blendJoints' : blendJnts, 'ikHandle' : ikHandle, 'targetJnts' : targetJnts}
        
    return ikfkDict 
