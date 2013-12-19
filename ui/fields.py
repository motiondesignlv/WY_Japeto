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
                        
class VectorField(BaseField):
    def __init__(self, *args, **kwargs):
        super(VectorField, self).__init__(*args,**kwargs)
        
        self._layout = QtGui.QHBoxLayout()
        self._valueLayout = QtGui.QVBoxLayout()
        self._xField = LineEditField(label = 'X', value = str(0.0))
        self._yField = LineEditField(label = 'Y', value = str(0.0))
        self._zField = LineEditField(label = 'Z', value = str(0.0))
        self._valueLayout.addStretch()
        self._valueLayout.addWidget(self._xField)
        self._valueLayout.addWidget(self._yField)
        self._valueLayout.addWidget(self._zField)
        self._valueLayout.addStretch()
        self._layout.addWidget(self.label())
        self._layout.addLayout(self._valueLayout)

        #set text if any value
        if self.value():
            if isinstance(self.value(), list) or isinstance(self.value(), tuple):
                if len(self.value()) < 3 or len(self.value()) > 3:
                    raise TypeError('%s must be a list of 3 values' % self.value())
            #set the values on the individual fields
            self._xField.setText(str(self.value()[0]))
            self._yField.setText(str(self.value()[1]))    
            self._zField.setText(str(self.value()[2]))
        
        self.setLayout(self._layout)
    
    def value(self):
        value = (float(self._xField.value()), float(self._yField.value()), float(self._zField.value()))
        super(VectorField, self).setValue(value)
        
        return super(VectorField,self).value()
    
class BooleanField(BaseField):
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self._layout = QtGui.QHBoxLayout()
        self._checkBox = QtGui.QCheckBox()
        self._checkBox.toggled.connect(self.setValue)
        self._layout.addWidget(self.label())
        self._layout.addWidget(self._checkBox)

    def setValue(self, value):
        self._checkBox.blockSignals(True)
        if value:
            self._checkBox.setCheckState(QtCore.Qt.Checked)
        else:
            self._checkBox.setCheckState(QtCore.Qt.Unchecked)
        self._checkBox.blockSignals(False)

    def value(self):
        return self._checkBox.checkState()

