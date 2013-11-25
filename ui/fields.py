#!/usr/bin/env python
from PyQt4 import QtGui, QtCore
import sys

class BaseField(QtGui.QWidget):
    def __init__(self, label, value = None, description = str(), parent = None):
        super(BaseField, self).__init__(parent)
        
        self.__label = QtGui.QLabel(label)
        self.__value = value
        self.__description = self.setAccessibleDescription(description)
    
    def label(self):
        return self.__label
    
    def labelText(self):
        return self.__label.text()
    
    def setLabel(self, value):
        self.__label.setText(value)
    
    def value(self):
        return self.__value
    
    def setValue(self,value):
        self.__value = value
        
    def setDescription(self, value):
        '''
        Sets the description of the current field
        
        @param value: String describing the field
        @type value: *str* or *QString*  
        '''
        #Check type
        if not isinstance(value, basestring) and not isinstance(value, QtCore.QString):
            raise TypeError('%s must be  a string or QString' % value)
        
        #set values
        self.__description = value
        self.setDescription(value)
        
        
class LineEditField(BaseField):
    def __init__(self, *args, **kwargs):
        super(LineEditField, self).__init__(*args,**kwargs)
        
        self._layout = QtGui.QHBoxLayout()
        self._lineEdit = QtGui.QLineEdit()
        #set text if any value
        if self.value():
            self.setText(self.value())
        
        self._lineEdit.textChanged.connect(self.setText)
        
        self._layout.addWidget(self.label())
        self._layout.addWidget(self._lineEdit)
        self._layout.addStretch()
        self.setLayout(self._layout)
        
    def setText(self, value):
        '''
        Sets the text for the QLineEdit
        '''
        if not isinstance(value, basestring) and not isinstance(value, QtCore.QString):
            raise TypeError('%s must be an string' % value)
        #get the souce of the call for setText function
        source = self.sender()
        print value
        
        #set the value on field
        self.setValue(value)
        #set lineEdit text
        if not source == self._lineEdit:
            self._lineEdit.setText(value)
        

        
class IntField(BaseField):
    def __init__(self, label, value = 0, description = str(), parent = None, min = -100, max = 100):
        super(IntField, self).__init__(label, value, description, parent)
        
        self._layout = QtGui.QHBoxLayout()
        self._intBox = QtGui.QSpinBox()
        self._intBox.setRange(min,max)
        self._layout.addWidget(self.label())
        if value:
            self._intBox.setValue(value)
        
        self._intBox.valueChanged.connect(self.setValue)
        self._layout.addWidget(self._intBox)
        self._layout.addStretch()
        self.setLayout(self._layout)
        
        
    def setValue(self, value):
        '''
        Sets the text for the QLineEdit
        '''
        if not isinstance(value, int):
            raise TypeError('%s must be an integer' % value)
        
        #get the source of where the function is being called
        source = self.sender()
        
        #set field value
        super(IntField, self).setValue(value)
        #set spinBox value
        if not source == self._intBox:
            self._intBox.setValue(value)
        
    def value(self):
        value = self._intBox.value()
        super(IntField, self).setValue(value)
        
        return super(IntField,self).value()
                        
