'''
Created on: 2014-06-28
Edited on:  2014-10-06

@author: Eddy Hintze
'''
import time
import serial


class LedController(object):
    def __init__(self):
        self.isConn = False
        self.model = ""
        self.port = ""
        self.ledCount = 0
        
    def connect(self, port):
        """
        Try and make a connection to the Controller
        """
        self.port = port
        try:
            self.conn = serial.Serial(self.port, 
                                        9600,
                                        timeout=0,
                                        stopbits=serial.STOPBITS_TWO
                                        )
            time.sleep(2)
            self.sendCommand('?')
            time.sleep(1) #delay to wait for arduino to respond
            self.model = self.conn.readline()
            
            if self.model[:2] == "XN": #check to see if is a device we can use
                self.isConn = True
                #Get number of leds from model name
                if self.model[7].isdigit():
                    self.ledCount = int(self.model[6]+''+self.model[7])
                else:
                    self.ledCount = int(self.model[6])
                    
                return self.model
            else:
                self.close()
                self.isConn = False
                return "Invalid Device"

        except serial.SerialException, e:
            self.isConn = False
            return "FAILED: " + self.port
         

    def sendCommand(self, val):
        self.conn.write(str(val))

    def checkConn(self):
        return self.isConn
    
    def getLedCount(self):
        return self.ledCount
    
    def getModel(self):
        return self.model

    def getPort(self):
        return self.port

    def close(self):
        self.conn.close()