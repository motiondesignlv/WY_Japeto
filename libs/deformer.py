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
                                        startingDirectory = dir, fileFilter = 'Skin Files (*%s)' % SkinCluster.kFileExtension)
            
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
        
        self._mObject = common.getMObject(self.node)
        self._fn = OpenMayaAnim.MFnSkinCluster(self._mObject)
        
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
        dagPath, components = self.__getComponents()
        self.getInfluenceWeights(dagPath, components)
        self.getBlendWeights(dagPath, components)
        
        for attr in ['skinningMethod', 'normalizeWeights']:
            self.data[attr] = cmds.getAttr('%s.%s' % (self.node, attr))
    
    def getInfluenceWeights(self, dagPath, components):
        weights = self.__getWeights(dagPath, components)
        
        influencePaths = OpenMaya.MDagPathArray()
        numInfluences = self._fn.influenceObjects(influencePaths)
        numComponentsPerInfluence = weights.length() / numInfluences
        for i in range(influencePaths.length()):
            influenceName = influencePaths[i].partialPathName()
            influenceNoNameSpace = SkinCluster.removeNamespace(influenceName)   
            self.data['weights'][influenceNoNameSpace] = [weights[j*numInfluences + i] for j in range(numComponentsPerInfluence)]
            
    def getBlendWeights(self, dagPath, components):
        weights = OpenMaya.MDoubleArray()
        self._fn.getBlendWeights(dagPath, components, weights)
        self.data['blendWeights'] = [weights[i] for i in range(weights.length())]

    #-------------------
    #Set information 
    #-------------------

    def setData(self, data):
        self.data = data

        dagPath, components = self.__getComponents()
        self.setInfluenceWeights(dagPath, components)
        self.setBlendWeights(dagPath, components)
        
        for attr in ['skinningMethod', 'normalizeWeights']:
            cmds.setAttr('%s.%s' % (self.node, attr), self.data[attr])
            
    def setInfluenceWeights(self, dagPath, components):
        weights = self.__getWeights(dagPath, components)
        
        influencePaths = OpenMaya.MDagPathArray()
        numInfluences = self._fn.influenceObjects(influencePaths)
        numComponentsPerInfluence = weights.length() / numInfluences
        
        for importedInfluence, importedWeights in self.data['weights'].items():
            for i in range(influencePaths.length()):
                influenceName = influencePaths[i].partialPathName()
                influenceNoNamespace = SkinCluster.removeNamespace(influenceName)
                if influenceNoNamespace == influenceName:
                    for j in range(numComponentsPerInfluence):
                        weights.set(importedWeights[j], j*numInfluences+i)
                        
            
        
        influenceIndices = OpenMaya.MIntArray(numInfluences)
        for i in range(numInfluences):
            influenceIndices.set(i,i)
        self._fn.setWeights(dagPath, components, influenceIndices, weights, False)
        
        
    def setBlendWeights(self, dagPath, components):
        blendWeights = OpenMaya.MDoubleArray(len(self.data['blendWeights']))
        for i,w in enumerate(self.data['blendWeights']):
            blendWeights.set(w,i)
            
        self._fn.setBlendWeights(dagPath, components, blendWeights)


    def __getComponents(self):
        fnSet = OpenMaya.MFnSet(self._fn.deformerSet())
        members = OpenMaya.MSelectionList()
        fnSet.getMembers(members, False)
        dagPath = OpenMaya.MDagPath()
        components = OpenMaya.MObject()
        members.getDagPath(0, dagPath, components)
        return dagPath, components
    
    def __getWeights(self, dagPath, components):
        weights = OpenMaya.MDoubleArray()
        util = OpenMaya.MScriptUtil()
        util.createFromInt(0)
        pUInt = util.asUintPtr()
        self._fn.getWeights(dagPath, components, weights, pUInt)
        return weights
    
    def saveWeights(self, filePath = None):
        #if no file path is input, bring up a dialog window
        if not filePath:
            dir = cmds.workspace(q = True, rootDirectory = True)
            filePath = cmds.fileDialog2(dialogStyle = 2, fileMode = 0, 
                                        startingDirectory = dir, fileFilter = 'Skin Files (*%s)' % SkinCluster.kFileExtension)
        #return if no filePath is found
        if not filePath:
            return
        #if it's a list we will get the first index 
        if isinstance(filePath, list):
            filePath = filePath[0]
        
        #check to see if extension is attached to the filePath
        if not filePath.endswith(SkinCluster.kFileExtension):
            filePath += SkinCluster.kFileExtension
        
        #gather the data
        self.getData()
        
        #export the data
        pyon.save(self.data, filePath)
        
    