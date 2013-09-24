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
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import transform 
from japeto.libs import ordereddict


#------------------------------------------------------------
#                      IK/FK Base CLASS
#------------------------------------------------------------
class IkFk(object):
    @classmethod
    def createIkHandle(cls,startJoint, endJoint, type = 'ikRPsolver', name = None, parent = None):
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
    
    
    
    def __init__(self, startJoint, endJoint, name = str(), parent = str()):
        super(IkFk, self).__init__()
        
        #private 
        self.__startJoint = startJoint
        self.__endJoint   = endJoint
        self.__parent     = parent
        self.__name       = name
        self.__group      = '%s%s' % (common.IK, common.FK)
        
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
    
    
    #SETTERS
    @group.setter
    def group(self, value):
        if cmds.objExists(self.__group):
            cmds.rename(self.__group, value)
            
        self.__group = value
    
    def __getJointChain(self):
        '''
        @TODO: Get all the joints from original chain
        '''
        origJnts = list()
        
        #getting all joints inbetween start and end joint
        inbetweeenJnts = common.getInbetweenNodes(self.__startJoint, self.__endJoint, list())
        
        #reverse joint list
        inbetweeenJnts.reverse()
        
        #declare origJnts as inbetweeenJnts
        origJnts = inbetweeenJnts
            
        #inserting start and end
        origJnts.insert(0, self.__startJoint)
        origJnts.insert(len(origJnts), self.__endJoint)
        
        #declaring class attribute list of original joints
        return tuple(origJnts)
    
    

    def create(self, searchReplace = str()):
        #create ik/fk group node
        if self.name:
            self.group = ('%s_%s' % (self.name, self.group))
        cmds.createNode('transform', n = self.group)
        cmds.addAttr(self.group, ln = 'ikfk', at = 'double', min = 0, max = 1, dv = 0, keyable = True)
        
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
        
        cmds.xform(pvDriver, ws = True, t = newPvPos)
        cmds.xform(ikDriver, ws = True, t = endJntPos)
        
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
            ikHdl , effector = createIkHandle(self.ikJoints[i], self.ikJoints[i+1], type = 'ikSCsolver',
        		   name = common.searchReplaceRename(self.ikJoints[i+1], '_%s' % common.JOINT, '_%s' % common.HANDLE), parent = self.group)
            #append ik handle to ikHandles list
            self.__ikHandles.append(ikHdl)
        #end loop
        
        #add foot rolls attribute on ik/fk group node
        footRollAttr = attribute.addAttr(self.group, 'footRolls', attrType = 'message')
        
        #create foot roll groups
        parent = self.group
        for grp in footRollGrpList:
            #store each group in the footRollDict
            self.__footRollGrpDict[grp] = cmds.createNode('transform', n = '%s_%s' % (self.name(), grp))
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
    ikfkAttr = attribute.addAttr(grp, 'ikfk', defValue = 0, value = 0, min = 0, max = 1)
    
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

    ikHandle, effector = createIkHandle(ikJnts[0], ikJnts[2], name = ikJnts[0].replace(common.JOINT, common.HANDLE), parent = grp)
    cmds.setAttr('%s.v' % ikHandle, 0)
    
    if stretch:
    	#ik stretch setup
    	targetJnts  = createStretchIK(ikHandle, grp)

    ikfkDict = {'group' : grp, 'ikJoints' : ikJnts, 'fkJoints' : fkJnts, 'blendJoints' : blendJnts, 'ikHandle' : ikHandle, 'targetJnts' : targetJnts}
        
    return ikfkDict 
