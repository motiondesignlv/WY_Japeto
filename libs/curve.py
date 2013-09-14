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
import japeto

common   = japeto.importModule('libs.common', True)

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