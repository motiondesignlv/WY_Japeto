'''
This is the control module for all the control utility functions

:author: Walter Yoder
:contact: walteryoder:gmail.com
:date: October 2012
'''

#import python packages
import os

#import maya modules
import maya.cmds as cmds
import maya.mel as mel

#import package modules
from japeto.libs import common
from japeto.libs import transform
from japeto.libs import pyon
from japeto.libs import curve
from japeto.libs import attribute
from japeto.libs import fileIO

CONTROL_FILEPATH  = os.path.join(os.path.dirname(__file__), 'control.pyon')


class Control(object):
    def __init__(self, node = str()):
        self.__control = node
        self.__fullPathName = str()
    
    
    #------------------
    #GETTERS
    #------------------    
    @property
    def name(self):
        return self.__control

    @property
    def fullPathName(self):
        return self.__fullPathName
    
    
    #------------------
    #SETTERS
    #------------------    


def create(name, type = 'circle', parent = None, color = 'yellow'):
    data = pyon.load(CONTROL_FILEPATH)
    #create zero group for the control
    zeroGrp = cmds.createNode('transform', n = '%s_%s' % (name, common.ZERO))
    ctrl = cmds.createNode('joint', n = '%s_%s' % (name, common.CONTROL))
    cmds.parent(ctrl, zeroGrp) #parent control to the zero group
    tag_as_control(ctrl) #tag the control

    #set draw style for the joint to be None
    cmds.setAttr('%s.drawStyle' % ctrl, 2)

    for node in data:
        if type == node:
            for i, shape in enumerate(data[node]['shapes']):
                if i > 0:
                    shapeName = '%s%s' % (name, i)
                else:
                    shapeName = name
                #create the curve for the control
                crv = curve.createFromPoints(data[node]['shapes'][shape]['cvPosition'],
                    degree = data[node]['shapes'][shape]['degree'],
                    name = shapeName)

                crvShape = common.getShapes(crv)[0]#find the shape
                #parent the shape to the transform
                cmds.parent(crvShape, ctrl, s =True, r = True)
                common.setColor(crvShape, color)
                cmds.delete(crv)

    if parent:
        cmds.parent(zeroGrp, parent)

    return ctrl

def createSetup(name, type = 'circle', parent = None):
    #import data
    data = pyon.load(CONTROL_FILEPATH)
    #create zero group for the control
    zeroGrp = cmds.createNode('transform', n = '%s_%s' % (name, common.ZERO))
    ctrl = cmds.createNode('transform', n = '%s_%s' % (name, common.GUIDES))
    cmds.parent(ctrl, zeroGrp) #parent control to the zero group
    tag_as_control(ctrl) #tag the control

    for node in data:
        if type == node:
            for i, shape in enumerate(data[node]['shapes']):
                #create the curve for the control
                crv = curve.createFromPoints(data[node]['shapes'][shape]['cvPosition'],
                         degree = data[node]['shapes'][shape]['degree'],
                         name = '%s%s' % (name,i))
                crvShape = common.getShapes(crv)[0]#find the shape
                #parent the shape to the transform
                cmds.parent(crvShape, ctrl, s =True, r = True)
                cmds.delete(crv)


    return ctrl


def createTemplate(ctrl, defaultType = 'circle'):
    #import data
    data = pyon.load(CONTROL_FILEPATH)

    #declare variables
    enumValue = str()
    conditionNodes = list()
    attrValue = 0

    #loop though data from control file
    for i,node in enumerate(data):
        if defaultType:
            if defaultType == node:
                attrValue = i
        #create attribute names
        if enumValue:
            enumValue = '%s:%s' % (enumValue,node)
        else:
            enumValue = '%s:' % node
        #for each control, create condition nodes for
        if data[node]['shapes']:
            condition = cmds.createNode('condition',
                                        n = '%s_%s_%s' % (ctrl,node,common.CONDITION))
            cmds.setAttr('%s.colorIfTrueR' % condition, 1)
            cmds.setAttr('%s.colorIfFalseR' % condition, 0)
            conditionNodes.append(condition)

        for i, shape in enumerate(data[node]['shapes']):
            #create the curve for the control
            crv = curve.createFromPoints(data[node]['shapes'][shape]['cvPosition'],
                degree = data[node]['shapes'][shape]['degree'],
                name = '%s_%s%s' % (ctrl,node,i))
            crvShape = common.getShapes(crv)[0]#find the shape
            #parent the shape to the transform
            cmds.parent(crvShape, ctrl, s =True, r = True)
            cmds.delete(crv)
            attribute.connect('%s.outColorR' % condition, '%s.v' % crvShape)
            cmds.setAttr('%s.overrideEnabled' % crvShape, 1)
            cmds.setAttr('%s.overrideDisplayType' % crvShape, 1)
            #hide history on shapes
            common.hideHistory(crvShape)

    #create and connect attibutes for controls
    shapeAttr = attribute.addAttr(ctrl,
            'controlShape',
            attrType = 'enum',
            defValue = enumValue,
            value = attrValue)
    for i in range(len(conditionNodes)):
        print conditionNodes[i]
        cmds.setAttr('%s.secondTerm' % conditionNodes[i], i)
        attribute.connect(shapeAttr, '%s.firstTerm' % conditionNodes[i])

    #hide history on controls
    common.hideHistory(ctrl)


    return ctrl

def displayLine(point1, point2, name = 'ctrlLine#', parent = str()):
    '''
    Create a display line between two points

    Example:
    ..python
        displayLine('l_uparm_sc_jnt', 'l_uparm_pv_ctrl')
        #Return: 'ctrlLine1'

        displayLine('l_uparm_sc_jnt', 'l_uparm_pv_ctrl', name = 'l_uparm_pv_displayLine')
        #Return: 'l_uparm_pv_displayLine'

    @param point1: First node to connect display line to
    @type point1: *str*

    @param point2: Second node to connect display line to
    @type point2: *str*

    @return: Display line
    @rtype: *str*

    '''
    #get posiitons of first and second points
    pnt1 = cmds.xform(point1, q =True, ws = True, t = True)
    pnt2 = cmds.xform(point2, q =True, ws = True, t = True)

    #create a pointList from point1 and point2 positions
    pointList = (pnt1,pnt2)

    #create display line from pointList
    displayLine = curve.createFromPoints(pointList, degree = 1, name = name)

    #cluster the two ends of the dispay line to point1 and point2
    cmds.cluster( '%s.cv[0]' % displayLine,
            wn = [point1,point1],
            bs = True,
            name = '%s_1_%s' % (displayLine, common.CLUSTER))

    cmds.cluster('%s.cv[1]' % displayLine,
            wn = [point2,point2],
            bs = True,
            name = '%s_2_%s' % (displayLine, common.CLUSTER))

    #override display type of displayLine to be templated
    cmds.setAttr('%s.overrideEnabled' % displayLine, 1)
    cmds.setAttr('%s.overrideDisplayType' % displayLine, 1)
    cmds.setAttr('%s.inheritsTransform' % displayLine, 0)

    if parent:
        cmds.parent(displayLine, parent)

    return displayLine


def save(controls, filepath = None, append = True):
    '''
    Save out control information to a pyon file

    Example:
      ..python::
        save('l_foot_ik_ctrl', '/home/wyoder/Documents/maya/scripts/controls/controls.pyon')
        :Return: '/home/wyoder/Documents/maya/scripts/controls/controls.pyon'

    @param controls: Controls to export
    @type controls: *str* or *list*

    @param filepath: Filepath to export data to
    @type filepath: *str*

    @param append: Whether to append controls to an existing file
    @type append: *bool*

    @return: Filepath controls were exported to
    @rtype: *str*
    '''

    data = dict()

    #if Append, check to see if file exist
    #if it exist, load it as data to append controls to
    if append:
        if fileIO.isFile(filepath):
            data = pyon.load(filepath)
    #check to see if controls is a proper data type
    if isinstance(controls, basestring):
        controls = [controls]
    if not isinstance(controls, list):
        raise TypeError('%s is not of type list()' % controls)

    for ctrl in controls:
        data[ctrl] = dict()
        shapes = common.getShapes(ctrl)
        if shapes:
            data[ctrl]['shapes'] = dict()
            for shape in shapes:
                if cmds.nodeType(shape) == 'nurbsCurve':
                    data[ctrl]['shapes'][shape] = dict()
                    data[ctrl]['shapes'][shape]['degree'] = cmds.getAttr('%s.degree' % shape)
                    data[ctrl]['shapes'][shape]['color'] = cmds.getAttr('%s.overrideColor' % shape)
                    cvs = curve.getCVs(shape) #delete the curve
                    data[ctrl]['shapes'][shape]['cvPosition'] = curve.getCVpositions(cvs)


    return pyon.save(data, filepath)


def load(filepath, name = None, type = 'circle'):

    data = pyon.load(filepath)

    for ctrl in data:
        if cmds.objExists(ctrl):
            if data[ctrl]:
                for key in data[ctrl]:
                    if 'shapes' in key:
                        if data[ctrl][key]:
                            for shape in data[ctrl][key]:
                                if not name:
                                    curve.createFromPoints(data[ctrl][key][shape]['cvPosition'],
                                            degree = data[ctrl][key][shape]['degree'],
                                            name = ctrl)
                                else:
                                    curve.createFromPoints(data[ctrl][key][shape]['cvPosition'],
                                            degree = data[ctrl][key][shape]['degree'],
                                            name = name)

        else:
            if type in ctrl:
                if name:
                    create(name = name, type = type)
                else:
                    create(name = ctrl, type = type)

    return data

def tag_as_control(control):
    '''
    @param control: node to tag as a control
    @type control: *str* or *list*
    '''
    if not isinstance(control, list):
        if not isinstance(control, basestring):
            raise TypeError('%s must be of type *str*, *unicode*, or *list*' % ctrl)
        ctrls = common.toList(control)
    else:
        ctrls = common.toList(control)

    for ctrl in ctrls:
        tagAttr = attribute.addAttr(ctrl, 'tag_controls', attrType = 'message')

    return tagAttr


def getControls(asset = None):
    '''
    Gets all controls connect to an asset or every control in the scene depending on user input

    @param asset: Asset you wish to look for controls on
    @type asset: *str*

    @return: List of controls
    @rtype: *list*
    '''
    controls = None
    if not asset:
        controls = cmds.ls('*.tag_controls', fl = True)
    elif asset:
        controls = attribute.getConnections('%s.tag_controls' % asset,
                incoming = False,
                plugs = False)

    if controls:
        return controls

    return None

#shapes
#-----------------------
def translateShape (ctrl,
        translation = transform.ZERO,
        index = 0 ,
        world = False):
    '''
    Rotate control shape

    @param ctrl: Animation control
    @type ctrl: *str*

    @param translation: Translation vector
    @type translation: *list*

    @param index: Shape index
    @type index: *int*
    '''
    # Get control shape
    shape = getShape (ctrl, index)

    # Translate shape
    if world:
        cmds.move (translation [0],
                translation [1],
                translation [2],
                curve.getCVs (shape),
                relative = True,
                worldSpace = True)
    else:
        cmds.move (translation [0],
                translation [1],
                translation [2],
                curve.getCVs (shape),
                relative = True,
                objectSpace = True)

def rotateShape (ctrl, rotation = transform.ZERO, index = 0):
    '''
    Rotate control shape

    @param ctrl: Animation control
    @type ctrl: *str*

    @param rotation: Rotation vector
    @type rotation: *list*

    @param index: Shape index
    @type index: *int*
    '''
    # Get control shape
    shape = getShapes(ctrl, index)

    # Rotate shape
    cmds.rotate (rotation [0],
            rotation [1],
            rotation [2],
            curve.getCVs (shape),
            relative = True,
            objectSpace = True)

def scaleShape (ctrl, scale = [1, 1, 1], index = 0):
    '''
    Rotate control shape

    @param ctrl: Animation control
    @type ctrl: *str*

    @param scale: Scale vector
    @type scale: *list*

    @param index: Shape index
    @type index: *int*
    '''
    # Get control shape
    shape = getShape (ctrl, index)

    # Scale shape
    cmds.scale (scale [0],
            scale [1],
            scale [2],
            curve.getCVs (shape),
            relative = True )

def getShape(ctrl, index = 0):
    '''
    gets shape based on index

    @param ctrl: Control you wish to get shape on
    @type ctrl: *str*

    @param index: Index of the shape on the control
    @type index: *int*
    '''
    #get shapes
    shapes = common.getShapes(ctrl)

    #return shape based off of index
    if shapes:
        return shapes[index]

    return None