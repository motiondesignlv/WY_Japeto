'''
This is the common module for all the common utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#importing python modules
import sys

#import maya modules
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya

#import package modules

#Constant variables
#-------------------



#Set up for naming convention constant variables
#  Example:
#    side_location(optional)_description_###(optional)_class(optional)_type

NAMETEMPLATE = 'side.location.description.number.type.function'
DELIMITER    = '_'

#side constants
LEFT   = 'l'
RIGHT  = 'r'
CENTER = 'c'

SIDES   = {"left" : LEFT, "right" : RIGHT,
            "center" : CENTER}

#location constants
FRONT   = 'fr'
BACK    = 'bk'
MIDDLE  = 'md'
TOP     = 'tp'
BOTTOM  = 'bt'

LOCATIONS = {'front' : FRONT, 'back' : BACK, 'middle' : MIDDLE,
         'top': TOP, 'bottom' : BOTTOM}

#Class constants
IK                = "ik"
FK                = "fk"
SKELETON          = "sk"
SKINCLUSTER       = "sc"
SIMULATION        = "sim"
SKINMUSCLE        = "sam"
DRIVER            = "drv"
PSD               = "psd"
SURFACE           = "srf"
CLUSTER           = "cluster"
WIRE              = "wire"
BLEND             = "blend"
LATTICE           = "lattice"
BEND              = "bend"
CURVE             = "crv"
GUIDES 		      = 'guide'
POLYGON           = "mesh"
NURBS             = "nurbs"
ANCHOR            = "anchor"
ROOT              = "root"
PARENTCONSTRAINT  = "parentConstraint"
POINTCONSTRAINT   = "pointConstraint"
POINTONCURVEINFO  = "pointOnCurveInfo"
ORIENTCONSTRAINT  = "orientConstraint"
AIMCONSTRAINT     = "aimConstraint"
PAIRBLEND         = "pairBlend"
FOLLICLE          = "follicle"
MULTIPLYDIVIDE    = "multiplyDivide"
MULTDOUBLELINEAR  = "multDoubleLinear"
PLUSMINUSAVERAGE  = "plusMinusAverage"
CURVEINFO         = "curveInfo"
DISTANCEBETWEEN   = "distanceBetween"
VECTORPRODUCT     = "vpn"
DECOMPOSEROTATION = "dcr"
DECOMPOSEMATRIX   = 'dcm'
SPREAD            = "spread"
SCALE             = "scale"
ROTATE            = "rotate"
TRANSLATE         = "translate"
REMAP             = "remap"
PIVOT             = "pivot"
PIN               = "pin"
REVERSE           = "reverse"
TWEAK             = "twk"
SETRANGE          = "setRange"
UPOBJECT          = "upObject"
TARGET            = "tgt"
TWIST             = "twst"
POLEVECTOR        = "pv"
GIMBAL            = "gimbal"
CONDITION         = "condition"
SET               = "set"
AIM               = 'aim'
UP                = 'up'


#Type constants
ZERO         = "zero"
GEOMETRY     = "geo"
JOINT        = "jnt"
GROUP        = "grp"
LOCATOR      = "loc"
IKHANDLE     = "ikHandle"
EFFECTOR     = "effector"
LOCALCONTROL = "ltrl"
CONTROL      = "ctrl"
DEFORMER     = "def"
HANDLE       = "hdl"
UTILITY      = "util"
MASTER       = "master"
SHAPE        = "shape"
DISPLAYLINE  = "displayLine"



# LOD constants
HI      = "hi"
MEDIUM  = "md"
LOW     = "lo"

LODS = {"hi" : HI, "medium" : MEDIUM, "low" : LOW}


#Naming template variables
DELIMITER = "_"
NAMETEMPLATE  = "SIDE.LOCATION.DESCRIPTION.NUMBER.CLASS.TYPE"
PADDING = 3
REQUIRED = ["SIDE", "DESCRIPTION", "TYPE"]


# Color constants
NONE        = 0;    NONE_RGB        = [0, 0.015, 0.375]
BLACK       = 1;    BLACK_RGB       = [0, 0, 0]
DARKGREY    = 2;    DARKGREY_RGB    = [0.25, 0.25, 0.25] 
GREY        = 3;    GREY_RGB        = [0.5, 0.5, 0.5] 
CERISE      = 4;    CERISE_RGB      = [0.6, 0, 0.157]
DARKBLUE    = 5;    DARKBLUE_RGB    = [0, 0.016, 0.376]
BLUE        = 6;    BLUE_RGB        = [0, 0, 1]
FORESTGREEN = 7;    FORESTGREEN_RGB = [0, 0.275, 0.098]
DARKVIOLET  = 8;    DARKVIOLET_RGB  = [0.149, 0, 0.263]
MAGENTA     = 9;    MAGENTA_RGB     = [0.784, 0, 0.784]
SIENNA      = 10;   SIENNA_RGB      = [0.541, 0.282, 0.2]
BROWN       = 11;   BROWN_RGB       = [0.247, 0.137, 0.122]
DARKRED     = 12;   DARKRED_RGB     = [0.6, 0.149, 0]
RED         = 13;   RED_RGB         = [1, 0, 0]
GREEN       = 14;   GREEN_RGB       = [0, 1, 0]
MIDBLUE     = 15;   MIDBLUE_RGB     = [0, 0.255, 0.6]
WHITE       = 16;   WHITE_RGB       = [1, 1, 1] 
YELLOW      = 17;   YELLOW_RGB      = [1, 1, 0]
CYAN        = 18;   CYAN_RGB        = [0.392, 0.863, 1]
PALEGREEN   = 19;   PALEGREEN_RGB   = [0.263, 1, 0.639]
SALMON      = 20;   SALMON_RGB      = [1, 0.69, 0.69]
MOCCA       = 21;   MOCCA_RGB       = [0.894, 0.675, 0.475]
PALEYELLOW  = 22;   PALEYELLOW_RGB  = [1, 1, 0.388]
SEAGREEN    = 23;   SEAGREEN_RGB    = [0, 0.6, 0.329]
DARKGOLD    = 24;   DARKGOLD_RGB    = [0.631, 0.412, 0.188]
OLIVE       = 25;   OLIVE_RGB       = [0.624, 0.631, 0.188]
LAWNGREEN   = 26;   LAWNGREEN_RGB   = [0.408, 0.631, 0.188]
DARKGREEN   = 27;   DARKGREEN_RGB   = [0.188, 0.631, 0.365]
TURQUOISE   = 28;   TURQUOISE_RGB   = [0.188, 0.631, 0.631]
DODGERBLUE  = 29;   DODGERBLUE_RGB  = [0.188, 0.404, 0.631]
VIOLET      = 30;   VIOLET_RGB      = [0.435, 0.188, 0.631]
DARKPINK    = 31;   DARKPINK_RGB    = [0.631, 0.188, 0.412]

COLORSSTR   = ['none', 'black', 'darkgrey', 'grey', 'cerise', 'darkblue', 'blue',
               'forestgreen', 'darkviolet', 'magenta', 'sienna', 'brown', 'darkred',
               'red', 'green', 'midblue', 'white', 'yellow', 'cyan', 'palegreen',
               'salmon', 'mocca', 'paleyellow', 'seagreen', 'darkgold', 'olive',
               'lawngreen', 'darkgreen', 'turquoise', 'dodgerblue', 'violet', 'darkpink']

COLORSDICTINDEX = dict( (c, eval(c.upper())) for c in COLORSSTR) # dictionary {'colorstring': int}
COLORSDICTRGB   = dict( (c, eval('%s_RGB' % c.upper())) for c in COLORSSTR)

SIDE_COLOR  = {None: NONE, RIGHT: RED, LEFT: BLUE, CENTER: YELLOW}
SIDE_COLOR_SECONDARY  = {None: NONE, RIGHT: SALMON, LEFT: CYAN, CENTER: OLIVE}


# Component constants
VERTEX      = ".vtx"
CV          = ".cv"
EDGE        = ".e"
FACE        = ".f"
COMPONENTS  = {"vertex" : VERTEX, "cv" : CV, "edge" : EDGE, "face" : POLYGON}

# File constants
MB      = ".mb"
MA      = ".ma"
FBX     = ".fbx"
XML     = ".xml"
CLIP    = ".clip"



def padNumber(number, pad):
    '''
    .. python:
        padNumber(2,3)
        #return: '002'

    @param number: number to use
    @type number: *int*

    @param pad: number padding to use (i.e. '3')
    @type pad: *int*

    @return: number string with correct padding
    @rtype: *str*

    '''

    if not isinstance(number, int):
        raise ValueError('%s must be an integer data type' % number)

    if not isinstance(pad, int):
        raise ValueError('%s must be an integer data type' % pad)   

    padNumberStr = str(number)
    pad = pad - len(padNumberStr)

    for i in range(pad):
        padNumberStr = '0%s' % padNumberStr 

    return padNumberStr 


def toList(input):
    """
    @param input:
    @type input: object
    """
    if isinstance(input,list):
        return input
    elif isinstance(input,tuple):
        return list(input)    

    return [input]


def isValid(node):
    '''
    checks to see if a node exist in the scene
    Example:
    ..python::
        isValid('l_arm_ctrl')
        #Return: True

    @param node: node to check scene for
    @type node: *str*

    @return: Return True if node exists, false if it does not
    @rtype: *bool*

    '''

    if cmds.objExists(node):
        return True

    return False

def isType(node, type):
    '''
    checks to see if node is of type input
    Example:
    ..python::
        isType('l_arm_ctrlShape', 'nurbsCurve')
        #Return: True

    @param node: node to check scene for
    @type node: *str*

    @param type: type to check node against
    @type type: *str*

    @return: Return True if node is of same type, else return False
    @rtype: *bool*

    '''

    if cmds.nodeType(node) == type:
        return True

    return False

# ------------------------------------------------------------------------------
# Name Functions
def checkName(name, i = 1):
    '''
    Checks if name exists and returns a padded one if it does

    @param name: Name you wish to check for
    @type name: *str*

    @param i: Integer to number the padding with
    @type i: *int*
    '''
    #check to see if *i* is an integer
    if not isinstance(i, int):
        raise TypeError('%s is not of type int()' % i)

    #check name and create a new one if it already exist in the scene
    if isValid(name):
        name = '%s_%s' % (name, padNumber(i, PADDING)) #create the new name using padding
        return checkName(name, i + 1) #recursively create the new name
    #end if

    #return new name
    return name


def searchReplaceRename(name, search = str(), replace = ()):
    '''
    Try's to replace character in name, if it can't it will ad the characters to the end of the name

    @param name: Name you wish to check for
    @type name: *str*

    @param search: Characters to search for in the name
    @type search: *str*

    @param replace: Characters to replace the search with in the name
    @type replace: *str*
    '''
    #check if characters are in the name
    if search in name:
        name = name.replace(search, replace)
    else:
        name = '%s%s' % (name, replace)

    return name

def generateName (*args, **kwargs):
    '''
    Example:

    .. python::
    generateName(SIDE = LEFT, DESCRIPTION = "leg", TYPE = GROUP)
    l_leg_grp


    Generate name based on template

    This method requires input of key word arguments that match those of the template.

    *LOCATION* *NUMBER* *CLASS* are optional kwargs.

    @param SIDE: side of character or object
    @type SIDE: *str*

    @param LOCATION: Location on character or object
    @type LOCATION: *str*

    @param DESCRIPTION: Decription of what is being named
    @type DESCRIPTION: *str*

    @param CLASS: class of the object being named... ex.(ik, fk, etc...)
    @type CLASS: *str*

    @param TYPE: Type of the object being named... ex.(jnt, grp, etc...)
    @type TYPE: *str*

    @return: Return new name
    @rtype: *str*
    '''

    # Get template order
    order = NAMETEMPLATE.split (".")
    keys = []
    for key in kwargs.keys():
            if key in order:
                    keys.append(key)

    for r in REQUIRED:
            if r not in keys:
                    cmds.error ('Must pass required Kwargs %s' % listToStringArray(REQUIRED))	

    try:          
        newName = ""      
        for i in range(0, len(order)):
            if kwargs.has_key(order[i]):      
                if i == len(order) - 1:
                    newName = "%s%s" % (newName, kwargs[order[i]]) 
                else:                           
                    # Check for padding			
                    if order[i] == "NUMBER":
                        number = str(kwargs[order[i]])
                        newName = "%s%s" % (newName, padNumber(number, PADDING) + DELIMITER)
                        continue
                    newName = "%s%s" % (newName, kwargs[order[i]] + DELIMITER)
    except:
        cmds.error("Please provide the correct kwargs for the name generator!\ncorrect kwargs are: %s" % str(order)) 

    # Return new name
    return newName



def getSide(name):
    '''
    Get a possible side reference from object name

    Example:

    .. python::
        # Get side token from name
        getSide ("l_fr_leg_001_ik_ctrl")
        "l"

    :note: Valid side tokens defined in SIDES constant variable
    :note: The search pattern goes start > end

    @param name: Object name
    @type name: *str*

    @return: Return side if found
    @rtype: *str*
    '''
    if isinstance(name, unicode):
        name = str(name)
    
    print name
    
    if not isinstance(name, basestring):
        raise RuntimeError('%s can only be passed as a string argument!' % name)

    nameList = name.split(DELIMITER)

    # Loop through side tokens

    for key in SIDES:

        # Search for side token
        for name in nameList:
            if SIDES[key] == name:
                return SIDES[key]

    # Return None
    return None    

def getLocation(name):
    '''
    Get a possible location reference from object name

    Example:

    .. python::
        # Get side token from name
        getLocation ("l_fr_leg_001_ik_ctrl")
        "fr"

    :note: Valid location tokens defined in LOCATIONS constant variable
    :note: The search pattern goes start > end

    @param name: Object name
    @type name: *str*

    @return: Return side if found
    @rtype: *str*
    '''
    if isinstance(name, unicode):
        name = str(name)

    if not isinstance(name, str):
        raise RuntimeError, '*name* can only be passed as a string argument!'

    nameList = name.split(DELIMITER)

    # Loop through side tokens

    for key in LOCATIONS:             
        # Search for side token
        for name in nameList:
            if LOCATIONS[key] == name:
                return LOCATIONS[key]

    # Return None
    return None        

def getDescription(name):
    '''
    Get a possible description reference from object name

    Example:

    .. python::
        # Get description token from name
        getSide ("l_fr_leg_001_ik_ctrl")
        "leg"

    :note: Valid side tokens defined in SIDES constant variable
    :note: The search pattern goes start > end

    @param name: Object name
    @type name: *str*

    @return: Return side if found
    @rtype: *str*
    '''
    if isinstance(name, unicode):
        name = str(name)

    if not isinstance(name, str):
        raise RuntimeError, '*name* can only be passed as a string argument!'

    nameList = name.split(DELIMITER)

    for key in LOCATIONS:
        if LOCATIONS[key] in nameList:
            index = nameList.index(LOCATIONS[key])
            return nameList[index+1]

    # Return None
    return nameList[1]


def getNumber(name):
    '''
    Get a possible Number reference from object name

    Example:

    .. python::
        # Get Number token from name
        getSide ("l_fr_leg_001_ik_ctrl")
        "001"

    :note: Valid side tokens defined in SIDES constant variable
    :note: The search pattern goes start > end

    @param name: Object name
    @type name: *str*

    @return: Return side if found
    @rtype: *str*
    '''
    if isinstance(name, unicode):
        name = str(name)

    if not isinstance(name, str):
        raise RuntimeError, '*name* can only be passed as a string argument!'

    nameList = name.split(DELIMITER)

    for string in nameList:
        if string.isdigit():
            number = string
            return number

    # Return None
    return None


def getClass(name):
    '''
    Get a possible CLASS reference from object name

    Example:

    .. python::
        # Get CLASS token from name
        getClass ("l_fr_leg_001_ik_ctrl")
        "ik"

    :note: Valid side tokens defined in SIDES constant variable
    :note: The search pattern goes start > end

    @param name: Object name
    @type name: *str*

    @return: Return side if found
    @rtype: *str*
    '''

    nameList = name.split(DELIMITER)

    location = getLocation(name)
    number = getNumber(name)
    description = getDescription(name)

    if number and location and len(nameList) == 6:
        index = nameList.index(number)
        return nameList[index+1]

    if number and not location and len(nameList) == 5:
        index = nameList.index(number)
        return nameList[index+1]

    if not number and location and len(nameList) == 5:
        index = nameList.index(location)
        return nameList[index+2]

    if not number and not location and len(nameList) == 4:
        index = nameList.index(description)
        return nameList[index+1]

    # Return None
    return None


def getNameType(name):
    '''
    Get a possible TYPE reference from object name

    Example:

    .. python::
        # Get TYPE token from name
        getClass ("l_fr_leg_001_ik_ctrl")
        "ik"

    :note: Valid side tokens defined in SIDES constant variable
    :note: The search pattern goes start > end

    @param name: Object name
    @type name: *str*

    @return: Return side if found
    @rtype: *str*
    '''

    nameList = name.split(DELIMITER)

    side = getSide(name)
    description = getDescription(name)

    if side and description:
        return nameList[-1]

    # Return None
    return None


def removeCharsFromString(name, chars):
    '''
    Example:

      python::
          removeCharsFromString("joint1", "in")
      "jot1"

    Returns a name striping out the characters entered in second argument "chars"

    This method requires arguments of the "name" and "chars"

    *LOCATION* *NUMBER* *CLASS* are optional kwargs.

    @param name: string to be stripped
    @type name: *str*

    @param chars: characters to be stripped from string 
    @type chars: *str*

    @return: Return new name
    @rtype: *str*
    '''    
    newNameList = name.split(chars)
    newName = ""
    for name in newNameList:
        newName = '%s%s' % (newName, name)

    return newName



# ------------------------------------------------------------------------------
# Display Override Functions

def getColorIndexFromRgb(rgb):
    for s, rgbvalue in COLORSDICTRGB.items():
        if rgb == rgbvalue:
            return COLORSDICTINDEX[s]

def getColorRgbFromIndex(index):
    for s, i in COLORSDICTINDEX.items():
        if i == index:
            return COLORSDICTRGB[s]


def setColor(node, color):
    '''
    Set wireframe color on object

    Example:

    .. python::

        setColor ("null1", "red")

    @param node: Object to set color for
    @type node: *str*

    @param color: Color to use, string or int(transforms) 
    @type color: *str* or *int* or *[float, float, float]*
    '''
    try:
        color = color.lower()
    except:
        pass
    msg = "'%s' is not a valid color. Use maya color index, rgb or a color name. \n%s\nValid color names : %s" % (color, '='*88, COLORSSTR)

    # Check if the control is a transform or a ddController
    ntype = cmds.nodeType(node)
    if ntype in ['transform', 'joint', 'nurbsSurface', 'nurbsCurve','implicitSphere']:
        # Check color input
        if isinstance(color, int):
            colorInt = color
        elif isinstance(color, basestring):
            # Check for valid color
            if color in COLORSDICTINDEX:
                colorInt = COLORSDICTINDEX[color]
            else:
                raise ValueError(msg)
        elif isinstance(color, list):
            colorInt = getColorIndexFromRgb(color) or None
            if not colorInt:
                raise ValueError(msg)
        else:
            raise TypeError(msg)

        # Set color override)
        cmds.setAttr (node + ".overrideEnabled", 1)
        cmds.setAttr (node + ".overrideShading", 0)
        cmds.setAttr (node + ".overrideColor", colorInt)


def setDisplayType(node, displayType = 'normal'):
    '''
    sets the display type based on displayType Attribute
    Example:
    ..pythoon:
        setDisplayType('l_upArm_jnt', displayType = 'reference')

    @param node: node to set display type on
    @type node: *str*

    @param displayType: type of display to make node
        ('normal', 'reference', 'template')
    @type displayType: *str* or *int*
    '''
    cmds.setAttr ('%s.overrideEnabled' % node, True)

    if isinstance(displayType,int):
        cmds.setAttr('%s.overrideDisplayType', displayType)
        return

    if displayType.lower() == 'reference':
        cmds.setAttr('%s.overrideDisplayType' % node, 2)
    elif displayType.lower() == 'normal':
        cmds.setAttr('%s.overrideDisplayType' % node, 0)
    elif displayType.lower() == 'template':
        cmds.setAttr('%s.overrideDisplayType' % node, 1)



# ------------------------------------------------------------------------------
# Hierarchy functions

def getTopNode(node):
    '''
    gets the top node of the hiearchy

    @param node: node to start from
    @type node: *str*
    '''
    if isinstance(node, unicode):
	node = str(node)

    if not isinstance(node, str):
	raise RuntimeError, '*node* can only be passed as a string argument!'

    topNode = mel.eval('rootOf("%s")'% node)
    if topNode:
	return topNode.strip('|')
    else:
	return node


def getParent(node):
    parent = cmds.listRelatives(node, p = True)

    if parent:
        return parent[0]

    return None


def getChildren(node):
    children = cmds.listRelatives(node, c = True)

    if children:
        return children

    return None


def getShapes(node, index = None):
    if cmds.nodeType(node) in ['nurbsCurve', 'mesh', 'nurbsSurface']:
        return node
    
    shapes = cmds.listRelatives(node, c = True, shapes = True)

    if shapes:
        if isinstance(index, int):
           return shapes[index]
        return shapes


    return None


def duplicate(node, name = None, parent = None):
    #duplicate node
    if name:
        dupNode = cmds.duplicate(node, parentOnly = True, name = name)[0]
    else:
        dupNode = cmds.duplicate(node, parentOnly = True)[0]

    if parent:
        if not getParent(node) == parent:
            cmds.parent(dupNode, parent)

    return dupNode

def getInbetweenNodes(startNode, endNode, inbetweenNodes = None):
    '''
    Gets all the nodes inbetween the two given nodes

    @param startNode: Node to start search
    @param startNode: *str*

    @param endNode: Node to end search
    @param endNode: *str*

    @param inbetweenNodes: List to place nodes found in search
    @param inbetweenNodes: *list*

    @return: List of nodes in between start and end node
    @rtype: *tuple*
    '''
    #check if nodes exist
    if not cmds.objExists(startNode) or not cmds.objExists(endNode):
        sys.stderr.write('%s or %s do not exists in the current scene' % (startNode, endNode))
    #end if

    inbetweenNodes = inbetweenNodes[:] if inbetweenNodes else []

    #get parent
    parent = cmds.listRelatives(endNode, p = True)        

    #check for parent
    if parent:
        if parent[0] == startNode:
             return inbetweenNodes

        #Add parent to inbetween node list
        inbetweenNodes.insert(0,parent[0])

        return getInbetweenNodes(startNode, parent[0], inbetweenNodes)	

# ------------------------------------------------------------------------------
# API Functions
def asMObject (node):
    '''
    Get node MObject

    Example:

    .. python::
        asMObject ("null1")

    @param node: Maya node
    @type node: *str*

    @return: Return node object
    @rtype: *MObject*
    '''
    # Get MObject
    mObj = OpenMaya.MObject ()
    sel  = OpenMaya.MSelectionList ()
    try:
        sel.add (node)
        sel.getDependNode (0, mObj)
    except:
        raise RuntimeError, 'No valid node'

    # Return object
    return mObj

def asMDagPath( node ):
    '''Returns MDagPath of given node

    Example:

    .. python::
        toMDagPath ("null1")

    @param node: node name
    @type node: *str*

    @return: Return node dag path
    @rtype: *MDagPath*
    '''

    dpNode = OpenMaya.MDagPath()
    slist  = OpenMaya.MSelectionList()
    try:
        slist.add( node )
        slist.getDagPath( 0, dpNode )
    except:
        raise RuntimeError, 'No valid dag node'

    return dpNode	


def getDagPath(name):
    '''
    Get the dag path for a given name
    '''

    dagPath = OpenMaya.MDagPath()
    mSelList = OpenMaya.MSelectionList()

    try:
        mSelList.add(name)
        mSelList.getDagPath(0,dagPath)
    except:
        raise RuntimeError, 'No valid dag node'

    return dagPath


def getMObject(name):
    '''
    Get the MObject for a given name
    '''

    mobject = OpenMaya.MObject()
    mSelList = OpenMaya.MSelectionList()

    try:
        mSelList.add(name)
        mSelList.getDependNode(0, mobject)
    except:
        raise RuntimeError, 'No valid dag node'

    return mobject

def fullPathName(name):
    dagPath = getDagPath(name)

    return dagPath.fullPathName()   

# ------------------------------------------------------------------------------
# History Editing 

def hideHistory(node):
    '''
    hides connection and shape history from channelbox of a given node

    @param node: node to hide history on
    @type node: *str*
    '''
    inputConnections = cmds.listConnections(node, destination = False) 

    if inputConnections:
        for connection in inputConnections:
            cmds.setAttr('%s.isHistoricallyInteresting' % connection, 0)

    #relatives     
    relatives = cmds.listRelatives(node, shapes = True)

    if relatives:
        for relative in relatives:
            cmds.setAttr('%s.isHistoricallyInteresting' % relative, 0)

