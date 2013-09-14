'''
This is the joint module for all the joint utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

#import python modules
import os
import sys

import maya.cmds as cmds
import japeto.libs.common as common

def create(name, parent = None, position = [0,0,0]):
    '''

    @param name:
    @param position:
    @param parent: parent of created joint
    @type parent: *str*
    '''

    #clear selection
    cmds.select(cl = True)

    if parent:
        if not cmds.objExists(parent):
            cmds.createNode('transform', n = parent)
        #if parent, create joint under parent and position
        jnt = cmds.joint(n = name)
        cmds.parent(jnt, parent)
        cmds.xform(parent, ws = True, t = position)
        return jnt

    #if no parent, just create joint at position
    jnt = cmds.joint(n = name, position = position)

    return jnt

def orientToRotate (joint):
    '''
    Transfers the joint orientation values to euler rotation

    @param joint: Joint(s) you want to do the transfer for
    @type joint: *str* or *list*
    '''
    sArrJoints = [joint] #common.toList(joint)

    for j in sArrJoints:
        if cmds.objectType(j)=='joint':
            doit=True
            for attr in ['rx','ry','rz','jox','joy','joz','ro']:
                #lock,or connected
                if cmds.getAttr(j+'.'+attr,l=True) or cmds.listConnections('%s.%s' % (j,attr), destination = False, plugs = True):
                    doit=False
            if doit:
                ori = cmds.xform(j,q=True,ws=True,ro=True)
                cmds.setAttr(j+'.jo',0,0,0)
                cmds.xform(j,ws=True,ro=ori)

            else:
               cmds.warning('%s attributes are locked and unable to change rotation') 

def rotateToOrient (joint):
    '''
    Transfer the euler rotate values to the joint orientation

    @param joint: Joint(s) you want to do the transfer for
    @type joint: *str* or *list*
    '''
    sArrJoints = [joint]#common.toList(joint)

    for j in sArrJoints:
        if cmds.objectType(j)=='joint':
            doit=True
            for attr in ['rx','ry','rz','jox','joy','joz','ro']:
                #don't exists, lock,or connected
                if cmds.getAttr(j+'.'+attr,l=True) or cmds.listConnections('%s.%s' % (j,attr), destination = False, plugs = True):
                    doit=False

            if doit:
                roo = cmds.xform(j,q=True,roo=True)#get rotation order
                cmds.xform(j, p=True, roo='xyz' )#set rotation order to default (joint orient only works with xyz rotation order)
                orientToRotate(j)#transfer current joint orient to rotate
                ori = cmds.getAttr(j+'.r')[0]
                cmds.setAttr(j+'.jo',ori[0],ori[1],ori[2])
                cmds.setAttr(j+'.r',0,0,0)
                cmds.xform(j, p=True, roo=roo )#set back the initial rotation order
            else:
                print ('//Warning: "' + j + '" is locked or connected, unable to set rotation')


def mirror (joint, search = common.LEFT, replace = common.RIGHT, axis = "x"):
    '''
    Mirror joint orientation
    *It won't create a new joint, it will only mirror the oriention from one existing joint to another.

    .. python ::

        mirror( cmds.ls(sl=True) )

    @param joint: Joint you want to mirror
    @type joint: *str* or *list*

    @param search: Search side token
    @type search: *str*

    @param replace: Replace side token
    @type replace: *str*

    @param axis: Mirror plane axis, for example **x**
    @type axis: *str*
    '''

    # get given joints
    joints = common.toList(joint)

    # get selection
    selection = cmds.ls(sl=True)

    posVector = ()
    oriVector = ()
    if axis.lower() == 'x':
        posVector = (-1,1,1)
        oriVector = (0,180,180)
    elif axis.lower() == 'y':
        posVector = (1,-1,1)
        oriVector = (180,0,180)
    elif axis.lower() == 'z':
        posVector = (1,1,-1)
        oriVector = (180,180,0)

    for i in range(len(joints)):

        obj1 = joints[i]
        obj2 = joints[i].replace( search, replace )

        if cmds.objExists(obj1) and cmds.objExists(obj2) and obj1 != obj2:

            # parent children
            jointGroup = cmds.createNode('transform')
            children   = cmds.listRelatives( obj2, type='transform' )
            if children:
                cmds.parent( children, jointGroup )

            # get position and rotation
            pos = cmds.xform( obj1, q=True, rp=True, ws=True )
            ori = cmds.xform( obj1, q=True, ro=True, ws=True )

            # set rotation orientation
            cmds.xform( obj2, ws = True, t = ( pos[0]*posVector[0], pos[1]*posVector[1], pos[2]*posVector[2] ), ro=ori )
            cmds.xform( obj2, ws = True, r = True, ro = oriVector )

            # set prefered angle
            if cmds.objExists( '%s.%s' % (obj1, 'preferredAngle') ):
                prefAngle = cmds.getAttr( '%s.%s' % (obj1, 'preferredAngle') )[0]
                if cmds.objExists( '%s.%s' % (obj2, 'preferredAngle') ):
                    cmds.setAttr( '%s.%s' % (obj2, 'preferredAngle'),
                                  prefAngle[0],
                                  prefAngle[1],
                                  prefAngle[2] )

            # re-parent
            if children:
                cmds.parent( children, obj2 )
            cmds.delete( jointGroup )

        else:
            raise RuntimeError, 'Node not found: %s' % obj2

    # --------------------------------------------------------------------------
    # re-select objects
    if selection:
        cmds.select( selection )
    else:
        cmds.select( cl= True)
