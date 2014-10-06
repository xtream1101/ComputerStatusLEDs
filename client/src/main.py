'''
Created on: 2014-06-28
Edited on:  2014-10-06

@author: Eddy Hintze
'''
import sys
import os
import time
import datetime
import serial
from serial.tools import list_ports
import subprocess
import json

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
    def data(self, model, led):
        self.model = model
        self.led = led
        self.key = self.model+''+str(self.led)
        
    def runCommand(self):
        while True:
            log("Running script for LED "+str(self.led))
            #get output from the command
            output = subprocess.check_output(self.command).strip()
            self.sendCmd(output)
            time.sleep(self.min)
            
    def sendCmd(self, cmd):
        #build command to send to the controller
        cmd = str(self.led) + '' + cmd
        log("LED "+str(self.led)+" command: "+cmd)
        ctrl[self.model].sendCommand(cmd)
        
    @pyqtSlot(int)
    def checkedSlot(self,state):
        if state != 2:
            log("Killed thread for LED "+str(self.led))
            #if checkbox gets unchecked, kill the thread.
            cmdThread[self.key].kill()
            del(cmdThread[self.key])
            #Turn off LED
            self.sendCmd("A0")
            #Enable edit fields
            txtCommand[self.model][self.led-1].setEnabled(True)
            sbMin[self.model][self.led-1].setEnabled(True)
        else:
            #Get values
            self.command = str(txtCommand[self.model][self.led-1].text())
            self.min = int(sbMin[self.model][self.led-1].value())
            #Disable edit fields
            txtCommand[self.model][self.led-1].setEnabled(False)
            sbMin[self.model][self.led-1].setEnabled(False)
            #start thread         
            cmdThread[self.key] = KThread(target=self.runCommand);
            cmdThread[self.key].start()
            log("Started thread for LED "+str(self.led))


            
class Window(QWidget):
    
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()
        
    def initUI(self):
        mainVBox = QVBoxLayout()
        mainVBox.addWidget(self.createTabs())
        
        #Load json data into fields
        loadData()
        self.setLayout(mainVBox)
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('LED Controller')    
        self.show()
        
    def createTabs(self):
        global cbEnable, txtCommand, sbMin
        
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
            key = str(tabs.tabText(tabIdx))
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
    deviceTemp = {}
    #Get list of serial ports and find any LED Controllers
    for port in ListSerialPorts():
        deviceTemp[port] = LedController()
        feedback = deviceTemp[port].connect(port)
        #if it is not a controller remove it from the list
        if feedback[:2] == 'XN':
            device[feedback] = deviceTemp[port]
        
        del deviceTemp[port]
        
    return device         

def killThreads():
    """
    Kills any running scripts on exit
    """
    for key in cmdThread:
        cmdThread[key].kill()

def closeConnections():
    for key in ctrl:
        ctrl[key].close()

def saveSettings():
    jsonData = {}
    for model in ctrl:
        ledCount = ctrl[model].getLedCount()
        ledList = {}
        for idx in xrange(ledCount):
            cmd = str(txtCommand[model][idx-1].text())
            delay = int(sbMin[model][idx-1].value())
            active = cbEnable[model][idx-1].isChecked()
            ledList[idx] = {'cmd':cmd,'delay':delay, 'active':active}
        jsonData[model] = ledList
        #write each model to its own config file
        with open('configs/'+model+'.json', 'w') as outfile:
            json.dump(jsonData[model], outfile, sort_keys = True, indent = 4, ensure_ascii=False)
        
def loadData():
    for model in ctrl:
        jsonData = {}
        try:
            f = open('configs/'+model+'.json', 'r')
            jsonData = json.load(f)
            f.close()
            ledCount = ctrl[model].getLedCount()
            for idx in xrange(ledCount):
                txtCommand[model][idx-1].setText(jsonData[str(idx)]['cmd'])
                sbMin[model][idx-1].setValue(jsonData[str(idx)]['delay'])
                cbEnable[model][idx-1].setChecked(jsonData[str(idx)]['active'])
        except IOError as e:
            pass

def log(data):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("ledStatus.log", "a") as logFile:
        logFile.write(timestamp+' - ')
        logFile.write(data)
        logFile.write("\n")
           
def quitApp():
    saveSettings()
    killThreads()
    #closeConnections()
    
       
def main():
    global ctrl, cmdThread
    
    #dict to stroe running threads
    cmdThread = {}
    #dict to store active controllers
    ctrl = listControllers()   
    
    app = QApplication(sys.argv)
    win = Window()
    exitApp = app.exec_()
    #run this code on app exit
    quitApp()
    log("Quit")
    sys.exit(exitApp)

if __name__ == '__main__':
    log("Started")
    main()
    
    
    
    
    
    
    
    
    
    
    
    