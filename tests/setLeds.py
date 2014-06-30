import os
import time
import serial
from serial.tools import list_ports

from Tkinter import *
import Tkinter as ttk 
from ttk import *


class Arduino:
    def __init__(self):
        self.isConn = False
        self.model = ""
        self.port = ""

    def connect(self, port):
        """
        Try and make a connection to Arduino
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
                return "Connected: " + self.model
            else:
                self.close()
                self.isConn = False
                return "Invalid Device"

        except serial.SerialException, e:
            self.isConn = False
            return "FAILED: " + self.port
         

    def sendCommand(self, val):
        self.conn.write(val)

    def checkConn(self):
        return self.isConn

    def getModel(self):
        return self.model

    def getPort(self):
        return self.port

    def close(self):
        self.conn.close()



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


def connectPort(*args):
    port_ = var.get()
    #check if key exists
    if port_ in led.keys():
        if led[port_].checkConn():
            connStatus.set("Switched")
        else:
            connStatus.set(led[port_].connect(port_))
    else:
        led[port_] = Arduino()
        connStatus.set(led[port_].connect(port_))



#Get list of open ports from windwos/unix
portList = list(ListSerialPorts())
portList.append("COM555")
#dict of led arduino units
led = {}

root = Tk()
root.title("Port Selector")

mainframe = Frame(root)                                 
mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack(pady = 10, padx = 10)

var = StringVar(root)



option = OptionMenu(mainframe, var, portList, *portList, command=connectPort)
var.set('Select a port')
option.grid(row = 1, column =1)

connStatus = StringVar()
lblConnStatus = Label(mainframe, text="...", textvariable=connStatus).grid(row = 1, column = 2)

Label(mainframe, text="Command").grid(row = 2, column = 1)
cmd = StringVar()
cmd_ent = Entry(mainframe, text=cmd, width = 15).grid(column = 2, row = 2)

root.mainloop()