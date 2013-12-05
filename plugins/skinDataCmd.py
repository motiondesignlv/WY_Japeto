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
    kVertIdFlag = '-v'
    kVertIdLongFlag = '-vertId'
    
    def __init__(self):
        super(SkinDataCmd, self).__init__()
        self.__mesh     = str()
        self.__mObject  = OpenMaya.MObject()
        self.__mDagPath = OpenMaya.MDagPath()
        self.__mSelList = OpenMaya.MSelectionList()
        self.__influenceNames  = list()
        self.__weights = OpenMaya.MDoubleArray()
        self.__returnWeights   = False
        self.__returnInfluenceWeights = False
        self.__returnInfluence = False
        self.__undoable = False
        self.__setVertWeights = False

    
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
            self.displayError('Must pass in Mesh as first Argument')         
        if argData.isQuery() and argData.isFlagSet( SkinDataCmd.kWeightsFlag ) and argData.isFlagSet( SkinDataCmd.kInfluenceFlag ):
            try:
                self._influnceNode = argData.commandArgumentString( 1 )
            except:
                pass
            self.__returnWeights = True
            self.__returnInfluenceWeights = True
            self.__undoable = False
        elif argData.isQuery() and argData.isFlagSet( SkinDataCmd.kInfluenceFlag ):
            self.__returnInfluence = True
            self.__undoable = False
        elif argData.isQuery() and argData.isFlagSet( SkinDataCmd.kWeightsFlag ):
            self.__returnWeights = True
            self.__undoable = False
        elif argData.isFlagSet( SkinDataCmd.kWeightsFlag ) and argData.isFlagSet( SkinDataCmd.kInfluenceFlag ) and argData.isFlagSet( SkinDataCmd.kVertIdFlag ):
            self._weightValue = argData.flagArgumentDouble(SkinDataCmd.kWeightsFlag, 0)
            self._vertId = argData.flagArgumentInt(SkinDataCmd.kVertIdFlag, 0)
            self._influence = argData.flagArgumentString(SkinDataCmd.kInfluenceFlag, 0)
            self.__setVertWeights = True
            self.__undoable = True
        else:
            self.displayError('No arguments passed')

            
    def redoIt(self):
        '''
        Get weights on mesh from skinCluster deformer passed in and return dictionary
        with all data stored.
        '''
        mSkinClsObject = self.__getSkinClusterObject(self.__mesh)
        
        #get the skincluster object
        self.__mFnScls = OpenMayaAnim.MFnSkinCluster(mSkinClsObject)
        
        #check which operation we want to return to the user
        if self.__returnWeights:
            influence = None
            if self.__returnInfluenceWeights:
                influence = self._influnceNode
            dagPath, components = self.__getComponents()
            weights = self.__getWeights(dagPath, components, influence)
            self.setResult(weights)
            self.getCurrentResult(OpenMaya.MDoubleArray())
        elif self.__returnInfluence:
            influenceNames = self.__getInfluences()
            self.setResult(influenceNames)
            self.getCurrentResult(list())
        elif self.__setVertWeights:
            self.__setWeights()

    def undoIt(self):
        pass


    def isUndoable(self):
        ''' This function indicates whether or not the command is undoable. If the
        command is undoable, each executed instance of that command is added to the
        undo queue. '''
        
        # We must return True to specify that this command is undoable.
        return self.__undoable
    
    
    #--------------------------------------------------------------------
    #GATHER DATA METHODS
    #--------------------------------------------------------------------

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
        
        if self.__mObject.hasFn(OpenMaya.MFn.kSkinClusterFilter):
            return self.__mObject
        
        self.__mSelList.getDagPath(0, self.__mDagPath)
        
        #check the object
        if not self.__mObject.hasFn(OpenMaya.MFn.kMesh) and self.__mObject.hasFn(OpenMaya.MFn.kTransform):
            dagFn = OpenMaya.MFnDagNode(self.__mDagPath)
            childCount = dagFn.childCount()
            for index in range(0,childCount):
                child = dagFn.child(index)
                if child.hasFn(OpenMaya.MFn.kMesh):
                    self.__mObject = OpenMaya.MObject(child)
                    break
                
        graphIter = OpenMaya.MItDependencyGraph(self.__mObject, OpenMaya.MItDependencyGraph.kDownstream, OpenMaya.MItDependencyGraph.kPlugLevel)
        
        while not graphIter.isDone():
            currentItem = graphIter.currentItem()
            if currentItem.hasFn(OpenMaya.MFn.kSkinClusterFilter):
                return currentItem
            graphIter.next()  

        
        return None 
    
    def __getComponents(self):
        '''
        Gets and returns the DagPath to the mesh and the components of the mesh
        '''
        fnSet = OpenMaya.MFnSet(self.__mFnScls.deformerSet())
        members = OpenMaya.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OpenMaya.MDagPath()
        components = OpenMaya.MObject()
        members.getDagPath(0, dagPath, components)
        
        return dagPath, components
    
    def __getWeights(self, dagPath, components, influence = None):
        '''
        Gets the weights from on the mesh
        
        @param dagPath: DagPath to the mesh
        @type dagPaht: *OpenMaya.MDagPath*
        
        @param components: Object pointing to the Components (i.e. Vertices)
        @type components: *OpenMaya.MObject*    
        
        @param influence: Name of the influence being queried
        @type influence: *str* or *unicode* 
        '''
        weights = OpenMaya.MDoubleArray()
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        pUInt = util.asUintPtr()
        if influence:
            influenceNames = self.__getInfluences()
            index = influenceNames.index(influence)
            self.__mFnScls.getWeights(dagPath,components, index, weights)
        else:
            self.__mFnScls.getWeights(dagPath, components, weights, pUInt)
        
        return weights
        
    def __getBlendWeights(self, dagPath, components):
        pass
    
    def __getInfluences(self):
        '''
        Gets and returns all the influence objects on the skinCluster
        '''
        # Influences & Influence count
        influences= OpenMaya.MDagPathArray()
        infCount = self.__mFnScls.influenceObjects(influences)
        # Get node names for influences
        influenceNames = [influences[i].partialPathName() for i in range(infCount)]
        
        return influenceNames


    #--------------------------------------------------------------------
    #SET DATA METHODS
    #--------------------------------------------------------------------
    def __setWeights(self):
        #get the object and dagPath of the mesh
        self.__mObject
            
        #skincluster function
        mSkinClsObject = self.__getSkinClusterObject(self.__mesh)
        mFnScls = OpenMayaAnim.MFnSkinCluster(mSkinClsObject)

        # Get node names for influences
        influenceNames = self.__getInfluences()

        
        vertIter = OpenMaya.MItMeshVertex(self.__mObject)
        
        while not vertIter.isDone():
            vertCurrentIndexUtil = OpenMaya.MScriptUtil(vertIter.index())
            vertCurrentIndexPtr = vertCurrentIndexUtil.asIntPtr()
            vertIter.setIndex(self._vertId,vertCurrentIndexPtr)
            self.__mFnScls.setWeights(self.__mDagPath, vertIter.currentItem(), influenceNames.index(self._influence), self._weightValue)    
            break

    #--------------------------------------------------------------------
    #CREATOR METHODS
    #--------------------------------------------------------------------
    @classmethod
    def cmdCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())

    @classmethod
    def cmdSyntaxCreator(cls):
        ''' Defines the argument and flag syntax for this command. '''
        syntax = OpenMaya.MSyntax()
        syntax.addArg( OpenMaya.MSyntax.kString )
        syntax.addArg( OpenMaya.MSyntax.kString )
        syntax.addFlag( cls.kInfluenceFlag, cls.kInfluenceLongFlag, OpenMaya.MSyntax.kString)
        syntax.addFlag( cls.kWeightsFlag, cls.kWeightsLongFlag, OpenMaya.MSyntax.kDouble )
        syntax.addFlag( cls.kVertIdFlag, cls.kVertIdLongFlag, OpenMaya.MSyntax.kUnsigned  )
        syntax.enableQuery(True)
        syntax.enableEdit(True)
            
        return syntax


# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Magic Leap - Walt Yoder", "1.0", "Any")
    try:
        mplugin.registerCommand(SkinDataCmd.kCmdName, SkinDataCmd.cmdCreator, SkinDataCmd.cmdSyntaxCreator)
    except:
        sys.stderr.write("Failed to register command: %s" % SkinDataCmd.kCmdName)
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(SkinDataCmd.kCmdName)
    except:
        sys.stderr.write("Failed to deregister command: %s" % SkinDataCmd.kCmdName)
        raise