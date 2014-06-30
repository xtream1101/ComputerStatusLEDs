'''
Created on Jun 28, 2014

@author: Eddy Hintze
'''
import sys
import os
import time
import serial
from serial.tools import list_ports
import subprocess
import atexit

from ledController import LedController
from kthread import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *


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
            


class myCheckBox(QCheckBox):
    """
    Stores the checkbox objects for use when toggled
    """
    def data(self, port, led):
        self.port = port
        self.led = led
        self.key = self.port+''+str(self.led)
        
    def runCommand(self):
        while True:
            #get output from the command
            output = subprocess.check_output(str(self.command))
            #build command to send to the controller
            cmd = str(self.led) + '' + output
            ctrl[self.port].sendCommand(cmd)
            time.sleep(self.min)
            
    @pyqtSlot(int)
    def checkedSlot(self,state):
        if state != 2:
            #if checkbox gets unchecked, kill the thread.
            cmdThread[self.key].kill()
            del(cmdThread[self.key])
        else:
            self.command = txtCommand[self.port][self.led-1].text()
            self.min = sbMin[self.port][self.led-1].value()
            #start thread         
            cmdThread[self.key] = KThread(target=self.runCommand);
            cmdThread[self.key].start()
        

            
class Window(QWidget):
    
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()
        
    def initUI(self):
        mainVBox = QVBoxLayout()
        mainVBox.addWidget(self.createTabs())
          
        self.setLayout(mainVBox)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('LED Controller')    
        self.show()
        
    def createTabs(self):
        global txtCommand, sbMin
        
        tabs = QTabWidget()
        #Create a tab for each controller
        tabList = []
        for key in ctrl.keys():
            tabList.append( QWidget() )
            tabs.addTab(tabList[-1], ctrl[key].getModel())
            tabs.setTabToolTip(len(tabList)-1, ctrl[key].getPort())
            
        #Create a trigger list for each controller (tab)
        cbEnable = {}
        txtCommand = {}
        sbMin = {}
        for tabIdx in xrange(len(tabList)):
            key = str(tabs.tabToolTip(tabIdx))
            cbEnable[key] = []
            txtCommand[key] = []
            sbMin[key] = []
            tabGrid = QGridLayout()
            gbTriggers = QGroupBox("Triggers")
            #Create a trigger
            for triggerIdx in xrange(ctrl[key].getLedCount()):
                triggerGrid = QGridLayout()
                
                cbEnable[key].append(myCheckBox())
                #Save the port and led number to know which checkbox was clicked
                cbEnable[key][triggerIdx].data(key, triggerIdx+1)
                #Create an action for the checkbox
                self.connect(cbEnable[key][triggerIdx],SIGNAL("stateChanged(int)"),cbEnable[key][triggerIdx],SLOT("checkedSlot(int)"))
                
                lblCommand = QLabel("LED "+str(triggerIdx+1)+" Command:")
                txtCommand[key].append(QLineEdit())
                lblInt = QLabel("Interval: ")
                sbMin[key].append(QSpinBox())
                sbMin[key][triggerIdx].setMaximum(60)
                sbMin[key][triggerIdx].setMinimum(1)
                lblMin = QLabel("min")

                triggerGrid.addWidget(cbEnable[key][triggerIdx], 0, 0)
                triggerGrid.addWidget(lblCommand, 0, 1, Qt.AlignRight)
                triggerGrid.addWidget(txtCommand[key][triggerIdx], 0, 2, 1, 2)
                triggerGrid.addWidget(lblInt, 1, 1, Qt.AlignRight)
                triggerGrid.addWidget(sbMin[key][triggerIdx], 1, 2)
                triggerGrid.addWidget(lblMin, 1, 3)
                triggerGrid.setColumnStretch(3,4)
                
                tabGrid.addLayout(triggerGrid, triggerIdx, 0)
                
            #create blank row at bottom to stretch    
            tabGrid.addWidget(QLabel(""), triggerIdx+1, 0,)
            tabGrid.setColumnStretch(triggerIdx+1, 4) 
            #add trigger list to a GroupBox
            gbTriggers.setLayout(tabGrid)
            #add the groupbox to the tab
            tabVBox = QVBoxLayout()
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


def killThreads():
    """
    Kills any running scripts on exit
    """
    for key in cmdThread:
        cmdThread[key].kill()
            
def quitApp():
    killThreads()
    print "exit"
       
def main():
    global ctrl, cmdThread
    
    #dict to stroe running threads
    cmdThread = {}
    #dict to store active controllers in
    ctrl = listControllers()   
    
    app = QApplication(sys.argv)
    win = Window()
    exitApp = app.exec_()
    #run this code on app exit
    quitApp()
    sys.exit(exitApp)

if __name__ == '__main__':
    main()
    
    
    
    
    
    
    
    
    
    
    
    