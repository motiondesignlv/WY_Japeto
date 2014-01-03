'''
This is the curve module for all the curve utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#import maya modules
from maya import cmds
from maya import OpenMaya

#import package modules
from japeto.libs import common
from japeto.libs import node

class Curve(node.Node):
    def __init__(self, name = str(), **kwargs):
        super(Curve, self).__init__(name, **kwargs)

        self.__cvPositions  = list()
        self.__cvs          = list()
        #self.__curve        = 
    
    @property
    def cvs(self):
        if not self._fullPathName and not self._name:
            return list()
        if not self._fullPathName and self._name:
            self.fullPathName
        #end if
        self.cvs = getCVs(self._fullPathName)
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


    @property
    def curve(self):
        pass

    #---------------
    #SETTERS
    #---------------
    @cvs.setter
    def cvs(self, value):
        cvList = common.toList(value)
        self.__cvs = cvList



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

def getParamFromPosition(curve, point):
    '''
    Gets a curves parameter value from a position or object in space
    
    @param curve: Curve you want to get paremter for
    @type curve: *str* or *MObject*
    
    @param point: Point in space or Node to get MPoint from
    @type: *list* or *MPoint* or **    
    '''
    #get dag path for curve and assign it a nurbsCurve function object 
    dagPath = common.getDagPath(curve)
    mFnNurbsCurve = OpenMaya.MFnNurbsCurve(dagPath)
    
    #Check to see if point is a list or tuple object
    if not isinstance(point, list) and not isinstance(point, tuple):
        if cmds.objExists(point):
            point = cmds.xform(point, q = True, ws = True, t = True)
        #end if
    #end if
    
    #Get and MPoint object and a double ptr
    mPoint = OpenMaya.MPoint(point[0], point[1], point[2])
    mDoubleUtil = OpenMaya.MScriptUtil()
    mDoubleUtil.createFromDouble(0.0)
    mDoublePtr = mDoubleUtil.asDoublePtr()
    
    #get the value from the point in space and assign it to the double pointer
    mFnNurbsCurve.getParamAtPoint(mPoint,mDoublePtr)

    return mDoubleUtil.getDouble(mDoublePtr) #return value from double pointer
