import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math
import sys

puppetNodeName = "puppet"
puppetNodeID = OpenMaya.MTypeId(0x122ff)
matrixNodeID = OpenMayaMPx.MPxTransformationMatrix().baseTransformationMatrixId

class PuppetNode(OpenMayaMPx.MPxTransform):
    parentAttr = OpenMaya.MObject()
    childAttr = OpenMaya.MObject()
    
    def __init__(self, transform=None):
        if transform is None:
            OpenMayaMPx.MPxTransform.__init__(self)
        else:
            OpenMayaMPx.MPxTransform.__init__(self, transform)
    
    def compute(self, plug, dataBlock):
        return True

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( PuppetNode() )

def nodeInitializer():
    return True
        
# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    
    try:
        mplugin.registerTransform( puppetNodeName, puppetNodeID,nodeCreator,
                                       nodeInitializer, OpenMayaMPx.MPxTransformationMatrix, matrixNodeID)
    except:
        sys.stderr.write( "Failed to register transform: %s\n" % puppetNodeName )
        raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode( puppetNodeID )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % puppetNodeName )