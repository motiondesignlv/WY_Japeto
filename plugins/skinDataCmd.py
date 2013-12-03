import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaAnim as OpenMayaAnim
import sys

class SkinDataCmd(OpenMayaMPx.MPxCommand):
    kCmdName = "skinData"
    kInfluenceFlag = '-inf'
    kInfluenceLongFlag = '-influence'
    kWeightsFlag = '-w'
    kWeightsLongFlag = '-weights'
    
    def __init__(self):
        super(SkinData, self).__init__()
        self.__mesh     = str()
        self.__mObject  = OpenMaya.MObject()
        self.__mDagPath = OpenMaya.MDagPath()
        self.__mSelList = OpenMaya.MSelectionList()
        self.__influenceNames  = list()
        self.__returnWeights   = False
        self.__returnInfluence = False

    
    def doIt(self, args):
        # Create the node
        self.parseArguments(args)
        return self.redoIt()
    
    def parseArguments(self, args):
        ''' 
        The presence of this function is not enforced,
        but helps separate argument parsing code from other
        command code. 
        '''
        
        # Getting the argData from MArgParser
        argData = OpenMaya.MArgParser( self.syntax(), args )
        try:
            self.__mesh = argData.commandArgumentString( 0 )
        except:
            self.displayError('Must pass in Mesh Argument')
        if argData.isQuery() and argData.isFlagSet( SkinData.kInfluenceFlag ):
            self.__returnInfluence = True
        elif argData.isQuery() and argData.isFlagSet( SkinData.kWeightsFlag ):
            self.__returnWeights = True
        else:
            self.displayError('No arguments passed')
            
    def redoIt(self):
        '''
        Get weights on mesh from skinCluster deformer passed in and return dictionary
        with all data stored.
        
        @param mesh: Name of geometry that is deforming
        @type mesh: *str*
        
        @return: Dictionary returned from getWeights function
        @rtype: *dict*
        '''
        mSkinClsObject = self.__getSkinClusterObject(self.__mesh)

        self.__mFnScls = OpenMayaAnim.MFnSkinCluster(mSkinClsObject)
        fnSet = OpenMaya.MFnSet(self.__mFnScls.deformerSet())
        members = OpenMaya.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OpenMaya.MDagPath()
        components = OpenMaya.MObject()
        members.getDagPath(0, dagPath, components)

        if self.__returnWeights:
            self.__getWeights(dagPath, components)
        elif self.__returnInfluence:
            self.__getInfluenceObjects()

    def undoIt(self):
        pass


    def isUndoable(self):
        ''' This function indicates whether or not the command is undoable. If the
        command is undoable, each executed instance of that command is added to the
        undo queue. '''
        
        # We must return True to specify that this command is undoable.
        return True

    def __getSkinClusterObject(self, mesh):
        '''
        Gets the deformer object on the given mesh. If no mesh is passed in,
        by default we will get active selection from you Maya scene

        @param mesh: Polygonal mesh you wish to get skincluster from
        @type mesh: *str* or *unicode*
        
        @return: Returns an MObject for the skinCluster attached to given mesh.
        @rtype: *MObject* or *None*
        
        '''
        self.__mSelList.add(self.__mesh)
        self.__mSelList.getDependNode(0, self.__mObject)
        
        #checks if it is a skinCluster already and returns if it is
        if self.__mObject.hasFn(OpenMaya.MFn.kSkinClusterFilter):
            return self.__mObject
        
        #get dagPath
        self.__mSelList.getDagPath(0, self.__mDagPath)
        
        #check the object, if it finds kMesh type, we re-assign mObject to the mesh
        if not self.__mObject.hasFn(OpenMaya.MFn.kMesh) and self.__mObject.hasFn(OpenMaya.MFn.kTransform):
            dagFn = OpenMaya.MFnDagNode(self.__mDagPath)
            childCount = dagFn.childCount()
            for index in range(0,childCount):
                child = dagFn.child(index)
                if child.hasFn(OpenMaya.MFn.kMesh):
                    self.__mObject = OpenMaya.MObject(child)
                    break
        #iterate througe the graph to get the skinCluster
        graphIter = OpenMaya.MItDependencyGraph(self.__mObject, OpenMaya.MItDependencyGraph.kDownstream, OpenMaya.MItDependencyGraph.kPlugLevel)
        
        while not graphIter.isDone():
            currentItem = graphIter.currentItem()
            if currentItem.hasFn(OpenMaya.MFn.kSkinClusterFilter):
                return currentItem
            graphIter.next()  

        
        return None 
    
    def __getWeights(self, dagPath, components):
        '''
        Gets the weights for mesh or skinCluster passed in to command
        
        @param dagPath: MDagPath to the kMesh which the skinCluster is connected to
        @type dagPath: *OpenMaya.MDagPath*
        
        @param components: MObject containing the vertices of the kMesh that is part of the
                           skinCluster deformer set
        @type components: *OpenMaya.MObject*
        '''
        weights = OpenMaya.MDoubleArray()
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        pUInt = util.asUintPtr()
        self.__mFnScls.getWeights(dagPath, components, weights, pUInt)
        
        self.setResult(weights)
        self.getCurrentResult(OpenMaya.MDoubleArray())
        
    def __getBlendWeights(self):
        pass
        
    def __getInfluenceObjects(self):
        # Influences & Influence count
        influences= OpenMaya.MDagPathArray()
        infCount = self.__mFnScls.influenceObjects(influences)
        # Get node names for influences
        influenceNames = [influences[i].partialPathName() for i in range(infCount)]
        
        self.setResult(influenceNames)
        self.getCurrentResult(list())
        
#####################################################################

def cmdCreator():
    return OpenMayaMPx.asMPxPtr(SkinData())


def cmdSyntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    syntax = OpenMaya.MSyntax()

    syntax.addArg( OpenMaya.MSyntax.kString )
    syntax.addFlag( SkinData.kInfluenceFlag, SkinData.kInfluenceLongFlag, OpenMaya.MSyntax.kBoolean )
    syntax.addFlag( SkinData.kWeightsFlag, SkinData.kWeightsLongFlag, OpenMaya.MSyntax.kBoolean )
    syntax.enableQuery(True)
        
    return syntax


# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Magic Leap - Walter Yoder", "1.0", "Any")
    try:
        mplugin.registerCommand(SkinData.kCmdName, cmdCreator, cmdSyntaxCreator)
    except:
        sys.stderr.write("Failed to register command: %s" % SkinData.kCmdName)
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(SkinData.kCmdName)
    except:
        sys.stderr.write("Failed to deregister command: %s" % SkinData.kCmdName)
        raise