import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math
import sys

puppetNodeName = "puppet"
puppetNodeID = OpenMaya.MTypeId(0x122ff)
matrixNodeID = OpenMayaMPx.MPxTransformationMatrix().baseTransformationMatrixId

class PuppetNode(OpenMayaMPx.MPxTransform):
    aTest = OpenMaya.MObject()
    aOutValue = OpenMaya.MObject()
    
    def __init__(self, transform=None):
        if transform is None:
            OpenMayaMPx.MPxTransform.__init__(self)
        else:
            OpenMayaMPx.MPxTransform.__init__(self, transform)
    
    def compute(self, plug, dataBlock):
        testValue = dataBlock.inputValue(self.aTest).asFloat()
        
        print "I am in the compute!", testValue
    
    def connectionMade(self,plug,otherPlug,asSrc):
        print plug,otherPlug,asSrc
        value = plug.asMDataHandle().asFloat()
        print "I am in the connectionMade!"
        print value

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( PuppetNode() )

def nodeInitializer():
    fnaTest = OpenMaya.MFnNumericAttribute()
    fnaOutValue = OpenMaya.MFnNumericAttribute()
    
    PuppetNode.aTest = fnaTest.create('test', 'test', OpenMaya.MFnNumericData.kFloat, 0.0)
    
    fnaTest.setKeyable(True)
    fnaTest.setReadable(True)
    fnaTest.setWritable(True)
    fnaTest.setStorable(True)
    
    PuppetNode.aOutValue = fnaOutValue.create('outValue', 'outValue', OpenMaya.MFnNumericData.kFloat, 0.0)
    
    fnaOutValue.setReadable(True)
    fnaOutValue.setWritable(False)
    fnaOutValue.setKeyable(False)
    fnaOutValue.setStorable(True)
    
    PuppetNode.addAttribute(PuppetNode.aTest)
    PuppetNode.addAttribute(PuppetNode.aOutValue)
    PuppetNode.attributeAffects(PuppetNode.aTest,PuppetNode.aOutValue)
        
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