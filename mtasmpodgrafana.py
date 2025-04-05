####################################################
#basic MPOD control script
####################################################


# Imports
import argparse
import pexpect as pxp
import math as m
import time as chrono
import numpy as np
import signal
from threading import Event
import re
from prometheus_client import start_http_server, Gauge
import os
import fcntl
import arpreq as arp

from datetime import datetime

############################################
#                set default values
# ---------------------------------------------------
class MTASGrafanaPrometheusLogger:

############################################
    # Set SNMP and Default THINGS
    __snmpStripAll=" -OqvU "# NOTE:: The leading and Trailing spaces are important
    __snmp_base_options = ' -v 2c -m-WIENER-CRATE-MIB -M-/usr/share/snmp/mibs '  # NOTE:: The leading and Trailing spaces are important

############################################
    def __GenerateMpodID(self,mod: int, chan: int):
        if mod == 0:
            return "u" + str(chan).zfill(1)
        else:
            return "u" + str(mod) + str(chan).zfill(2)
 
############################################
    def __SetIP_AND_OpenLockFile(self,IPtoSet):
        self.MPODIP = " " + str(IPtoSet) + " "

############################################
    def SetIPOfMpod(self,ip_to_set):
        self.MPODIP = ip_to_set

############################################
    def get_voltage(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltage.'+mpodID))
            return retval
        return None

############################################
    def get_current_limit(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public")+ ' outputCurrent.' + mpodID))
            return retval
        return None

############################################
    def get_sensed_current(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementCurrent.' + mpodID))
            return retval
        return None

############################################
    def get_sensed_voltage(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementSenseVoltage.' + mpodID))
            return retval 
        return None

############################################
    def get_terminal_voltage(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementTerminalVoltage.' + mpodID))
            return retval
        return None

############################################
    def get_ramp(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltageRiseRate.' + mpodID))
            return retval
        return None


############################################
    def get_switch_state(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = pxp.run(self.__MakeSnmpGetCommand("public") + ' outputSwitch.' + mpodID).decode().replace("\r\n","")
            return retval
        return None

############################################
    def get_output_status(self,mod: int, chan: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputStatus.' + mpodID))
            return retval
        return None

############################################
    def get_all_info(self,mod: int,chan: int):
        mpodID = self.__GenerateMpodID(mod, chan)
        mpodSnmpIndex = str(int(mpodID.lstrip("u"))+1)
        chanData = pxp.run(self.__MakeSnmpGetCommand("guru") + " outputIndex." + mpodSnmpIndex + " outputSwitch." + mpodSnmpIndex + " outputMeasurementSenseVoltage." + mpodSnmpIndex + " outputVoltage." + mpodSnmpIndex + " outputMeasurementCurrent." + mpodSnmpIndex + " outputCurrent." + mpodSnmpIndex + " outputVoltageRiseRate." + mpodSnmpIndex + " outputVoltageFallRate." + mpodSnmpIndex).decode().split("\r\n")
        statStr = chanData[1].upper()
        termVolStr = float(chanData[2])
        voltageSetPointStr = float(chanData[3])
        termCurStr = float(chanData[4])
        currentTripPointStr = float(chanData[5])
        riseFallRateStr = float(chanData[6])
        return {'state': statStr, 'voltage': voltageSetPointStr, 'current' : currentTripPointStr, 'ramp': riseFallRateStr, 'sense_current': termCurStr, 'sense_voltage': termVolStr}

############################################
    def get_sense_voltage_current(self,mod: int,chan: int):
        mpodID = self.__GenerateMpodID(mod, chan)
        mpodSnmpIndex = str(int(mpodID.lstrip("u"))+1)
        chanData = pxp.run(self.__MakeSnmpGetCommand("guru") + " outputIndex." + mpodSnmpIndex + " outputMeasurementSenseVoltage." + mpodSnmpIndex + " outputMeasurementCurrent." + mpodSnmpIndex).decode().split("\r\n")
        termVolStr = float(chanData[1])
        termCurStr = float(chanData[2])
        return termVolStr, termCurStr 

############################################
    def walk_sense_voltage(self):
        chanData = pxp.run(self.__MakeSnmpWalkCommand("guru") + " outputMeasurementSenseVoltage").decode().split("\r\n")[:-1]
        return chanData 

############################################
    def walk_sense_current(self):
        chanData = pxp.run(self.__MakeSnmpWalkCommand("guru") + " outputMeasurementCurrent").decode().split("\r\n")[:-1]
        return chanData 

############################################
    def __does_mod_chan_exist(self,mod: int, chan: int):
        if mod in self.modlist:
            if chan in self.__chandict[mod]:
                return True
        return False

############################################
    def __IsThisAnMPOD(self,IPforTest):
            macaddress=arp.arpreq(str(IPforTest))
            ## These two partial MAC addresses are the only two as of April 2023 that are registered to WEINER. ORNL currently has a mix of controllers with these addresses. The "00:50..."" address is on the older controllers while "30:32..." is on the new one (the one with the little red switch onboard)
            if macaddress[0:8].lower() == "30:32:94" or macaddress[0:13].lower() == "00:50:c2:2d:c":
                selfDescription = self.__GETSYSDesc(IPforTest)
                if selfDescription[1].upper() == "MPOD":
                    return True
                else:
                    return False
            else:
                return False

############################################
    def __MakeSnmpGetCommand(self,community):
        return ('snmpget ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.MPODIP)

############################################
    def __MakeSnmpWalkCommand(self,community):
        return ('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.MPODIP)

############################################    
    def __GETSYSDesc(self,TestIP):
        return (pxp.run("snmpget "+ self.__snmpStripAll + self.__snmp_base_options + " -c public " + str(TestIP) + " sysDescr.0").decode().strip().split(" "))
        
############################################
    def GetCrateSysMainStatSTR(self):
        retvalue=pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode()
        return(retvalue.replace("\r\n",""))

############################################    
    def ParseChannelMap(self):
        self.__chandict = {}
        self.__chanlist = []
        self.modlist = []
        self.hvmap = {}

        self.__channamelist = [ str(byte_string,encoding='utf-8').lower() for byte_string in  ( ((pxp.run('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c guru ' + self.MPODIP + ' outputName')).split(b'\r\n'))[:-1] ) ]

        for cname in self.__channamelist:
            m = re.findall(r"\d",cname)
            if len(m) < 3 :
                if not ( 0 in self.modlist):
                    self.modlist.append(0)
                    self.__chandict[0] = []
                chanid = int(''.join([str(a) for a in m]))
                self.__chandict[0].append(chanid)
                info = self.get_all_info(0,chanid)
                self.hvmap[cname] = {"modid" : 0, "chanid" : chanid, "voltage": info['voltage'], "current": info['current'], "state": info['state'],"ramp": info['ramp']}
            else:
                modnum = int(m[0])
                if not(modnum in self.modlist):
                    self.modlist.append(modnum)
                    self.__chandict[modnum] = []
                chanid = int(''.join([str(a) for a in m[1:]]))
                self.__chandict[modnum].append(chanid)
                info = self.get_all_info(modnum,chanid)
                self.hvmap[cname] = {"modid" : modnum, "chanid" : chanid, "voltage": info['voltage'], "current": info['current'], "state": info['state'],"ramp": info['ramp']}

############################################    
    def LogInfo(self):
        while not shutdown_event.is_set():
            volts = self.walk_sense_voltage()
            currents = self.walk_sense_current()
            for v in volts:
                volt = float(v)
                print(volt)
            for c in currents:
                current = float(c)*1000*1000
                print(current)
            chrono.sleep(5)

############################################    
    def Startup(self):
        if self.GetCrateSysMainStatSTR().upper() == "ON":
            self.ParseChannelMap()

############################################
    def __init__(self,MPODIP:str=None,PIXIEIP:str=None):
        if MPODIP != None:
            self.__SetIP_AND_OpenLockFile(MPODIP)
            self.hvmap = {}
            if self.__IsThisAnMPOD(MPODIP):
                try:
                    self.Startup()
                except IOError:
                    os._exit(1)
            else:
                os._exit(1)

voltagedb = Gauge('mtas-voltage', 'MPOD Voltages',['ring','fb','idx'])
currentdb = Gauge('mtas-current', 'MPOD Currents',['ring','fb','idx'])
shutdown_event = Event()

def handle_signal(signum, frame):
    shutdown_event.set()

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

#def generate_metrics():
#         rings = ['center','inner','middle','outer']
#         frontback = ['front','back']
#         ids = ['1','2','3','4','5','6']
#         while True:
#             # Update the metric with a random value
#             for curring in rings :
#                 for currfb in frontback:
#                     for curridx in ids:
#                         voltage.labels(ring=curring,fb=currfb,idx=curridx).set(random.randint(0, 100))
#             time.sleep(5)  # Update every 5 seconds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mtas-grafana-prometheus logger for the mpod and pixie crate')
    parser.add_argument('-m','--mpod',type=str,default="192.168.13.237",help='mpod ip address')
    parser.add_argument('-p','--pixie',type=str,default="192.168.13.236",help='pixie ip address')
    args = parser.parse_args()

    mtas = MTASGrafanaPrometheusLogger(args.mpod,args.pixie)
    start_http_server(9101)
    mtas.LogInfo()
