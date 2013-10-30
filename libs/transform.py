# Import Maya modules
import maya.cmds        as cmds
import maya.mel         as mel
import maya.OpenMaya    as OpenMaya

# Import japeto modules
import japeto
common      = japeto.importModule ("libs.common", True)
attribute   = japeto.importModule ("libs.attribute", True)

# ------------------------------------------------------------------------------
# Transform Constants
IDENTITY = [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0]

ZERO            = [0.0, 0.0, 0.0]
LEFT    = X     = [1.0, 0.0, 0.0]
RIGHT   = X_NEG = [-1.0, 0.0, 0.0]
UP      = Y     = [0.0, 1.0, 0.0]
DOWN    = Y_NEG = [0.0, -1.0, 0.0]
FRONT   = Z     = [0.0, 0.0, 1.0]
BACK    = Z_NEG = [0.0, 0.0, -1.0]

AXES        = {"x" : X, "-x" : X_NEG, "y" : Y, "-y" : Y_NEG, "z" : Z, "-z" : Z_NEG}
AXES_INDEX  = {"x" : 0, "-x" : 0, "y" : 1, "-y" : 1, "z" : 2, "-z" : 2}
MSPACE      = {"world": api.MSpace.kWorld, "object" : api.MSpace.kObject, "local" : api.MSpace.kTransform}


def matchXform(target, original, type = 'pose'):
    position = cmds.xform(target, q = True, ws = True, t = True)
    rotation = cmds.xform(target, q = True, ws = True, ro = True)
    if type == 'pose':
        cmds.xform(original, ws = True, t = position)
        cmds.xform(original, ws = True, ro = rotation)
    elif type == 'position':
        cmds.xform(original, ws = True, t = position)

    elif type == 'rotate':
        cmds.xform(original, ws = True, ro = rotation)



def getAxis( transform, vector=(0,1,0) ):
    '''Returns the closest axis to the given vector.

    .. python ::

        import maya.cmds as cmds

        # Simple Example
        t = cmds.createNode('transform')
        getAxis( t, (1,0,0) )
        # Result: 'x'

        # Joint Example
        j1 = cmds.joint(p=(0, 0, 0))
        j2 = cmds.joint(p=(0, 0, 2))
        cmds.joint( j1, e=True, zso=True, oj='xyz', sao='yup')
        getAxis( j1, (1,0,0) )
        # Result: '-z'

    @param transform: Transform node to calculate the vector from
    @type transform: *str*
    @param vector: Vector to compare with the transform matrix.
    @type vector: *list* or *tuple*
    @returns: *x*,*-x*,*y*,*-y*,*z* or *-z*
    @rtype: *str*
    '''

    # get dag path
    dpath = common.asMDagPath( transform )

    # get world matrix
    m = dpath.inclusiveMatrix()

    # get vectors
    x      = api.MVector( m(0,0), m(0,1), m(0,2) )
    y      = api.MVector( m(1,0), m(1,1), m(1,2) )
    z      = api.MVector( m(2,0), m(2,1), m(2,2) )
    v      = api.MVector( vector[0], vector[1], vector[2] )
    axis   = None
    factor = -1

    # x
    dot = x * v
    if dot > factor:
        factor = dot
        axis = 'x'

    # -x
    dot = -x * v
    if dot > factor:
        factor = dot
        axis = '-x'

    # y
    dot = y * v
    if dot > factor:
        factor = dot
        axis = 'y'

    # -y
    dot = -y * v
    if dot > factor:
        factor = dot
        axis = '-y'

    # z
    dot = z * v
    if dot > factor:
        factor = dot
        axis = 'z'

    # -z
    dot = -z * v
    if dot > factor:
        factor = dot
        axis = '-z'

    return axis      


def getAveragePositionFromRelatives( transform ):
    '''Get average position from relatives.
    It filters out constraints.

    @param transform: Transform to use for relatives look up
    @type transform: *str*

    @return: Return average position
    @rtype: *list*
    '''
    lR = cmds.listRelatives( transform, type='transform', f=True)
    if not lR:
        return cmds.xform( transform, q=True, ws=True, rp=True)

    count  = 0
    avgPos = [0,0,0]
    for r in lR:
        # skip constraints
        if cmds.ls( r, type='constraint' ):
            continue

        pos = cmds.xform( r, q=True, ws=True, rp=True)
        count     += 1
        avgPos[0] += pos[0]
        avgPos[1] += pos[1]
        avgPos[2] += pos[2]

    avgPos[0]/=count
    avgPos[1]/=count
    avgPos[2]/=count

    return avgPos


def averagePosition(objects):
    '''
    Gets the average position of given objects
    
    Example:
        average_position(["joint1", "joint2", "joint3"])
        #Result: (1.546, 24.592,302.13)
    
    @param objects: Objects you would like to get the average position from
    @type objects: *list* 
    
    @return: Point position
    @rtype: *tuple*
    '''
    pointListX = list()
    pointListY = list()
    pointListZ = list()
    for obj in objects:
        if not cmds.objExists(obj):
            sys.stderr.write('%s does not exist' % obj)
        #Get world space position of an object
        ws = cmds.xform(obj, q = True, ws = True, t = True)
        #store the point positions
        pointListX.append(ws[0])
        pointListY.append(ws[1])
        pointListZ.append(ws[2])
    #end for loop
    
    #average positions
    pointX = getAverage(pointListX)
    pointY = getAverage(pointListY)
    pointZ = getAverage(pointListZ)
    
    return [pointX, pointY, pointZ]


def averagePositionFromSelected():    
    #get selected items
    mSelList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList()
    if mSelList.length() == 0:
        sys.stderr.write('nothing is selected!')
    pntListX = list()
    pntListY = list()
    pntListZ = list()
    
   #loop through selected
    for i in range(mSelList.length()):
        mObject = OpenMaya.MObject()
        dagPath = OpenMaya.MDagPath()
        mSelList.getDagPath(i, dagPath)
        mSelList.getDependNode(i, mObject)
        type = object.apiType()
        
        if (type == OpenMaya.MFn.kTransform or type == OpenMaya.MFn.kJoint):
            mFnTransform = api.MFnTransform(dagPath)
            wsVector = mFnTransform.translation(api.MSpace.kTransform)
            pntListX.append(wsVector.x)
            pntListY.append(wsVector.y)
            pntListZ.append(wsVector.z)
        #end if
        else:
            cmds.warning('%s is not a transform or a joint so will not be computed' % dagPath.fullPathName())
        #end else
        
    pntX = getAverage(pntListX) 
    pntY = getAverage(pntListY)
    pntZ = getAverage(pntListZ)
    
    return OpenMaya.MVector(pntX,pntY,pntZ)

        
def getAverage(values):
    '''
    Get the average number of a given list of numbers
    
    Example:
        get_average([2.54,3,9,903])
        #Result: 229.38499999999999
        
    @param values: Numbers to get average from
    @type values: *list*
    
    @return: Average number
    @rtype: *float*  
    '''
    #put values into a list
    values = common.toList(values)
    
    return float(sum(values) / len(values))


def getAimAxis ( transform, allowNegative = True):
    '''
    Get transform aim axis based on relatives.
    This is a wrap of getAxis(), uses the average position of the children to pass the vector.

    @param transform: Transform to get the aim axis from.
    @type transform: *str*

    @param allowNegative: Allow negative axis
    @type allowNegative: *bool*

    @return: Return aim axis
    @rtype: *str*
    '''

    pos  = cmds.xform( transform, q=True, ws=True, rp=True )
    rel  = getAveragePositionFromRelatives( transform )
    axis = getAxis( transform, (rel[0]-pos[0], rel[1]-pos[1], rel[2]-pos[2] ) )

    if not allowNegative:
        return axis[-1]

    return axis