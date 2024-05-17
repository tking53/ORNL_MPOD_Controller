####################################################
#basic PIXIEFRONTPANEL control script
####################################################


# Imports
import pexpect as pxp
import math as m
import time as chrono
import numpy as np
import threading
import logging
import logging.handlers

import re
from rich import print

import os
import fcntl
import arpreq as arp

from datetime import datetime

import u3

############################################
#                set default values
# ---------------------------------------------------
class MTASLABJACKProbeReader:

############################################    
    def __LogInfo(self):
        while self.Logging:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d\t%H:%M:%S")

            tempstr = formatted_datetime+'\t'
            for i in range(4):
                temp = self.GetTemp(i)
                measuretempstr = f'{temp:.1f}\t'
                tempstr += measuretempstr
            self.TempLog.error(tempstr)
            chrono.sleep(60)

############################################    
    def GetTemp(self,id:int):
        if id < 4:
            return float(self.LabJack.getFeedback(self.probes[id])[0])*(-0.00498025) + 198.495
        else:
            print(f"[red bold] LabJack Temp Probe {id} does not exist, they are [0-4)[/]")
            return None

############################################    
    def StartLogging(self,filename):
        if not self.Logging:
            self.Logging = True
            self.baselogname = filename
            if not os.path.exists(self.baselogname):
                os.makedirs(self.baselogname)
            self.TempFilename = filename+"/temps.tsv"

            Temp_exists = os.path.exists(self.TempFilename)

            self.TempLog = logging.getLogger('Temps'+str(self.SerialNumber)) 
            self.TempLogHandler = logging.handlers.TimedRotatingFileHandler(self.TempFilename,when='H',interval=1,backupCount=168)
            self.TempLog.addHandler(self.TempLogHandler)
            
            if not Temp_exists:
                self.TempLog.error("#Temps are in Celsius\n")

            self.Logger = threading.Thread(target=self.__LogInfo)
            self.Logger.start()
        else:
            print(f"[red bold] ALREADY LOGGING CURRENTS IN TEMPS IN {self.TempFilename}[/]")

############################################    
    def StopLogging(self):
        self.Logging = False
        self.Logger.join()
        self.TempLogHandler.close()

############################################
    def __init__(self):
        self.Logging = False
        try:
            self.LabJack = u3.U3()
            self.LabJackConfig = self.LabJack.configU3()
            self.SerialNumber = self.LabJackConfig['SerialNumber']
            self.probes = [ u3.AIN(i,31) for i in range(4) ]
        except Exception as e:
            print(f"[red bold] CAUGHT THIS ERROR WHEN TRYING TO COMMUNICATE WITH THE LABJACK {e}[/]")

############################################
    def __del__(self):
        if self.Logging:
            self.StopLogging()
