'''
Created on Jun 28, 2014

@author: Eddy Hintze
'''
import sys
import os
import time
import serial
from serial.tools import list_ports

from ledController import LedController

from PyQt4 import QtGui, QtCore

def ListSerialPorts():
    """
    Returns a generator for all available serial ports
    """
    if os.name == 'nt':
        # windows
        for i in range(256):
            try:
                s = serial.Serial(i)
                s.close()
                yield 'COM' + str(i + 1)
            except serial.SerialException:
                pass
    else:
        # unix
        for port in list_ports.comports():
            yield port[0]
            
            
class Window(QtGui.QWidget):
    
    def __init__(self):
        super(Window, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        

        mainVBox = QtGui.QVBoxLayout()
        mainVBox.addWidget(self.createTabs())
          
        self.setLayout(mainVBox)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('LED Controller')    
        self.show()
        
    def createTabs(self):
        tabs = QtGui.QTabWidget()
        #Create a tab for each controller
        tabList = []
        for key in ctrl.keys():
            tabList.append( QtGui.QWidget() )
            tabs.addTab(tabList[-1], ctrl[key].getModel())
            tabs.setTabToolTip(len(tabList)-1, ctrl[key].getPort())
            
        #Create a trigger list for each controller (tab)
        cbEnable = {}
        txtCommand = {}
        sbInt = {}
        for tabIdx in xrange(len(tabList)):
            key = str(tabs.tabToolTip(tabIdx))
            cbEnable[key] = []
            txtCommand[key] = []
            sbInt[key] = []
            tabGrid = QtGui.QGridLayout()
            gbTriggers = QtGui.QGroupBox("Triggers")
            #Create a trigger
            for triggerIdx in xrange(ctrl[key].getLedCount()):
                triggerGrid = QtGui.QGridLayout()
                
                cbEnable[key].append(QtGui.QCheckBox(""))
                lblCommand = QtGui.QLabel("LED "+str(triggerIdx+1)+" Command:")
                txtCommand[key].append(QtGui.QLineEdit())
                lblInt = QtGui.QLabel("Interval: ")
                sbInt[key].append(QtGui.QSpinBox())
                sbInt[key][-1].setMaximum(60)
                sbInt[key][-1].setMinimum(1)
                lblIntMin = QtGui.QLabel("min")
                
                triggerGrid.addWidget(cbEnable[key][triggerIdx], 0, 0)
                triggerGrid.addWidget(lblCommand, 0, 1, QtCore.Qt.AlignRight)
                triggerGrid.addWidget(txtCommand[key][triggerIdx], 0, 2, 1, 2)
                triggerGrid.addWidget(lblInt, 1, 1, QtCore.Qt.AlignRight)
                triggerGrid.addWidget(sbInt[key][triggerIdx], 1, 2)
                triggerGrid.addWidget(lblIntMin, 1, 3)
                triggerGrid.setColumnStretch(3,4)
                
                tabGrid.addLayout(triggerGrid, triggerIdx, 0)
                
            #create blank row at bottom to stretch    
            tabGrid.addWidget(QtGui.QLabel(""), triggerIdx+1, 0,)
            tabGrid.setColumnStretch(triggerIdx+1, 4) 
            #add trigger list to a GroupBox
            gbTriggers.setLayout(tabGrid)
            #add the groupbox to the tab
            tabVBox = QtGui.QVBoxLayout()
            tabVBox.addWidget(gbTriggers)
            tabList[tabIdx].setLayout(tabVBox)
            
        return tabs

def listControllers():
    """
    Returns a dict of all LED Controllers pluged in
    """
    device = {}
    #Get list of serial ports and find any LED Controllers
    for port in ListSerialPorts():
        device[port] = LedController()
        feedback = device[port].connect(port)
        #if it is not a controller remove it from the list
        if feedback[:2] != 'XN':
            del device[port]
    return device         
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

if __name__ == '__main__':
    
    #dict to store active controllers in
    ctrl = listControllers()    
    #for testing only
    ctrl['COM555'] = LedController()
    ctrl['COM555'].model = 'XN-LED4-rj5d'
    ctrl['COM555'].ledCount = 4
    ctrl['COM555'].port = 'COM555'
    ctrl['COM555'].isConn = True
    ctrl['COM666'] = LedController()
    ctrl['COM666'].model = 'XN-LED3-js6e'
    ctrl['COM666'].ledCount = 3
    ctrl['COM666'].port = 'COM666'
    ctrl['COM666'].isConn = True
    main()
    
    
    
    
    
    
    
    
    
    
    
    