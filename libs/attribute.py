'''
This is the attribute module for all the attribute utility functions

:author: Walter Yoder
:contact: walteryoder@gmail.com
:date: October 2012
'''

import maya.cmds as cmds
import japeto

import japeto.libs.common as common

def resolveArgs (attr, node = None, validate = True):
    '''
    Resolve attribute arguments

    .. python ::

    .. python ::
        resolveArgs ("testMe.translateX")
        # Result: ('testMe.translateX', 'translateX', 'testMe')

    @note: All inidcies get stripped from attribute names

    @param attr: Attribute name or path
    @type attr: *str*

    @param node: Attribute parent node
    @type node: *str*

    @param validate: Validate the existance of attribute
    @type validate: *bool*

    @return: Return attribute elements
    @rtype: *tuple*
    '''
    # Check if node is given
    if node:
        # Get attribute path
        attrPath = "%s.%s" % (node, attr)
        attrName = attr
        attrNode = node
    else:
        # Split attribute path
        attrElements = attr.split (".")

        # Check if path is valid
        if len (attrElements) < 2:
            # Raise error
            raise NameError ("Invalid attribute path!")

        # Define attribute name
        attrPath = attr
        attrName = ".".join (attrElements [1:])
        attrNode = attrElements [0]
        #attrLastName = attrElements.pop ()

    # Return attribute elements
    return (attrPath, attrName, attrNode)


def attrNodeList(attr, node):
    #Get list of nodes and attrs
    attrList = common.toList(attr)
    nodeList = common.toList(node)

    #declare function list varaibles
    attrs = list()
    nodes = list()

    #check for nodes
    if not nodeList:
		for attr in attrList:
			attrName, attrPath, attrNode = resolveArgs(attr)
			attrs.append(attrName)
			nodes.append(attrNode)
    else:
		for node in nodeList:
			for attr in attrList:
				attrName, attrPath, attrNode = resolveArgs(attr, node)
				if not attrName in attrs:
				    attrs.append(attrName)
				if not attrNode in nodes:
				    nodes.append(attrNode)

    return attrs, nodes



def lock (attr, node = None):
    '''
    Lock attributes

    .. python ::
        lock ("testMe.translateX")

    @param attr: Attribute name(s) or path(s)
    @type attr: *str* or *list*

    @param node: Attribute parent node(s)
    @type node: *str*
    '''
    # Resolve arguments to
    attrList = common.toList (attr)
    nodeList = common.toList (node)

    # Loop through nodes
    for node in nodeList:
        # Loop through attributes
        for attr in attrList:
            # Resolve attribute
            attrPath, attrName, attrNode = resolveArgs (attr, node)

            # Lock attributes
            cmds.setAttr(attrPath, lock = True)


def hide(attr, node = None):
    attrList = common.toList (attr)
    nodeList = common.toList (node)

    #loop through nodes
    for node in nodeList:
        # Loop through attributes
        for attr in attrList:
            # Resolve attribute
            attrPath, attrName, attrNode = resolveArgs (attr, node)
            # Get attribute children
            attrChildren = cmds.attributeQuery (attrName, node = attrNode, listChildren = True)

            # Check if attribute has any children
            if attrChildren:
                for childAttr in attrChildren:
                    # Hide attribute
                    cmds.setAttr ("%s.%s" % (attrNode, childAttr), keyable = False)

            else:
                cmds.setAttr(attrPath, keyable = False )


def lockAndHide(attr, node = None):
    '''
    Locks and hides specified attributes

    '''
    attrList = common.toList(attr)

    for attr in attrList:
        if node:
            lock(attr, node)
            hide(attr, node)
            continue

        attrPath, attrName, attrNode = resolveArgs (attr, node)
        lock(attrPath)
        hide(attrPath)


def unlock(attr, node = str()):
    attrs, nodes = attrNodeList(attr, node)

    #lock attributes
    for node in nodes:
        for attr in attrs:
            cmds.setAttr('%s.%s' % (node, attr), l = False)


def unhide(attr, node = str()):	    
    attrs, nodes = attrNodeList(attr, node)

    #lock attributes
    for node in nodes:
        for attr in attrs:
            cmds.setAttr('%s.%s' % (node, attr), k = True)


def unlockAndUnhide(attr, node):
    unlock(attr, node)
    unhide(attr,node)


def connect(source, destination, force = True):
    '''
    connects source attribute to the destination attribute

    @param source: Attribute to grab connections
    @type source: *str*

    @param destination: Attribute to connect to
    @type destination: *str*

    @param force: Force the connection
    @type force: *bool*
    '''
    cmds.connectAttr(source, destination,f = force)

def addAttr(node, attr, attrType = 'double',keyable = True, defValue = None, min = 0, max = 0, value = None , parent = None):
    '''
    @param node: node to apply attribute to
    @type node: *str* or *unicode*

    @param attr: attribute or attributes to assign to node
    @type attr: *str* or *list* or *unicode*

    @return: attribute path
    @rtype: *str* or *list*
    '''

    attrs = attr


    if not isinstance(node, basestring):
        raise TypeError('%s must be of type *str* or *unicode*!' % node)

    if isinstance(attrs,basestring):
        attrs = [attrs]

    if not isinstance(attrs, list):
        raise TypeError('%s must be of type *list*' % attrs)

    for attr in attrs:
        if attrType == 'double':
            if defValue == None:
                defValue = 0 #set default value to 0
            if parent:
                #add attr to the parent attribute
                if not min and not max:
                    cmds.addAttr(node, ln = attr, at = attrType, keyable = keyable, dv = defValue,parent = parent)
                else:
                    cmds.addAttr(node, ln = attr, at = attrType, keyable = keyable, dv = defValue, min = min, max = max,parent = parent)
            else:
                if not min and not max:
                    cmds.addAttr(node, ln = attr, at = attrType, keyable = keyable, dv = defValue)
                else:
                    cmds.addAttr(node, ln = attr, at = attrType, keyable = keyable, dv = defValue, min = min, max = max)
        elif attrType == 'enum':
            if isinstance(defValue, str):
                enumValue = defValue
            elif isinstance(defValue, list):
                #make list in string for enumName flag
                enumValue = ':'.join(defValue)
            else:
                raise TypeError('%s is not of type list or string' % defValue)
            #add enum attribute
            cmds.addAttr(node, ln = attr,  at = attrType, en = enumValue, keyable = keyable)
        elif attrType == 'double3':
            cmds.addAttr(node, ln=attr, at = attrType)
        elif attrType == 'message':
            cmds.addAttr(node, ln = attr, at = attrType, keyable = keyable)

    if value:
        #set the value on the attribute
        cmds.setAttr('%s.%s' % (node,attr), value)
    #create new attribute
    newAttr = '%s.%s' % (node, attr)

    return newAttr

#get and set values on attributes
def getValue(attr, node = None):
    '''
    gets the values of attributes

    @param attr: attribute you want to get the value from
    @type attr: *str*

    @param node: parent node of attribute
    @type node: *str*
    '''

    attrPath, attrName, attrNode = resolveArgs (attr, node)
    return cmds.getAttr(attrPath)


# Switch Attribute Function
def switch (attr, node = None, value=0, choices = None, outputs = None):
    '''
    Create a switch attribute with the given outputs

    .. python ::

        switch ('color',node='testMe', choices=['red','green','blue'], outputs=[(1,0,0),(0,1,0),(0,0,1)] )

    This function gets the given outputs and connect them into a choice node.

    So you can switch between them with the created enum attribute.

    @param attr: Name of the enum attribute you want to create
    @type attr: *str*

    @param node: Node where the enum attribute is going to be created.
    @type node: *str*

    @param value: Default value for the attribute.
    @type value: *int*

    @param choices: Items in the enum attribute
    @type choices: *list*

    @param outputs: Output values you want to iterate.
    @type outputs: *list*

    @return: Return choice.output node.
    @rtype: *str*
    '''
    # Resolve attribute
    #attrPath, attrName, attrNode = resolveArgs (attr, node, validate = False)
    attrNode = node
    attrName = attr
    attrPath = '%s.%s' % (attrNode, attrName)

    # Create enum attribute
    addAttr (node,attr, attrType = "enum", value=value, defValue = choices)
    sChoice = cmds.createNode ("choice", name = attrNode + attrName + "Choice")
    cmds.connectAttr(attrPath, '%s.selector' % sChoice)

    # Add output attributes
    for i in range (len (outputs)):
        sAttr = "output%i" % i
        if isinstance (outputs [i],bool):
            addAttr (node = sChoice, attr = sAttr, attrType = "bool", defValue = outputs[i] )
        elif isinstance (outputs [i],int):
            addAttr (node = sChoice, attr = sAttr, attrType = "long", defValue = outputs[i] )
        elif isinstance (outputs [i],float):
            addAttr (node = sChoice, attr = sAttr, attrType = "double", defValue = outputs[i] )
        elif isinstance (outputs [i],list) or isinstance(outputs [i],tuple):
            addAttr (sChoice, sAttr, "double3")
            addAttr (sChoice, sAttr + "X", "double", defValue = outputs [i][0], parent = sAttr)
            addAttr (sChoice, sAttr + "Y", "double", defValue = outputs [i][1], parent = sAttr)
            addAttr (sChoice, sAttr + "Z", "double", defValue = outputs [i][2], parent = sAttr)

        # Connect output attribute
        cmds.connectAttr(sChoice + "." + sAttr, '%s.input[%s]' % (sChoice, i), f = True)

    # Return new switch output attribute
    return sChoice + ".output"


# ------------------------------------------------------------------------------
# Connection Functions
def isConnected (attr, node = None, incoming = True, outgoing = True):
    '''
    Check if attribute is connected

    .. python ::
        isConnected ("testMe.translateX")
        # Result: False

    @param attr: Attribute name or path
    @type attr: *str*

    @param node: Attribute parent node
    @type node: *str*

    @return: Return status
    @rtype: *bool*
    '''
    # Resolve attribute
    attrPath = resolveArgs (attr, node) [0]

    # Check if attribute is connected
    if outgoing and cmds.connectionInfo (attrPath, isSource = True):
        return True
    elif incoming and cmds.connectionInfo (attrPath, isDestination = True):
        return True
    else:
        return False


def getConnections (attr, node = None, incoming = True, outgoing = True, plugs = True):
    '''
    Get attribute connections

    .. python ::

    getConnections ("testMe.translateX")
    # Result: None

    @param attr: Attribute name or path
    @type attr: *str*

    @param node: Attribute parent node
    @type node: *str*

    @param incoming: Get incoming connections
    @type incoming: *bool*

    @param outgoing: Get outgoing connections
    @type outgoing: *bool*

    @param plugs: Include attribute names in output
    @type plugs: *bool*

    @return: Return connections
    @rtype: *list*
    '''
    # Check if attribute is connected
    if isConnected (attr, node):
        # Resolve attribute
        attrPath = resolveArgs (attr, node) [0]

        return cmds.listConnections (attrPath, shapes = True, plugs = plugs, skipConversionNodes = True, source = incoming, destination = outgoing)
    else:
        return None



def copy(attr, node = None, destination = None, connect = False, reverseConnect = True, newName = None):
    '''
    Copy attribute to another object

    @param attr: Attribute name(s) or path(s)
    @type attr: *str* or *list*

    @param node: Attribute parent node
    @type node: *str*

    @param destination: Attribute destination node
    @type destination: *str*

    @param connect: Connect copied attributes to original
    @type connect: *bool*

    @param newName: New attribute name
    @type newName: *str*

    @return: Return copy attribute path
    @rtype: *str*
    '''
    attrList = common.toList(attr)

    for attr in attrList:
        attrPath, attrName, attrNode = resolveArgs(attr, node)

        attrType = cmds.getAttr(attrPath, type = True)

        # Get default value
        defValue = cmds.addAttr (attrPath, query = True, defaultValue = True)

        # Get enum items 
        if attrType == 'enum':
            defValue = cmds.attributeQuery( attr, node = attrNode, listEnum=True)[0].split(':')

        # Add new attribute
        if newName != None:
            copyAttr = addAttr (destination, newName, attrType = attrType, defValue = defValue, min = getAttrMin(attrPath), max = getAttrMax(attrPath))
        else:
            copyAttr = addAttr (destination, attrName, attrType = attrType, defValue = defValue, min = getAttrMin(attrPath), max = getAttrMax(attrPath))

        # Set visibility
        keyable    = cmds.getAttr( attrPath, keyable=True )
        channelBox = cmds.getAttr( attrPath, channelBox=True )
        cmds.setAttr( copyAttr, keyable=keyable, channelBox=channelBox )
        # connect
        if connect:
            # Connect new attribute to old
            cmds.connectAttr(copyAttr, attrPath, f = True)
        elif reverseConnect:
            # Connect old attribute to new
            cmds.connectAttr(attrPath, copyAttr, f = True)
        else:
            # Copy attribute value
            cmds.setAttr(copyAttr, cmds.getAttr(attrPath))

    # Return new attribute path
    return copyAttr



def getAttrMin(attr, node = None):
    attrPath, attrName, attrNode = resolveArgs(attr, node)
    # Return minimum value
    return cmds.addAttr (attrPath, query = True, min = True)


def getAttrMax(attr, node = None):
    attrPath, attrName, attrNode = resolveArgs(attr, node)
    # Return minimum value
    return cmds.addAttr (attrPath, query = True, max = True)