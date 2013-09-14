'''
This modules contains the class that handles Puppet nodes
'''
#import python modules

#import Maya modules
import maya.cmds as cmds
import maya.OpenMaya as om

#import package modules
import japeto.libs.common as common

#Constant Variables
PUPPET     = 'Puppet' 
TAGNAME    = 'puppet_nodes'


class Puppet(object):
    def __init__(self, mobject):
        #if string is passed 
        if isinstance(mobject, basestring):
            mobject = common.getMObject(mobject)
        
        try:
            self.__mobject = mobject
            self.__mFnNode = om.MFnDependencyNode(self.__mobject)
        except:
            raise RunTimeError('%s must be an *OpenMaya.MObject* or *str*. Puppet object not constructed' % mobject)
  
    #-----------------------------
    #GETTERS
    #-----------------------------
    def name(self):
        return self.__mFnNode.name()
    
    def fullPathName(self):
        return common.fullPathName(self.__mFnNode.name())
        
    #-----------------------------
    #Private Functions
    #-----------------------------
    
    #-----------------------------
    #Tagging Functions
    
    def tagNode(self):
        '''
        Tags the node to be a puppet node
        '''
        global TAGNAME, PUPPET
        cmds.addAttr(self.fullPathName(), ln = TAGNAME, at = 'message', k = True)
        cmds.connectAttr('%s.%s' % (PUPPET,TAGNAME), '%s.%s' % (self.fullPathName(), TAGNAME), f = True)
        
        
    def unTagNode(self):
        '''
        Untags the node so it is no longer a puppet node
        '''
        global TAGNAME
        
        #get path
        tagPath = '%s.%s' % (self.fullPathName(), TAGNAME)
        
        #check to see if path exists
        if cmds.objExists(tagPath):
            cmds.deleteAttr(tagPath)
        #end if
        
    def addChild(self, child):
        '''
        adds nodes as a child object
        '''
        cmds.parent(child, self.fullPathName())
        
    def storeArgs(self, **kwargs):
        cmds.addAttr(self.fullPathName(), ln = 'buildArgs', dt = 'string')
        cmds.setAttr('%s.buildArgs' % self.fullPathName(), '%s' % kwargs, type = 'string')
    
    def restoreArgs(self, object):
        object.initialize(**eval(cmds.getAttr('%s.buildArgs' % self.fullPathName())))
        
    
    ##-----------------------------
    #Utility Functions



def create(name):
    '''
    Creation of a puppet node
    
    Example:
        ...python:
            puppet.create('l_leg')
            #Result: puppet.Puppet object
    
    @param name: Name of the puppet node
    @type name: *str*
    
    @return: puppet.Puppet object
    @rtype: *Puppet*
    '''
    global PUPPET, TAGNAME
    
    name = common.checkName(name)
    
    #create a transform node with the name passed
    mFnDependNode = om.MFnDependencyNode() #create MFnDependency Node object
    
    #if puppet node does not exist, create one
    if not common.isValid(PUPPET):
        puppetObject = mFnDependNode.create('transform', PUPPET)
        cmds.addAttr(PUPPET, ln = TAGNAME, at = 'message')
    #end if

    #create
    cmds.createNode('transform', name = name) #create transform
    #mFnDependNode.setName(name) #set name
    
    #return an asset object
    newPuppetNode = Puppet(name)
    
    #parent node to puppet
    cmds.parent(newPuppetNode.fullPathName(), PUPPET)
    
    #tag puppet nodes
    newPuppetNode.tagNode()
    
    return newPuppetNode

def restorePuppetNodes():
    global PUPPET
    #declare empty dictionary for restored nodes
    restoredNodes = dict()
    
    #check for a PUPPET node
    if not common.isValid(PUPPET):
        raise RunTimeError('%s does not exist in your scene! You need a %s node to restore puppet nodes' % (PUPPET, PUPPET))
    #end if
    
    #get the children of PUPPET
    children = common.getChildren(PUPPET)
    
    #check to see if there are any children, if not, raise a warning and return nothing
    if not children:
        cmds.warning('%s has no child puppet nodes to restore!' % PUPPET)
        return False
    #end if
    
    #If nodes exist then place them in the restored dictionary
    for node in children:
        restoredNodes[node] = Puppet(node)
        
    return restoredNodes