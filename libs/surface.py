# '''
# Library to work with surfaces
#
# @author:Walter Yoder
# @contact: walteryoder@gmail.com
# @author: Jeff Brodsky
# @date: December 2012
#
#
# @points on a surface: closestPointOnSurface buildDictClosestPointSurface createFollicles
# '''
# #---------------------------------------------------------------------------------------
import os
import sys
import doctest

#import Maya Modules
import maya.cmds as cmds
import maya.mel as mel

#Import package Modules
from japeto.libs import common
from japeto.libs import jsonData
from japeto.libs import curve
from japeto.libs import transform

#Constant Variables
INFORMATION = ['position','width', 'patchesU','patchesV', 'pivot', 'lengthRatio', 'axis']


def createFromPoints(points, degree = 3, direction = 'x',name = "newSurface", spansU = 0, spansV = 0):
    ''' 
    Build curve from transforms 
    
    Example: 
    #        >>> createFromTransforms (["transform1", "transform2"], 1, "newSurface")
        
        
    @param transforms: Transform object to place point to draw the curve
    @type transforms: *list*
    
    @param degree: degree of the curve, linear or cubic
    @type degree: *int*
    '''
    
    if not isinstance(points, list):
        raise RuntimeError, 'There needs to be more then one transform, transforms argument must be a type *list*'

    #generate the first curve
    curve_one = curve.createFromPoints (points, degree, "tmpCurve1")
    #move curve in the proper direction
    cmds.move(transform.AXES[direction][0], transform.AXES[direction][1], transform.AXES[direction][2], curve_one, r=True)
    #generate the first curve
    curve_two = curve.createFromPoints (points, degree, "tmpCurve2")
    #move curve in the proper direction
    cmds.move(transform.AXES['-%s' % direction][0], transform.AXES['-%s' % direction][1], transform.AXES['-%s' % direction][2], curve_two, r=True)
    
    
    if degree == 3:
        surface = cmds.loft(curve_one,curve_two,ch=False,ss=0,n=name)[0]
        cmds.rebuildSurface(surface,kr=0,kcp=True)
    elif degree == 1:
        surface = cmds.loft(curve_one,curve_two,ch=False,ss=0, degree =1, rebuild = True,n=name)[0]
        cmds.rebuildSurface(surface,ch = False, rpo = 1, rt= 0, end = 1, kr = 0, kcp = 0, kc = 0, tol = 0.01, fr = 0, dir = 2, du = degree, dv = degree, su = spansU, sv = spansV) 
        
    #delete curves
    cmds.delete((curve_one,curve_two))
    
    return surface

def createFromTransforms(transforms, degree = 3, direction = 'x',name = "newSurface", spansU = 0, spansV = 0): 
    ''' 
    Build curve from transforms 
    
    Example: 
#        >>> createFromTransforms (["transform1", "transform2"], 1,
"newSurface")
        
        
    @param transforms: Transform object to place point to draw the curve
    @type transforms: *list*
    
    @param degree: degree of the curve, linear or cubic
    @type degree: *int*
    '''
    
    if not isinstance(transforms, list):
        raise RuntimeError, 'There needs to be more then one transform, transforms argument must be a type *list*'
        
    
    #create an empty dictionary for the transform positions
    transform_postitions = dict()
    
    for t in transforms:
        transform_postitions[t] = cmds.xform(t, q = True, ws= True, rp = True)

    #generate the first curve
    curve_one = curve.createFromTransforms (transforms, degree, "tmpCurve1")
    #move curve in the proper direction
    cmds.move(transform.AXES[direction][0], transform.AXES[direction][1], transform.AXES[direction][2], curve_one.name, r=True)
    #generate the first curve
    curve_two = curve.createFromTransforms (transforms, degree, "tmpCurve2")
    #move curve in the proper direction
    cmds.move(transform.AXES['-%s' % direction][0], transform.AXES['-%s' % direction][1], transform.AXES['-%s' % direction][2], curve_two.name, r=True)
    
    
    if degree == 3:
        surface = cmds.loft(curve_one.name,curve_two.name,ch=False,ss=0,n=name)[0]
        cmds.rebuildSurface(surface,kr=0,kcp=True)
    elif degree == 1:
        surface = cmds.loft(curve_one.name,curve_two.name,ch=False,ss=0, degree =1, rebuild = True,n=name)[0]
        cmds.rebuildSurface(surface,ch = False, rpo = 1, rt= 0, end = 1, kr = 0, kcp = 0, kc = 0, tol = 0.01, fr = 0, dir = 2, du = degree, dv = degree, su = spansU, sv = spansV) 
        
    #delete curves
    cmds.delete((curve_one.name,curve_two.name))
    
    return surface
    


def skinTwistSurfaces(joints, surface):
    '''
    adds a skinCluster to a surface based on joints

    Example:
    
    .. python::
        skinTwistSurfaces(joints = [joint1, joint2], surface = nurbsPlane1)
    
    @param joints: joints to deform surface
    @type joints: *list*
    
    @param surface: surface to be deformed by joints
    @type surface: *str*        
    '''
    if not isinstance(surface, str):
        if isinstance(surface, unicode):
            surface = str(surface)
        else:
            raise TypeError('%s is not a string. Pass string into argument surface' % surface)
        
    if not common.isValid(surface):
        raise RuntimeError('%s is does not exist in the scene.' % surface)
    
    for jnt in joints:
        if not common.isValid(jnt):
            raise RuntimeError('%s is does not exist in the scene.' % jnt)
    
    #create the skinCluster based on joints and surface 
    skinCluster = cmds.skinCluster(joints,surface,dr=0.1,tsb=True)
    
    #iterate through joints and assign values to cv's on surface so the are bound to a specific joint
    #check surface degree
    surfShape = common.getShape(surface)[0]
    degree = cmds.getAttr('%s.degreeU' %surfShape)
    
    for i in range(0,len(joints)):
        cmds.skinPercent( skinCluster[0], (surface + '.cv[0:%d][%d]' %(degree, i)), transformValue=[(joints[i], 1.0)])
        
    return skinCluster


def closestPointOnNurbsSurface(surface,transform):
    '''
    creates a list of both parameters U and V closest point on a surface
    
    Example:

      ..python:
        closestPointOnNurbsSurface("nurbsPlane1","joint1")
        #Return: {"joint2" : ["joint2A", "joint2B"], "joint3" : ["joint3A", "joint3B"]}

    @param surface: the nurbs surface to use for closest point
    @type surface: *str* 
    
    @param transform: Transform used to find closest point
    @type transform: *str* 
    
    @return: Return both parameters U and V 
    @rtype: *list*
    '''
    #create empty parameters list to stor U and V values
    parameters = []
    
    #create temp xform snap to transform to get world space
    tempTrans = cmds.group(em=True,n='tempTrans')
    
    #move "tempTrans" into position
    cmds.delete(cmds.pointConstraint(transform,tempTrans))
    
    #create closestPoint node
    cpos = cmds.createNode('closestPointOnSurface',n='tempCpos')
    
    #get surf shape
    surfShape = cmds.listRelatives(surface,s=True)[0]
    
    #connect to cpos
    cmds.connectAttr((surfShape + '.worldSpace[0]'),(cpos + '.inputSurface'))
    cmds.connectAttr((tempTrans + '.translate'),(cpos + '.inPosition'))
    
    #get the parameters U and V
    parameterU = cmds.getAttr(cpos + '.parameterU')
    parameterV = cmds.getAttr(cpos + '.parameterV')   
    
    #store "U" and "V" in a list 
    parameters.append(parameterU)
    parameters.append(parameterV)
    
    #delete both nodes used to get information
    cmds.delete(tempTrans,cpos)
    
    return parameters
    

def buildDictClosestPointSurface(surface,transforms = []):
    '''
    creates a list of both parameters U and V closest point on a surface
    
    Example:
    
        ..:python
          buildDictClosestPointSurface("nurbsPlane1",["joint1","joint2", "joint3"])
          {"joint1" : [.658, .129], joint2" : [.951, .297], joint3" : [.211, .897]}

    @param surface: @param surface: the nurbs surface to use for closest point
    @type surface: *str* 
    
    @param transforms: Transform used to find closest point
    @type transforms: *list* 
    
    @return: Return both parameters U and V 
    @rtype: *dict*
    '''	
    #create a dictionary 
    dictClosestPoints = dict()
    
    #iterate through "joints" list and get the 
    #closest point on the surface in both "U" and "V"
    for transform in transforms:
        parameters = closestPointOnNurbsSurface(surface,transform)        
        #place "parameterUV" list as the Value for dictClosestPoints[j]
        dictClosestPoints[transform] = parameters

    return dictClosestPoints


def createFollicle(surface,name, U = 0, V = 0):
    '''
    creates a list of follices
    
    Example:

	..:python
	  createFollicle("nurbsPlane1","l_fr_toe_001_follicle")
	  #Return: l_fr_toe_001_follicle

    @param surface: Nurbs surface to attach follcile to
    @type surface: *str* 
    
    @param name: Name for the follicle
    @type name: *str* 
    
    @param U: U position on the surface to attach follicle
    @type: *int* or *float*
    
    @param V: V position on the surface to attach follicle
    @type: *int* or *float*
    
    @return: Return follicle
    @rtype: *str*
    '''	
    #getting the shape of the "surface"	
    surfShape = cmds.listRelatives(surface,s = True)[0]

    #creates the follicle
    follicle = cmds.createNode('follicle',n = '%s_%s' % (name, common.SHAPE))
    follicleTrans = cmds.listRelatives(follicle,p = True)[0]
    
    #makes the connection from the surface to the follicle
    cmds.connectAttr((surfShape + '.worldMatrix[0]'),(follicle + '.inputWorldMatrix'))
    cmds.connectAttr((surfShape + '.local'),(follicle + '.inputSurface'))
    #setting the attributes to place the follicles in the correct place
    cmds.setAttr((follicle + '.parameterU'),U)        
    cmds.setAttr((follicle + '.parameterV'),V)        
    cmds.connectAttr((follicle + '.outTranslate'),(follicleTrans + '.translate'))
    cmds.connectAttr((follicle + '.outRotate'),(follicleTrans + '.rotate'))
    
    cmds.rename(follicleTrans, name)
   
    return follicle



def createFollicles(surface,names , u = [0], v = [0]):
    '''
    creates follices and returns the list 
    
    Example:

	..:python
	  createFollicle("nurbsPlane1","l_fr_toe_001_follicle")
	  #Return: l_fr_toe_001_follicle

    @param surface: Nurbs surface to attach follcile to
    @type surface: *str*
    
    @param name: Name for the follicle
    @type name: *str* or *list* 
    
    @param U: U position on the surface to attach follicle
    @type: *int* *float* or *list*
    
    @param V: V position on the surface to attach follicle
    @type: *int* *float* or *list*
    
    @return: Return follicles
    @rtype: *list*
    '''	

    if type(names) == str:
        names = [names]

    if type(u) != list:
        u = [u]

    if type(v) != list:
        v = [v]
        cmds.warning('names should be as long as your U or V lists. If not, it will only produce one follicle')

    lengthUV = min(len(u), len(v), len(names))
    
    follicles = []
    
    #getting the shape of the "surface"
    surfShape = cmds.listRelatives(surface,s = True)[0]

    for i in range(0, lengthUV):
        #creates the follicle
        follicle = cmds.createNode('follicle',n = names[i]+'Shape')
        follicles.append(follicle) #appends follicle to "follicles" list
        follicleTrans = cmds.listRelatives(follicle,p = True)[0]
        #makes the connection from the surface to the follicle
        cmds.connectAttr((surfShape + '.worldMatrix[0]'),(follicle + '.inputWorldMatrix'))
        cmds.connectAttr((surfShape + '.local'),(follicle + '.inputSurface'))
        #setting the attributes to place the follicles in the correct place
        cmds.setAttr((follicle + '.parameterU'),u[i])
        cmds.setAttr((follicle + '.parameterV'),v[i])        
        cmds.connectAttr((follicle + '.outTranslate'),(follicleTrans + '.translate'))
        cmds.connectAttr((follicle + '.outRotate'),(follicleTrans + '.rotate'))
        cmds.rename(follicleTrans, names[i])

    return follicles




def getSurfaceInfo(surfaces, information = None): 
    '''
    creates a of the surfaces "information" specified

    information to call:
    *position* *rotateOrder* *jointOrient* *translate* *rotate* *scale* *rotateAxis*

    Example:

	..:python
	getJointInfo("joint1", information = ['position', 'rotateOrder'])
	{'jntDeHeelCMid': {'rotateOrder': 0, 'position': [20.165274536690067, 4.4028129391309898, 25.833476658221134]}}

    @param surfaces: joint or joints to get information from
    @type surfaces: *str* or *list*
    
    @param information: information that will be returned
    @type information: *str* or *list*
    
    @return: Return joint as key and dictionary of information as value
    @rtype: *dict*
    '''   

    surfaceInfoDict = {}    
    #check to see if there was information passed to function
    if not information:
        cmds.error('Must pass one of the following strings into the argument *information*: %s' % (common.listToStringArray(INFORMATION)))	
    #check to make sure user passed information as a list	
    if type(information) == str:
        if ',' in information:
            information = information.split(',')
            
    if type(information) != list:
        information = [information]

    if isinstance (surfaces, str):
        surfaces = [surfaces]

    
    for surface in surfaces:
        surfaceInfo = {}
        for i in range(0, len(information)):
            if information[i] in INFORMATION:
                if information[i] == 'position':
                    surfaceInfo[information[i]] = cmds.xform(surface,q = True, rp = True, ws = True)
                else:
                    surfaceInfo[information[i]] = mel.eval('nurbsPlane -q -%s %s' % (information[i],surface))
 
        surfaceInfoDict[surface] = surfaceInfo
     
     
    return surfaceInfoDict


def writeSurfaceInfo(surfaces, filePath, component = None, information = None):
    '''
    Write joint information file with json encoding  

    Example:

	..:python:
	  (joints = ("l_fr_toeA_001_sk_jnt","l_fr_toeA_002_sk_jnt"), component = 'youngTembo', filePath = "/sl/shows/TEMBOTEST/user/work.wyoder/scripts/test", information = ['position','rotateOrder', 'translate', 'rotate', 'jointOrient'])

    information:
        *position* *rotateOrder* *jointOrient* *translate* *rotate* *scale* *rotateAxis*

    @param surfaces: surface or surfaces to get information from
    @type surfaces: *str* or *list*

    @param filePath: file path and name of file
    @type filePath: *str* 
    
    @param information: information that will be returned
    @type information: *str* or *list*
    
    @param dict: information that will be returned
    @type dict: *str* or *list*
    '''   
    if not information:
        information = INFORMATION
        
    surfaceInfoDict = getSurfaceInfo(surfaces,information)
    jsonData.writeDicts(filePath, surfaceInfoDict)


def readSurfaceInfo(filePath):
    dataDict = jsonData.readDicts(filePath)
    surfaces = []
    for surface in dataDict:
        surfaces.append(surface)
        cmds.select(cl = True)
        cmds.nurbsPlane(name = surface,ch = 1)
        for key in dataDict[surface].keys():
            # '''
            # if isinstance(dataDict[key], list):
            #     dataDict[key] = common.ddcommon.listToStringArray(dataDict[key])
            # '''
            if isinstance(dataDict[surface][key], list):
                if key == 'position':
                    cmds.setAttr('%s.translate' % (surface), dataDict[surface][key][0], dataDict[surface][key][1], dataDict[surface][key][2])
                    continue
                else:
                    mel.eval('nurbsPlane -e -%s %s %s %s %s' % (key, str(dataDict[surface][key][0]), str(dataDict[surface][key][1]), str(dataDict[surface][key][2]), surface))
                    continue
                
            mel.eval('nurbsPlane -e -%s %f %s' % (key, dataDict[surface][key], surface))

    return dataDict
