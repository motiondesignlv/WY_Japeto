'''
This is the curve module for all the curve utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#import maya modules
import maya.cmds as cmds
import maya.mel as mel

#import package modules
from japeto.libs import common

class Curve(object):
    def __init__(self, name = str()):
        self.__name         = name
        self.__fullPathName = str()
        self.__cvPositions  = list()
        self.__cvs          = list()
    
    
    #---------------
    #GETTERS
    #---------------
    @property    
    def name(self):
        return self.__name
    
    @property
    def fullPathName(self):
        if self.__name:
            self.__fullPathName = common.fullPathName(self.__name)
            #end if
        #end if
                
        return self.__fullPathName
    
    @property
    def cvs(self):
        if not self.__fullPathName and not self.__name:
            return list()
        if not self.__fullPathName and self.__name:
            self.fullPathName
        #end if
        self.cvs = cmds.ls('%s.cv[*]' % self.__fullPathName, flatten = True)
        return self.__cvs
        
    @property
    def cvPositions(self):
        cvList = self.cvs
        
        if cvList:
            for cv in cvList:
                point = cmds.xform(cv, q = True, ws = True, t = True)
                self.__cvPositions.append(point)
            #end loop
        #end if

        return self.__cvPositions

    #---------------
    #SETTERS
    #---------------
    @cvs.setter
    def cvs(self, value):
        cvList = common.toList(value)
        self.__cvs = cvList
        
    @name.setter
    def name(self, value):
        if not isinstance(value, basestring):
            raise ValueError('%s must be a *str* or *unicode* object' % value)
        #end if
        
        if self.__name:
            if cmds.objExists(self.__name):
                cmds.rename(self.__name, value)
            #end if
        #end if
        
        self.__name = value
        self.__fullPathName = common.fullPathName(self.__name)
        
    def delete(self):
        if cmds.objExists(self.fullPathName):
            cmds.delete(self.fullPathName)
            


#----------------------------------------------------
# get information functions
def getCVs(curve):
    return cmds.ls('%s.cv[*]' % curve, flatten = True)
    
    
def getCVpositions(pointList):
	positions = list()
	
	for point in pointList:
		ws = cmds.xform(point, q = True, ws = True, t = True)
		positions.append(ws)
	
	return positions
	
#----------------------------------------------------
# Create functions
def createFromPoints(points, degree = 1, name = 'curve#'):
    knotList = [0]
    
    if degree == 1:
        knotList.extend(range(1, len(points)))
    if degree == 3:
        knotList.extend([0])
        knotList.extend(range(len(points) - 2))
        knotList.extend([knotList[-1], knotList[-1]])


    curve = cmds.curve (degree = degree, point = points, knot = knotList)
    curve = cmds.rename (curve, name)
    
    return curve

def createFromTransforms(transforms, degree = 1, name = 'curve#'):
    '''
    Creates a curve from transforms
    Example:
        ...createFromTransforms(['joint1', 'joint2', 'joint3'])
        #return 
    
    '''
    points = list()
    
    for transform in transforms:
        points.append(cmds.xform(transform, q = True, ws = True, rp = True))

    curve = createFromPoints(points, degree, name)

    return Curve(curve)