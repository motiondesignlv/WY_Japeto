'''
This is the Spine component.

:author:  Walter Yoder
:contact: walteryoder@gmail.com
:date:    September 2013
'''
#import maya modules
import maya.cmds as cmds

#import package modules
from japeto.libs import common
from japeto.libs import attribute
from japeto.libs import ikfk
from japeto.libs import control
from japeto.libs import transform
from japeto.libs import joint
from japeto.libs import curve
from japeto.libs import surface
reload(surface)

from japeto.components import component
from japeto.components import chain
reload(component)
reload(transform)


class Spine(chain.Chain):
    def __init__(self, name):
        super(Spine, self).__init__(name)
        
    
    @component.overloadArguments
    def initialize(self,**kwargs):
        super(Spine,self).initialize(**kwargs)
        
        #TODO: Place builds arguments specific to the spine

    def setupRig(self):
        super(Spine, self).setupRig()
        
    def rig(self):
        super(Spine, self).rig()
        
        pointList = list()
        
        #inbetweenNodes = common.getInbetweenNodes(self.ikfkChain.ikJoints[0], self.ikfkChain.ikJoints[-1])
        pointList.append(cmds.xform(self.ikfkChain.ikJoints[0], q = True, ws = True, rp = True))
        for i,jnt in enumerate(self.ikfkChain.ikJoints):
            if jnt == self.ikfkChain.ikJoints[-1]:
                break
            #end if
            pointList.append(transform.averagePosition([jnt, self.ikfkChain.ikJoints[i+1]]))
        #end loop 
        pointList.append(cmds.xform(self.ikfkChain.ikJoints[-1], q = True, ws = True, rp = True))
        #spineCurve = curve.createFromPoints(pointList, degree = 3)
        spineSurface = surface.createFromPoints(pointList, name = '%s_%s' % (self.name,common.SURFACE))
        surface.createFollicle(spineSurface, name = spineSurface.replace(common.SURFACE, common.FOLLICLE), U = .5, V = .5)