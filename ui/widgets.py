'''
japeto UI classes 
'''
import fields 

#PyQt modules
from PyQt4 import QtGui
from PyQt4 import QtCore

#python modules
import os

#Japeto modules
from japeto import templates
from japeto.templates import rig
from japeto.ui import models

#import maya modules
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import OpenMayaUI
from maya import cmds

#sip module
import sip

def getMayaWindow():
    #Get the maya main window as a QMainWindow instance
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

    
class FileView(QtGui.QTreeView):
    def __init__(self, parent = None):
        super(FileView, self).__init__(parent)
        
        self.setAlternatingRowColors(True)
        self._model = models.FileGraphModel()
        self.setModel(self._model)
        self.expandAll()
        

class InheritTemplateDialog(QtGui.QDialog):
    '''
    Dialog used for loading graphs or templates that have been saved or written
    '''
    def __init__(self, parent = None):
        super(InheritTemplateDialog, self).__init__(parent)
        self.parentTemplate = None
        
        layout = QtGui.QVBoxLayout()
        buttonLayout = QtGui.QHBoxLayout()
        self.okButton = QtGui.QPushButton('Ok')
        self.closeButton = QtGui.QPushButton('Close')
        
        
        self.closeButton.clicked.connect(self._close)
        self.okButton.clicked.connect(self._getChosenTemplate)
        
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(self._getTemplates())
        
        self.templateNameLineEdit = fields.LineEditField('New Template Name')
        
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.closeButton)
        layout.addWidget(self.templateNameLineEdit)
        layout.addWidget(self.comboBox)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def _getTemplates(self):
        '''
        Get all the templates on disk
        '''
        nullFiles = ['__init__.py']
        files = os.listdir(templates.__path__[0])
        fileList = list()
        for file in files:
            if file not in nullFiles and '.pyc' not in file:
                if '.py' in file and file not in fileList:
                    fileList.append(file.split('.')[0])
                #end if
            
        #end loop
        return fileList
    
    def _close(self):
        '''
        Closes to the dialog
        '''
        self.close()
        
    def _getChosenTemplate(self):
        '''
        Assigns the chosen template to the template attribute on this dialog
        '''
        self.parentTemplate = self.comboBox.currentText()
        self.close()


class LoadTemplateDialog(QtGui.QDialog):
    '''
    Dialog used for loading graphs or templates that have been saved or written
    '''
    __caption__ = 'Load Template'
    __filter__  = '*.py'
    __defaultPath__ = templates.__path__[0]
    def __init__(self, parent = None):
        super(LoadTemplateDialog, self).__init__(parent)
        self.template = None
        self.templateFile = LoadTemplateDialog.__defaultPath__
        
        layout = QtGui.QVBoxLayout()
        searchLayout = QtGui.QHBoxLayout()
        buttonLayout = QtGui.QHBoxLayout()
        
        self.searchButton = QtGui.QPushButton('...')
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(self._getTemplates())
        self.searchButton.clicked.connect(self._getTemplateFile)
        
        self.okButton = QtGui.QPushButton('Ok')
        self.closeButton = QtGui.QPushButton('Close')
        
        self.closeButton.clicked.connect(self._close)
        self.okButton.clicked.connect(self._getChosenTemplate)
        
        searchLayout.addWidget(self.comboBox)
        searchLayout.addWidget(self.searchButton)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.closeButton)
        layout.addLayout(searchLayout)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)
        
    def _getTemplates(self):
        '''
        Get all the templates on disk
        '''
        nullFiles = ['__init__.py']
        files = os.listdir(LoadTemplateDialog.__defaultPath__)
        fileList = list()
        for file in files:
            if file not in nullFiles and '.pyc' not in file:
                if '.py' in file and file not in fileList:
                    fileList.append(file.split('.')[0])
                #end if
            
        #end loop
        return fileList
    
    def _getTemplateFile(self):
        filepath = str(QtGui.QFileDialog.getOpenFileName(parent = self.parent(), caption = self.__caption__,
                                                         directory = cmds.workspace(q = True, dir = True), 
                                                         filter = self.__filter__))
        
        #if no file name we will exit the function
        if not filepath:
            return False
        
        #seperate the fileName from the extension so we can attach the proper extension
        fileName, fileExt = os.path.splitext(filepath)
        
        self.template = fileName.split('/')[-1]
        self.templateFile = filepath.replace("/%s%s" % (self.template, fileExt), "/")
        print self.templateFile
        self.comboBox.addItem(self.template)
        self.comboBox.setCurrentIndex(self.comboBox.count() - 1)
        
        return True
    
    def _close(self):
        '''
        Closes to the dialog
        '''
        self.close()
        
    def _getChosenTemplate(self):
        '''
        Assigns the chosen template to the template attribute on this dialog
        '''
        self.template = self.comboBox.currentText()
        templateFile = "%s%s" % (self.template,LoadTemplateDialog.__filter__.replace('*.', '.'))
        if not templateFile in os.listdir(self.templateFile):
            self.templateFile = LoadTemplateDialog.__defaultPath__
        
        self.templateFile = os.path.join(self.templateFile,templateFile)
        self.close()


class SaveTemplateDialog(QtGui.QFileDialog):
    '''
    This is the dialog used for saving our graphs/templates
    '''
    __caption__ = 'Save Template'
    __filter__  = '*.py'
    
    def __init__(self, parent = None, directory = str()):
        super(SaveTemplateDialog, self).__init__(parent, self.__caption__, directory, self.__filter__)
        
        self.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        self.setDefaultSuffix('.py')
        self._fileName = str()
        
    def show(self):
        '''
        Shows the fileDialog and sets the _fileName attribute from the user input 
        '''
        #Bring up the file dialog box and return the file that is being saved if any
        fileName = str(self.getSaveFileName(parent = self.parent(), caption = self.__caption__, directory = str(self.directory().absolutePath()), filter = self.__filter__))
        
        #if no file name we will exit the function
        if not fileName:
            return False
        
        #seperate the fileName from the extension so we can attach the proper extension
        fileName, fileExt = os.path.splitext(fileName)

        #make sure the file hase the extension
        self._fileName = '%s%s' % (fileName, self.defaultSuffix())
        
        return True
        
    def saveFile(self, data):
        '''
        Saves the file specified through the dialog writing the data passed in.
        This is used by for writing the graph/template in the JapetoWindow
        
        :see: JapetoWindow._saveTemplate
        
        :param data: Data/graph/template to be written to the file
        :type data: str        
        '''
        if not self._fileName:
            raise RuntimeError("No file path specified")
        '''
        if not isinstance(data, str):
            raise TypeError("Data passed in must be passed as a string")
        '''
        print "Saving %s" % self._fileName

        #write the data to the file
        rig.Rig.saveTemplate(data, self._fileName)