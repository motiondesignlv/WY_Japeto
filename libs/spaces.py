'''
Spaces Library

:author: 
:contact:  
'''
# ------------------------------------------------------------------------------
# Import Python Modules

# Import Maya modules
import maya.cmds as cmds

# Import rigtools modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import transform

# ------------------------------------------------------------------------------
# Create Space Switching Function
def create( spaceNode, spaceAttrNode = None , parent=None ):
    '''
    Create space switcher

    :param spaceNode: Transform node to be constrained.
    :type spaceNode: *str*
    :param spaceAttrNode: Node where the 'space' attribute is going to be created.
    :type spaceAttrNode: *str*
    :param parent: Parent for the spaces group.
    :type parent: *str*
    :return: Spaces group
    :rtype: *str*
    '''
    # Load decompose matrix plugin

    # get attribute spaceNode
    if spaceAttrNode == None:
        spaceAttrNode = spaceNode

    # check if exists
    if cmds.objExists( '%s.spaceGrp' % spaceNode ):
        raise RuntimeError, 'This node has spaces already. Use addSpace instead'

    # --------------------------------------------------------------------------
    # CREATE GROUP
    #
    grp = cmds.createNode('transform',n='%s%s' % (spaceNode,'Spaces'), parent=parent  )
    cmds.setAttr('%s.%s' % (grp,'inheritsTransform'),False)
    decomMatrixNode = cmds.createNode('decomposeMatrix')
    cmds.connectAttr( '%s.%s' % (spaceNode,'parentMatrix'), '%s.%s' % (decomMatrixNode,'inputMatrix') )
    cmds.connectAttr( '%s.%s' % (decomMatrixNode,'outputTranslate'), '%s.%s' % (grp,'translate') )
    cmds.connectAttr( '%s.%s' % (decomMatrixNode,'outputRotate'), '%s.%s' % (grp,'rotate') )
    cmds.connectAttr( '%s.%s' % (decomMatrixNode,'outputScale'), '%s.%s' % (grp,'scale') )

    # --------------------------------------------------------------------------
    # CREATE LOCAL SPACE
    #
    attribute.addAttr( spaceAttrNode, 'space', attrType='enum', defValue=['local'] )
    localSpace = cmds.createNode('transform', name='%s_%s' % (grp,'local'), parent=grp)
    transform.matchXform( localSpace, spaceNode, 'pose' )
    attribute.lockAndHide( ['t','r','s','v'], localSpace )

    # --------------------------------------------------------------------------
    # CREATE CONSTRAINT
    #
    constraint = cmds.parentConstraint( localSpace, spaceNode )[0]

    # --------------------------------------------------------------------------
    # CREATE MESSAGE ATTRIBUTES
    #
    # spaceAttrNode
    cmds.addAttr( spaceNode, k=True, ln='spaceAttrNode', at='message' )
    cmds.connectAttr( '%s.%s' % (spaceAttrNode,'space'), '%s.%s' % (spaceNode,'spaceAttrNode') )

    # spaceNode
    cmds.addAttr( spaceAttrNode, k=True, ln='spaceNode', at='message' )
    cmds.connectAttr( '%s.%s' % (spaceNode,'message'), '%s.%s' % (spaceAttrNode,'spaceNode') )

    # spaceGrp
    cmds.addAttr( spaceNode, k=True, ln='spaceGrp', at='message' )
    cmds.connectAttr( '%s.%s' % (grp,'message'), '%s.%s' % (spaceNode,'spaceGrp') )

    # spaceConstraint
    cmds.addAttr( spaceNode, k=True, ln='spaceConstraint', at='message' )
    cmds.connectAttr( '%s.%s' % (constraint,'message'), '%s.%s' % (spaceNode,'spaceConstraint') )
    # --------------------------------------------------------------------------

    return grp

class Spaces( object ):
    '''
    cvar spaceNode:  :
    @cvar spaceGrp:  :
    @cvar spaceAttrNode:  :
    @cvar spaceConstraint:
    '''

    def __init__( self, node ):
        super( Spaces, self ).__init__()

        # If node == spaceAttrNode
        if cmds.objExists( '%s.spaceNode' % node):
            self.spaceNode = cmds.getAttr( '%s.spaceNode' % node )
        # If node == spaceNode
        elif cmds.objExists( '%s.spaceGrp' % node ) and cmds.objExists( '%s.spaceAttrNode' % node ) and cmds.objExists( '%s.spaceConstraint' % node ):
            self.spaceNode = node
        # Else
        else:
            raise RuntimeError, 'No "space" attributes found in: "%s"' % node

        # get variables
        self.spaceGrp        = attribute.getConnections('spaceGrp', self.spaceNode, plugs = False)[0]
        self.spaceAttrNode   = attribute.getConnections('spaceAttrNode', self.spaceNode, plugs = False)[0]
        self.spaceConstraint = attribute.getConnections('spaceConstraint', self.spaceNode, plugs = False)[0]

    def __connect__( self ):
        '''Reconnects spaces with constraint
        '''

        # get spaces in constraint
        aliasList  = cmds.parentConstraint( self.spaceConstraint, q=True, weightAliasList=True )
        targetList = cmds.parentConstraint( self.spaceConstraint, q=True, targetList=True )

        # key constraint
        for i in range(len(aliasList)):

            # Create Condition Node ( R: used for weight, G: used for node state )
            condNode = cmds.createNode('condition')
            cmds.setAttr( '%s.%s' % (condNode,'operation'), 0 ) # < equal
            cmds.setAttr( '%s.%s' % (condNode,'secondTerm'), i )
            cmds.connectAttr( '%s.%s' % (self.spaceAttrNode,'space'), '%s.%s' % (condNode, 'firstTerm'), f=True )

            # Weight Condition
            cmds.setAttr( '%s.%s' % (condNode,'colorIfTrueR'), 1 )
            cmds.setAttr( '%s.%s' % (condNode,'colorIfFalseR'), 0 )
            cmds.connectAttr( '%s.%s' % (condNode,'outColorR'), '%s.%s' % (self.spaceConstraint, aliasList[i]), f=True )

    def addSpace( self , target, name=None, mode='parent'):
        '''Adds new space.

        @param target: New target for spaces.
        @type target: *str*
        @param name: Name of the target in the enum attribute.
        @type name: *str*
        @param mode: 'orient' or 'parent'
        @type mode: *str*
        '''

        # get attribute node
        if name == None:
            name = target

        # --------------------------------------------------------------------------
        # EDIT ENUM ATTRIBUTE

        # get new spaces
        existingSpaces = cmds.attributeQuery( 'space', node=self.spaceAttrNode, listEnum=True)[0].split(':')

        if name in existingSpaces or target in existingSpaces:
            raise RuntimeError, 'There is a space with that name in "%s.%s"' % (self.spaceAttrNode,'space')

        # edit enum attribute
        cmds.addAttr( '%s.%s' % (self.spaceAttrNode,'space'), e=True, enumName=':'.join(existingSpaces+[name]) )

        # --------------------------------------------------------------------------
        # create new space
        newSpace = cmds.createNode('transform', name='%s_%s' % (self.spaceGrp, name), parent=self.spaceGrp)
        transform.matchXform( newSpace, self.spaceNode, 'pose')
        #cmds.setAttr( '%s.%s' % (newSpace, 'displayLocalAxis') , True)

        if mode == 'orient':
            cmds.orientConstraint( target, newSpace, mo=True )
        else:
            cmds.parentConstraint( target, newSpace, mo=True )

        # create constraint
        constraint = cmds.parentConstraint( newSpace, self.spaceNode, mo=True )[0]

        # connect spaces
        self.__connect__()

    def removeSpace( self, space ):
        '''Removes spaces.

        @param space: Space index you want to delete.
        @type space: *int*
        '''

        # get current space
        currentSpace = cmds.getAttr( '%s.%s' % (self.spaceAttrNode,'space') )

        # ----------------------------------------------------------------------
        # edit enum attribute

        # get new spaces
        existingSpaces = cmds.attributeQuery( 'space', node=self.spaceAttrNode, listEnum=True)[0].split(':')
        if space>len(existingSpaces):
            raise IndexError, 'No space found in index: %i' % space
        newSpaces = [existingSpaces[i] for i in range(len(existingSpaces)) if i!=space]

        # edit attribute
        cmds.addAttr( '%s.%s' % (self.spaceAttrNode,'space'), e=True, enumName=':'.join(newSpaces) )

        # ----------------------------------------------------------------------
        # delete group in spacesGrp

        spaces = cmds.listRelatives( self.spaceGrp, type='transform' )
        cmds.delete( spaces[space] )

        # ----------------------------------------------------------------------
        # re- connect
        self.__connect__()

        # ----------------------------------------------------------------------
        # refresh
        if space == currentSpace:
            cmds.dgdirty( a=True )

    def switch( self, space, keyframe = False ):
        '''
        @param space: Space you want to switch on.
        @type space: *int*
        @param keyframe: Set keyframe into spaceAttrNode
        @type keyframe: *bool*
        '''

        # get current frame
        currentFrame = cmds.currentTime(q=True)
        currentSpace = cmds.getAttr( '%s.%s' % (self.spaceAttrNode,'space') )

        # ----------------------------------------------------------------------
        # get transformation ( script )
        position = cmds.xform( self.spaceAttrNode, q=True,ws=True, rp=True)
        rotation = cmds.xform( self.spaceAttrNode, q=True,ws=True, ro=True)
        localPosition = cmds.getAttr('%s.%s' % (self.spaceAttrNode,'translate'))[0]
        localRotation = cmds.getAttr('%s.%s' % (self.spaceAttrNode,'rotate'))[0]

        # ----------------------------------------------------------------------
        # key previous
        if keyframe:
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'space') , time=currentFrame-1, value=currentSpace )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'translateX'), time=currentFrame-1, value=localPosition[0] )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'translateY'), time=currentFrame-1, value=localPosition[1] )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'translateZ'), time=currentFrame-1, value=localPosition[2] )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'rotateX'), time=currentFrame-1, value=localRotation[0] )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'rotateY'), time=currentFrame-1, value=localRotation[1] )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'rotateZ'), time=currentFrame-1, value=localRotation[2] )

        # switch to new space
        cmds.setAttr( '%s.%s' % (self.spaceAttrNode,'space'), space)

        # set position
        if not attribute.isLocked('tx',self.spaceAttrNode) and not attribute.isLocked('ty',self.spaceAttrNode) and not attribute.isLocked('tz',self.spaceAttrNode):
            cmds.xform(self.spaceAttrNode,ws=True,t=position)

        # set rotation
        if not attribute.isLocked('rx',self.spaceAttrNode) and not attribute.isLocked('ry',self.spaceAttrNode) and not attribute.isLocked('rz',self.spaceAttrNode):
            cmds.xform(self.spaceAttrNode,ws=True,ro=rotation)

        # set keyframes
        if keyframe:
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'space') )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'translateX') )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'translateY') )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'translateZ') )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'rotateX') )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'rotateY') )
            cmds.setKeyframe( '%s.%s' % (self.spaceAttrNode,'rotateZ') )