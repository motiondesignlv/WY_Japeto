'''
This is the deformer module for all the deformer utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: Decmeber 2012
'''

# """
# #importing python modules
# import sys
# import os
#
# #import maya modules
# import maya.cmds as cmds
# import maya.mel as mel
# import maya.OpenMaya as api
#
# #import package modules
# import japeto
# from japeto import plugins
# reload(plugins)
#
#
# #distribute plug-ins
# plugins.distributePlugin(os.path.join(japeto.__path__[0], 'plugins/cvShapeInverter/src/cvShapeInverter.py'))
# #load plug-ins
# cmds.loadPlugin( 'cvShapeInverter.py',qt = True)
#
#
# #import deformer libs
#
# import cvShapeInverter
#
# def createTarget(original, name = None):
# 	'''
# 	takes skinned geometry and creates a target shape
# 	@param original: original skinned geometry
# 	@type original: *str*
# 	'''
# 	#check original node type to make sure it is of type mesh
# 	if cmds.nodeType(original) == 'mesh':
# 		original = cmds.listRelatives(original, p = True)[0]
# 	#end if
# 	elif not cmds.nodeType(original) == 'mesh':
# 		shapes = cmds.listRelatives(original, c = True, shapes = True)
# 		if not cmds.nodeType(shapes[0]) == 'mesh':
# 			raise TypeError('%s is not a *mesh* nodeType' % original)
# 		#end if
# 	#end elif
# 	#check name to see if it is
# 	if not name:
# 		name = '%s_target' % original
# 	#end if
#
# 	#process for creating target
# 	target = cmds.duplicate(original, name = name)[0]
# 	targetParent = cmds.listRelatives(target, p = True)
# 	if targetParent:
# 		cmds.parent(target, world = True)
# 	#set visibility for both shape and original
# 	cmds.setAttr('%s.v' % original, 0)
#
# 	return target
#
#
# def invertBlend(original, target):
# 	'''
# 	Takes a scultped shape in pose and inverts the shape and applies it as a blendshape
# 	@param original: original skinned geometry
# 	@type original: *str*
# 	@param target: target blendshape to invert
# 	@type target:
# 	'''
# 	#blendshape group name variable
# 	blendShapeGrp = 'blendShapes'
#
# 	#make selection for shape inverter
# 	cmds.select(original, r = True)
# 	cmds.select(target, add = True)
#
# 	#create inverted pose to use as blend shape
# 	invertedTarget = cvShapeInverter.invert()
#
# 	#delete target
# 	cmds.delete(target)
#
# 	#if a blendShape group does not exist, create one
# 	if not cmds.objExists(blendShapeGrp):
# 		cmds.createNode('transform', n = blendShapeGrp)
#
# 	cmds.xform(invertedTarget, ws = True, r = True, t = [10, 0 ,0])
# 	cmds.setAttr('%s.v' % original, 1)
# 	cmds.parent(invertedTarget, blendShapeGrp)
# """