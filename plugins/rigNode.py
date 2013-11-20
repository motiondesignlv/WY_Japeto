import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

rigNodeName = "rig"
rigNodeID = OpenMaya.MTypeId(0x101ff)
matrixNodeID = OpenMayaMPx.MPxTransformationMatrix().baseTransformationMatrixId

class RigNode(OpenMayaMPx.MPxTransform):

    def __init__(self, transform=None):
        if transform is None:
            OpenMayaMPx.MPxTransform.__init__(self)
        else:
            OpenMayaMPx.MPxTransform.__init__(self, transform)
    
    def compute(self, plug, dataBlock):
        return True

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( RigNode() )

def nodeInitializer():
    return True
        
# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    
    try:
        mplugin.registerTransform( rigNodeName, rigNodeID,nodeCreator,
                                       nodeInitializer, OpenMayaMPx.MPxTransformationMatrix, matrixNodeID)
    except:
        sys.stderr.write( "Failed to register transform: %s\n" % rigNodeName )
        raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    
    try:
        mplugin.deregisterNode( rigNodeID )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % rigNodeName )
        raise