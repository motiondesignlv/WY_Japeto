'''
---------------------------------------------------
Name: SK Decompose Rotation Node Plugin

Version: 1.0 / August 5th, 2009
Version: 1.1 / May 2013

Original Author: Serguei Kalentchouk
Contributing Author: Jan Berger

Email: serguei.kalentchouk@disney.com

Description: Decompose rotation into individual
twist angle values around all 3 axies

Usage: Create the decompose rotation node and
connect the world or local matrix of the object you
wish you resolve. Alternatively connect or input
euler rotation values and rotation order.
The matrix connection takes priority over angles.
---------------------------------------------------
'''

# ---------------------
# Import Needed Modules
# ---------------------
import sys
import math
import maya.OpenMaya as api
import maya.OpenMayaMPx as apiMpx

# ------------------------
# Identify Plugin Elements
# ------------------------
skPluginName = "decomposeRotation"
skNodeName = "decomposeRotation"
skNodeID = api.MTypeId (110378) # DO NOT CHANGE THE ID

# ------------------------------
# Constraint Managment Callbacks
# ------------------------------
def skInitializeDecomposeRotationNode ():
    ''' Initizlie the decompose rotation node '''
    # Define attribute types
    nAttr = api.MFnNumericAttribute ()
    tAttr = api.MFnTypedAttribute ()
    uAttr = api.MFnUnitAttribute ()
    cAttr = api.MFnCompoundAttribute ()
    eAttr = api.MFnEnumAttribute ()

    # Define inputs
    skDecomposeRotationNode.targetMatrix = tAttr.create ("targetMatrix", "tm", api.MFnData.kMatrix)

    skDecomposeRotationNode.rotateX = uAttr.create ("rotateX", "rtx", api.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setKeyable (True)
    skDecomposeRotationNode.rotateY = uAttr.create ("rotateY", "rty", api.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setKeyable (True)
    skDecomposeRotationNode.rotateZ = uAttr.create ("rotateZ", "rtz", api.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setKeyable (True)

    skDecomposeRotationNode.targetRotation = cAttr.create ("targetRotation", "tr")
    cAttr.addChild (skDecomposeRotationNode.rotateX)
    cAttr.addChild (skDecomposeRotationNode.rotateY)
    cAttr.addChild (skDecomposeRotationNode.rotateZ)

    skDecomposeRotationNode.rotateOrder = eAttr.create ("rotateOrder", "rto", 0)
    eAttr.addField ("xyz", 0)
    eAttr.addField ("yzx", 1)
    eAttr.addField ("zxy", 2)
    eAttr.addField ("xzy", 3)
    eAttr.addField ("yxz", 4)
    eAttr.addField ("zyx", 5)

    skDecomposeRotationNode.twistMode = eAttr.create ("twistMode", "twm", 0)
    eAttr.addField ("default", 0)
    eAttr.addField ("No Roll", 1)

    # Define outputs
    skDecomposeRotationNode.twistX = nAttr.create ("twistX", "tx", api.MFnNumericData.kFloat, 0.0)
    nAttr.setConnectable (True)
    nAttr.setChannelBox (True)
    skDecomposeRotationNode.twistY = nAttr.create ("twistY", "ty", api.MFnNumericData.kFloat, 0.0)
    nAttr.setChannelBox (True)
    skDecomposeRotationNode.twistZ = nAttr.create ("twistZ", "tz", api.MFnNumericData.kFloat, 0.0)
    nAttr.setChannelBox (True)

    # Add attributes
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.targetMatrix)
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.targetRotation)
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.rotateOrder)
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.twistX)
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.twistY)
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.twistZ)
    skDecomposeRotationNode.addAttribute (skDecomposeRotationNode.twistMode)

    # Define attribute relationships
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.targetMatrix, skDecomposeRotationNode.twistX)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.targetMatrix, skDecomposeRotationNode.twistY)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.targetMatrix, skDecomposeRotationNode.twistZ)

    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.targetRotation, skDecomposeRotationNode.twistX)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.targetRotation, skDecomposeRotationNode.twistY)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.targetRotation, skDecomposeRotationNode.twistZ)

    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.rotateOrder, skDecomposeRotationNode.twistX)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.rotateOrder, skDecomposeRotationNode.twistY)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.rotateOrder, skDecomposeRotationNode.twistZ)

    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.twistMode, skDecomposeRotationNode.twistX)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.twistMode, skDecomposeRotationNode.twistY)
    skDecomposeRotationNode.attributeAffects (skDecomposeRotationNode.twistMode, skDecomposeRotationNode.twistZ)

def skCreateDecomposeRotationNode ():
    ''' Create the decompose rotation node '''
    return apiMpx.asMPxPtr (skDecomposeRotationNode ())

# --------------------------
# Main Plugin Class Elements
# --------------------------
class skDecomposeRotationNode (apiMpx.MPxNode):
    ''' SK Decompose Rotation Node '''
    def __init__ (self):
        ''' Initialize class '''
        # Initialize the parent class
        apiMpx.MPxNode.__init__ (self)

        # Define public class varibles
        self.targetMatrix = api.MObject ()
        self.rotateX = api.MObject ()
        self.rotateY = api.MObject ()
        self.rotateZ = api.MObject ()
        self.rotateOrder = api.MObject ()

        self.twistX = api.MObject ()
        self.twistY = api.MObject ()
        self.twistZ = api.MObject ()

        self.twistMode = api.MObject ()

    def compute (self, plug, data):
        ''' Compute the node behaviour '''
        if (plug == skDecomposeRotationNode.twistX):
            # Get target matrix plug
            targetMatrixPlug = api.MPlug (self.thisMObject (), skDecomposeRotationNode.targetMatrix)

            # Check if target matrix plug is connected
            if (targetMatrixPlug.isConnected ()):
                # Get target matrix
                dataHandle = data.inputValue (skDecomposeRotationNode.targetMatrix)
                targetMatrixData = dataHandle.data ()
                targetMatrix = api.MFnMatrixData (targetMatrixData).matrix ()
            else:
                # Get rotation angles
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateX)
                rotateX = dataHandle.asAngle ()
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateY)
                rotateY = dataHandle.asAngle ()
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateZ)
                rotateZ = dataHandle.asAngle ()

                dataHandle = data.inputValue (skDecomposeRotationNode.rotateOrder)
                rotateOrder = dataHandle.asInt ()

                # Get matrix from rotation angles
                targetMatrix = self.getMatrixFromAngles (rotateX, rotateY, rotateZ, rotateOrder)

            twistMode = data.inputValue (skDecomposeRotationNode.twistMode).asInt () 

            twistAngle = 0

            # Get twist angle
            if twistMode == 0:
                twistAngle = self.getTwist (targetMatrix, 0, 1)

            elif twistMode == 1:

                depFn = api.MFnDependencyNode ( self.thisMObject () )
 

                offset = api.MEulerRotation ( math.radians( 90 ), 0, 0 ) 

                targetMatrix = targetMatrix *  offset.asMatrix() 

                vec_x = api.MVector( targetMatrix(0,0), targetMatrix(0,1), targetMatrix(0,2) ) 
                vec_y = api.MVector( targetMatrix(1,0), targetMatrix(1,1), targetMatrix(1,2) )

                vec_x.normalize()
                vec_y.normalize()
  
                matList = (abs(vec_x.x), vec_x.y, vec_x.z, 0, vec_y.x, vec_y.y, vec_y.z, 0, 0, 0, 1, 0, 0, 0, 0, 1)
                twistMatrix = api.MMatrix()
                api.MScriptUtil.createMatrixFromList( matList, twistMatrix) 
  
                twistAngle = math.degrees( api.MTransformationMatrix ( twistMatrix ).eulerRotation().z )


            # Set output twist
            dataHandle = data.outputValue (skDecomposeRotationNode.twistX)
            dataHandle.setFloat (twistAngle)
            dataHandle.setClean ()
        elif (plug == skDecomposeRotationNode.twistY):
            # Get target matrix plug
            targetMatrixPlug = api.MPlug (self.thisMObject (), skDecomposeRotationNode.targetMatrix)

            # Check if target matrix plug is connected
            if (targetMatrixPlug.isConnected ()):
                # Get target matrix
                dataHandle = data.inputValue (skDecomposeRotationNode.targetMatrix)
                targetMatrixData = dataHandle.data ()
                targetMatrix = api.MFnMatrixData (targetMatrixData).matrix ()
            else:
                # Get rotation angles
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateX)
                rotateX = dataHandle.asAngle ()
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateY)
                rotateY = dataHandle.asAngle ()
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateZ)
                rotateZ = dataHandle.asAngle ()

                dataHandle = data.inputValue (skDecomposeRotationNode.rotateOrder)
                rotateOrder = dataHandle.asInt ()

                # Get matrix from rotation angles
                targetMatrix = self.getMatrixFromAngles (rotateX, rotateY, rotateZ, rotateOrder)

            twistMode = data.inputValue (skDecomposeRotationNode.twistMode).asInt () 

            twistAngle = 0
 
            # Get twist angle
            if twistMode == 0:
                twistAngle = self.getTwist (targetMatrix, 1, 0)

            elif twistMode == 1:
                twistAngle = self.getTwistNoRoll (targetMatrix, 1, 0) 

            # Set output twist 
            dataHandle = data.outputValue (skDecomposeRotationNode.twistY)  
            dataHandle.setFloat (twistAngle) 
            dataHandle.setClean ()
        elif (plug == skDecomposeRotationNode.twistZ):
            # Get target matrix plug
            targetMatrixPlug = api.MPlug (self.thisMObject (), skDecomposeRotationNode.targetMatrix)

            # Check if target matrix plug is connected
            if (targetMatrixPlug.isConnected ()):
                # Get target matrix
                dataHandle = data.inputValue (skDecomposeRotationNode.targetMatrix)
                targetMatrixData = dataHandle.data ()
                targetMatrix = api.MFnMatrixData (targetMatrixData).matrix ()
            else:
                # Get rotation angles
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateX)
                rotateX = dataHandle.asAngle ()
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateY)
                rotateY = dataHandle.asAngle ()
                dataHandle = data.inputValue (skDecomposeRotationNode.rotateZ)
                rotateZ = dataHandle.asAngle ()

                dataHandle = data.inputValue (skDecomposeRotationNode.rotateOrder)
                rotateOrder = dataHandle.asInt ()

                # Get matrix from rotation angles
                targetMatrix = self.getMatrixFromAngles (rotateX, rotateY, rotateZ, rotateOrder)

            # Get twist angle
            # twistAngle = self.getTwist (targetMatrix, 2, 1)

            twistMode = data.inputValue (skDecomposeRotationNode.twistMode).asInt () 

            twistAngle = 0
 
            # Get twist angle
            if twistMode == 0:
                twistAngle = self.getTwist (targetMatrix, 2, 1)

            elif twistMode == 1:
                twistAngle = self.getTwistNoRoll (targetMatrix, 2, 1)

            # Set output twist
            dataHandle = data.outputValue (skDecomposeRotationNode.twistZ)
            dataHandle.setFloat (twistAngle)
            dataHandle.setClean ()
        else:
            # Return unknown
            return api.kUnknownParameter
 
    def getMatrixFromAngles (self, angleX, angleY, angleZ, rotateOrder = 0):
        ''' Get matrix from rotation angles '''
        # Define rotate order list
        rotateOrderList = [api.MEulerRotation.kXYZ, api.MEulerRotation.kYZX, api.MEulerRotation.kZXY,
            api.MEulerRotation.kXZY, api.MEulerRotation.kYXZ, api.MEulerRotation.kZYX]

        # Create transformation matrix
        transfMatrix = api.MTransformationMatrix ()

        # Set euler rotation from angles
        eulerRotation = api.MEulerRotation (angleX.value (), angleY.value (), angleZ.value (), rotateOrderList [rotateOrder])

        # Set matrix from euler rotation
        transfMatrix.rotateTo (eulerRotation)
        matrix = transfMatrix.asMatrix ()

        # Return matrix
        return matrix

    def getTwist (self, targetMatrix, rollAxis, upAxis):
        ''' Get twist around axis '''
        # Define roll vector
        axesList = [0, 0, 0]
        axesList [rollAxis] = 1
        rollV = api.MVector (axesList [0], axesList [1], axesList [2])

        # Get direction and up vector from target matrix
        dirV = api.MVector (targetMatrix [rollAxis])
        dirV.normalize ()
        upV = api.MVector (targetMatrix [upAxis])
        upV.normalize ()

        # Get right vector
        rightV = dirV ^ rollV
        rightV.normalize ()

        # Get angle between direction and roll vectors
        angle = math.acos (dirV * rollV)

        # Create the resulting quaternion with no spin about the roll axis
        sine = math.sin (angle / 2)
        cosine = math.cos (angle / 2)
        noSpinQuat = api.MQuaternion (rightV.x * sine, rightV.y * sine, rightV.z * sine, cosine)
        noSpinQuat.conjugateIt ()

        # Create the new matrix from the no spin quaternion
        noSpinMatrix = noSpinQuat.asMatrix ()

        # Get new up vector
        upVNew = api.MVector (noSpinMatrix [upAxis])

        # Get cross vector between old and new up vectors
        crossV = upV ^ upVNew
        crossV.normalize ()

        # Get angle difference between up vectors and get the angle sign based on cross vector direction
        try:
            twist = math.acos (upV * upVNew)
            if (crossV.isEquivalent (dirV, 0.01) == True):
                # Negate twist angle
                twist = -twist
        except ValueError:
            # Set twist to 0 if failed
            twist = 0

        # Convert twist from radians to degrees
        twistAngle = math.degrees (twist)

        # Return twist angle
        return twistAngle

    def getTwistNoRoll (self, targetMatrix, rollAxis, upAxis):

        ''' Get roll free transformation '''

        aim_vec = api.MVector( targetMatrix(0,0), targetMatrix(0,1), targetMatrix(0,2) )
                
        axesList = [0, 0, 0]
        axesList [rollAxis] = 1
        up_vec = api.MVector (axesList [0], axesList [1], axesList [2])
 
        front_vec = api.MVector ( 1,0,0 )
        aim_vec.normalize() 

        aim_vec.x = round( aim_vec.x, 2) 
        aim_vec.y = round( aim_vec.y, 2)
        aim_vec.z = round( aim_vec.z, 2)

        up_vec.x = round( up_vec.x, 2)
        up_vec.y = round( up_vec.y, 2)
        up_vec.z = round( up_vec.z, 2)

        up_vec.x = 0
         
        rotqa = api.MQuaternion ( front_vec, aim_vec )

        aim_matrix = api.MTransformationMatrix()
        aim_matrix.rotateBy ( rotqa, api.MSpace.kTransform )
         
        objectup = up_vec.transformAsNormal( aim_matrix.asMatrixInverse() )
                      
        objectup.x = round(objectup.x, 2)
        objectup.y = round(objectup.y, 2)
        objectup.z = round(objectup.z, 2)
            
        rotqu = api.MQuaternion ( up_vec, objectup )
        aim_matrix.rotateBy ( rotqu, api.MSpace.kObject )
          
        return self.getTwist ( aim_matrix.asMatrix(), rollAxis, upAxis ) 
# --------------------------
# Plugin Managment Callbacks
# --------------------------
def initializePlugin (mobject):
    ''' Initialize the decompose rotation plugin '''
    # Get plugin
    mayaPlugin = apiMpx.MFnPlugin (mobject, "Magic Leap", "1.1", "2013")

    # Register plugin elements
    mayaPlugin.registerNode (skNodeName, skNodeID, skCreateDecomposeRotationNode, skInitializeDecomposeRotationNode)
    

def uninitializePlugin (mobject):
    ''' Uninitialize the decompose rotation plugin '''
    # Get plugin
    mplugin = apiMpx.MFnPlugin(mobject)

    # Deregister plugin elements
    mplugin.deregisterNode (skNodeID)
