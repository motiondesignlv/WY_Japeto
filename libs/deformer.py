'''
This is the deformer module for all the deformer utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: September 2013
'''
#import python modules
import os

#import Maya modules
from maya import cmds
from maya import OpenMaya
from maya import OpenMayaAnim

#import package modules
import japeto
from japeto.libs import common
from japeto.libs import pyon
from japeto.libs import ordereddict
from japeto.libs import fileIO

#load plugin for skinData
fileIO.loadPlugin(os.path.join(japeto.PLUGINDIR, 'skinDataCmd.py'))


class SkinCluster(object):
    
    kFileExtension = '.wts'
    
    @classmethod
    def save(cls, filePath = None, shape = None):
        skin = SkinCluster(shape)
        skin.saveWeights(filePath)
    
    @classmethod
    def load(self, filePath = None, shape = None):
        if not shape:
            try:
                shape = cmds.ls(sl = True)[0]
            except:
                raise RuntimeError('nothing is selected')
            
            
        #if no file path is input, bring up a dialog window
        if not filePath:
            dir = cmds.workspace(q = True, rootDirectory = True)
            filePath = cmds.fileDialog2(dialogStyle = 2, fileMode = 0, 
                                        startingDirectory = dir, fileFilter = 'Weight Files (*%s)' % SkinCluster.kFileExtension)
            
        #return if no filePath is found
        if not filePath:
            return
        #if it's a list we will get the first index 
        if isinstance(filePath, list):
            filePath = filePath[0]
            
        #read in the data from file
        data = pyon.load(filePath)
        
        #make sure the vertex count is the same
        meshVerts = cmds.polyEvaluate(shape, vertex = True)
        importedVerts = len(data['blendWeights'])
        if meshVerts != importedVerts:
            raise RuntimeError('Vertex counts do not match. %d != %d' % (meshVerts, importedVerts))
        
        if SkinCluster.getSkinCluster(shape):
            #existing skinCluster
            skinCluster = SkinCluster(shape)
        else:
            #create new skinCluster
            joints = data['weights'].keys()
            cmds.skinCluster(joints, shape, tsb = True, nw = 2, n = data['name'])
            skinCluster = SkinCluster(shape)
        
        skinCluster.setData(data)
            

    @classmethod
    def getSkinCluster(cls,shape):
        shape = common.getShapes(shape, 0)
        history = cmds.listHistory(shape, pruneDagObjects = True, il = 2)
        
        if not history:
            return None
        
        skins = [scl for scl in history if cmds.nodeType(scl) == 'skinCluster']
        if skins:
            return skins[0]
        
        return None
    
    @classmethod
    def removeNamespace(cls, value):
        valueSplit = value.split('|')
        newName = ''
        for i, val in enumerate(valueSplit):
            if i > 0:
                newName += '|'
            newName += val.split(':')[-1]
        return newName
    
    
    def __init__(self, shape = None):
        if not shape:
            try:
                shape = cmds.ls(sl = True)[0]
            except:
                raise RuntimeError('nothing is selected')
        
        self.shape = common.getShapes(shape, 0)
        if not shape:
            raise RuntimeError('No shape connected to %s' % shape)
        
        self.node = SkinCluster.getSkinCluster(self.shape)
        
        #create the orderedDict for data
        self.data = ordereddict.OrderedDict()
        self.data['name']             = self.node
        self.data['skinningMethod']   = int()
        self.data['normalizeWeights'] = int()
        self.data['weights']          = ordereddict.OrderedDict()
        self.data['blendWeights']     = list()
                    

    #-------------------
    #Get information 
    #-------------------
    
    def getData(self):
        self.getInfluenceWeights()
        self.getBlendWeights()
        
        for attr in ['skinningMethod', 'normalizeWeights']:
            self.data[attr] = cmds.getAttr('%s.%s' % (self.node, attr))
    
    def getInfluenceWeights(self):
        influence = cmds.skinData(self.node,q=True,inf=True)
        weights = cmds.skinData(self.node,q=True,wts=True)

        numComponentsPerInfluence = len(weights)/len(influence)
        numberOfInflunces = len(influence)
        for i in range(numberOfInflunces):  
            self.data['weights'][influence[i]] = [weights[j*numberOfInflunces + i] for j in range(numComponentsPerInfluence)]
            
    def getBlendWeights(self):
        self.data['blendWeights'] = cmds.skinData(self.node,q=True,bwt=True)

    #-------------------
    #Set information 
    #-------------------

    def setData(self, data):
        self.data = data

        self.setInfluenceWeights()
        self.setBlendWeights()
        
        for attr in ['skinningMethod', 'normalizeWeights']:
            cmds.setAttr('%s.%s' % (self.node, attr), self.data[attr])
            
    def setInfluenceWeights(self):
        influencePaths = cmds.skinData(self.node,q=True,inf=True)
        numInfluences = len(influencePaths)
        weights = list(range(numInfluences*len(self.data['weights'][self.data['weights'].keys()[0]])))
        numComponentsPerInfluence = len(weights) / numInfluences

        for i in range(numInfluences):
            influenceName = influencePaths[i]
            influenceNoNamespace = SkinCluster.removeNamespace(influenceName)
            if influenceNoNamespace == influenceName:
                for j in range(numComponentsPerInfluence):
                    weights[j*numInfluences+i] = self.data['weights'][influenceName][j]
                        
        cmds.skinData(self.node,wts=weights,inf=influencePaths)
                        
        
        
    def setBlendWeights(self):
        cmds.skinData(self.node,bwt=self.data['blendWeights'])
        


    def __getComponents(self):
        fnSet = OpenMaya.MFnSet(self._fn.deformerSet())
        members = OpenMaya.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OpenMaya.MDagPath()
        components = OpenMaya.MObject()
        members.getDagPath(0, dagPath, components)
        return dagPath, components
    
    def saveWeights(self, filePath = None):
        #if no file path is input, bring up a dialog window
        if not filePath:
            dir = cmds.workspace(q = True, rootDirectory = True)
            filePath = cmds.fileDialog2(dialogStyle = 2, fileMode = 0, 
                                        startingDirectory = dir, fileFilter = 'Weight Files (*%s)' % SkinCluster.kFileExtension)
        #return if no filePath is found
        if not filePath:
            return
        #if it's a list we will get the first index 
        if isinstance(filePath, list) or isinstance(filePath,tuple):
            filePath = filePath[0]
        
        #check to see if extension is attached to the filePath
        if not filePath.endswith(SkinCluster.kFileExtension):
            filePath += SkinCluster.kFileExtension
        
        #gather the data
        self.getData()
        
        #export the data
        pyon.save(self.data, filePath)
        
    



def createCluster(geometry,name,handle=str()):
    '''
    Will create and return a cluster with the handle given.

    :param geometry: geometry you wish to have the cluster deform.
    :type geometry: str

    :param name: Name for the cluster that will be created.
    :type name: str

    :param handle: Handle you wish to use for the cluster.
    :type handle: str

    :return: Cluster name
    :rtype: str
    '''
    if not isinstance(geometry,basestring):
        raise TypeError("{0} must be a str. and exist in the scene.".format(geometry))

    if not cmds.objExists(geometry):
        raise RuntimeError("{0} does not exist in the current Maya session.".format(geometry))

    currentSelection = cmds.ls(sl=True)

    cmds.select(geometry,r=True)

    #select the geometry in the scene
    if handle and cmds.objExists(handle):
        cls,clsHandle = cmds.cluster(wn=(handle,handle))
    else:
        cls, clsHandle = cmds.cluster()

    cmds.cluster(cls,e=True,g=geometry)
    cls = cmds.rename(cls,name)
    if not handle == clsHandle:
        cmds.rename(clsHandle,handle)

    if currentSelection:
        cmds.select(currentSelection)

    return cls