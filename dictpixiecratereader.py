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

############################################
#                set default values
# ---------------------------------------------------
class PIXIEFrontReadout:

############################################
    # Set SNMP and Default THINGS
    ListOfDefaultIPsForPIXIEFRONTPANELs = ["192.168.4.5"]
    __snmpStripAll=" -OqvU "# NOTE:: The leading and Trailing spaces are important
    __snmp_base_options = ' -v 2c -m-WIENER-CRATE-MIB -M-/usr/share/snmp/mibs '  # NOTE:: The leading and Trailing spaces are important

############################################
    def __GeneratePixieFrontReadoutID(self, chan: int):
        return "u" + str(chan).zfill(1)
 
############################################
    def __SetIP_AND_OpenLockFile(self,IPtoSet):
        self.IP = " " + str(IPtoSet) + " "
        self.lockfile = open("/tmp/mpodcontroller_" + self.IP.strip().replace(".","_") + ".lock", 'w')

############################################
    def SetIPOfPixieFrontReadout(self,ip_to_set):
        print(f"[bold red]Updated IP from {self.IP} to {ip_to_set} :: YOU NEED TO RERUN `Startup()`[/]")
        self.IP = ip_to_set

############################################
    def GetCrateSysMainStatus(self):
        retval = pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode().upper()
        print(f"[white]PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/] is [red]{retval}[/]")

############################################
    def get_voltage(self,chan: int,verbose=True):
        if self.__does_chan_exist(chan):
            mpodID = self.__GeneratePixieFrontReadoutID( chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltage.'+mpodID))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has a voltage of {retval} on  CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET VOLTAGE ON  CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE CHANNELS ARE {self.__chandict[0]}[/]")
        return None

############################################
    def get_current_limit(self, chan: int,verbose=True):
        if self.__does_chan_exist(chan):
            mpodID = self.__GeneratePixieFrontReadoutID( chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public")+ ' outputCurrent.' + mpodID))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has a current limit of {retval} on  CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET CURRENT LIMIT ON  CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE CHANNELS ARE {self.__chandict[0]}[/]")
        return None

############################################
    def get_sensed_current(self, chan: int,verbose=True):
        if self.__does_chan_exist(chan):
            mpodID = self.__GeneratePixieFrontReadoutID( chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementCurrent.' + mpodID))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has a current of {retval} on  CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET CURRENT ON CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE CHANNELS ARE {self.__chandict[0]}[/]")
        return None

############################################
    def get_sensed_voltage(self, chan: int,verbose=True):
        if self.__does_chan_exist(chan):
            mpodID = self.__GeneratePixieFrontReadoutID( chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementSenseVoltage.' + mpodID))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has an actual ouput voltage of {retval} on  CHANNEL {chan}[/]")
            return retval 
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET ACTUAL OUTPUT VOLTAGE ON  CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE CHANNELS ARE {self.__chandict[0]}[/]")
        return None

############################################
    def get_terminal_voltage(self, chan: int,verbose=True):
        if self.__does_chan_exist(chan):
            mpodID = self.__GeneratePixieFrontReadoutID( chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementTerminalVoltage.' + mpodID))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has an ouput voltage of {retval} on  CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET OUTPUT VOLTAGE ON  CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE CHANNELS ARE {self.__chandict[0]}[/]")
        return None

############################################
    def get_fan_speed(self,chan: int,verbose=True):
        if self.__does_fan_exist(chan):
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' fanSpeed.' + str(chan)))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has a fan speed of {retval} on CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET FAN SPEED ON CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE FANS ARE {self.fanlist}[/]")
        return None

############################################
    def get_sensor_temp(self,chan: int,verbose=True):
        if self.__does_temp_exist(chan):
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' sensorTemperature.temp' + str(chan)))
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has an external temp sensor of {retval} on CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET OUTPUT VOLTAGE ON CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
            print(f"[red bold]AVAILABLE EXTERNAL TEMP PROBES ARE {self.templist}[/]")
        return None

############################################
    def get_air_inlet_temp(self,verbose=True):
        retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' fanAirTemperature.0'))
        if verbose:
            print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has an air inlet temp of {retval}[/]")
        return retval

############################################
    def get_switch_state(self, chan: int,verbose=True):
        if self.__does_chan_exist(chan):
            mpodID = self.__GeneratePixieFrontReadoutID( chan)
            retval = pxp.run(self.__MakeSnmpGetCommand("public") + ' outputSwitch.' + mpodID).decode().replace("\r\n","")
            if verbose:
                print(f"[white]PIXIEFRONTPANEL CRATE AT IP [/][cyan]{self.IP}[/] [white]has an output switch state of {retval} on  CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET OUTPUT VOLTAGE ON  CHANNEL {chan} AS IT DOES NOT EXIST IN PIXIEFRONTPANEL CRATE AT IP[/] [cyan]{self.IP}[/]")
        return None

############################################
    def get_all_info(self,chan: int):
        mpodID = self.__GeneratePixieFrontReadoutID( chan)
        mpodSnmpIndex = mpodID
        chanData = pxp.run(self.__MakeSnmpGetCommand("guru") + " outputIndex." + mpodSnmpIndex + " outputMeasurementSenseVoltage." + mpodSnmpIndex + " outputVoltage." + mpodSnmpIndex + " outputMeasurementCurrent." + mpodSnmpIndex + " outputCurrent." + mpodSnmpIndex ).decode().split("\r\n")
        termVolStr = float(chanData[1])
        voltageSetPointStr = float(chanData[2])
        termCurStr = float(chanData[3])
        currentTripPointStr = float(chanData[4])
        return {'voltage': voltageSetPointStr, 'current' : currentTripPointStr, 'sense_current': termCurStr, 'sense_voltage': termVolStr}

############################################
    def get_sense_voltage_current(self,chan: int):
        mpodID = self.__GeneratePixieFrontReadoutID( chan)
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
    def walk_sensor_temp(self):
        chanData = pxp.run(self.__MakeSnmpWalkCommand("guru") + " sensorTemperature").decode().split("\r\n")[:-1]
        return chanData 

############################################
    def walk_fan_speed(self):
        chanData = pxp.run(self.__MakeSnmpWalkCommand("guru") + " fanSpeed").decode().split("\r\n")[:-1]
        return chanData 

############################################
    def __does_temp_exist(self, chan: int):
        if chan in self.templist:
            return True
        return False

############################################
    def __does_chan_exist(self, chan: int):
        if chan in self.__chandict[0]:
            return True
        return False

############################################
    def __does_fan_exist(self,chan: int):
        print(self.fanlist)
        if chan in self.fanlist:
            return True
        return False

############################################
    def __IsThisAnPIXIEFRONTPANEL(self,IPforTest):
            macaddress=arp.arpreq(str(IPforTest))
            ## These two partial MAC addresses are the only two as of April 2023 that are registered to WEINER. ORNL currently has a mix of controllers with these addresses. The "00:50..."" address is on the older controllers while "30:32..." is on the new one (the one with the little red switch onboard)
            print("[green]\tThis MAC address : {} is registered to WIENER[/]".format(macaddress))
            if macaddress[0:8].lower() == "30:32:94" or macaddress[0:13].lower() == "00:50:c2:2d:c":
                selfDescription = self.__GETSYSDesc(IPforTest)
                if selfDescription[1].upper() == "MPOD":
                    print(f"[green]\tSNMP reports that the device at this IP address of[/] [cyan]{IPforTest}[/] [green]is an {selfDescription[1]}[/]")
                    return False
                else:
                    print(f"[green]\tSNMP reports that the device at this IP address of[/] [cyan]{IPforTest}[/] [green]is an PIXIE {selfDescription[1]}[/]")
                    return True
            else:
                return False

############################################
    def __MakeSnmpGetCommand(self,community):
        return ('snmpget ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.IP)

############################################
    def __MakeSnmpBULKgetCommand(self,community):
        return ('snmpbulkget ' + self.__snmpStripAll + self.__snmp_base_options + "-Cr" + str(self.__NumberOfChannels) +  ' -c ' + str(community) + self.IP)

############################################
    def __MakeSnmpSetCommand(self,community):
        return ('snmpset ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.IP)

############################################
    def __MakeSnmpWalkCommand(self,community):
        return ('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.IP)

############################################    
    def __GETSYSDesc(self,TestIP):
        return (pxp.run("snmpget "+ self.__snmpStripAll + self.__snmp_base_options + " -c public " + str(TestIP) + " sysDescr.0").decode().strip().split(" "))
        
############################################
    def GetCrateSysMainStatSTR(self):
        retvalue=pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode()
        return(retvalue.replace("\r\n",""))

############################################    
    def ParseChannelMap(self):
        print('[dark_orange]Parsing out the current channelmap.\nThis will take a second as we\'re polling the mpod to get the current hv parameters[/]')
        self.__chandict = {}
        self.__chanlist = []
        self.modlist = []
        self.hvmap = {}
        self.templist = [1,2,3,4,5,6,7,8]
        self.fanlist = [1,2,3]

        self.__channamelist = [ str(byte_string,encoding='utf-8').lower() for byte_string in  ( ((pxp.run('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c guru ' + self.IP + ' outputName')).split(b'\r\n'))[:-1] ) ]

        self.__chandict[0] = []
        chanid=0
        for cname in self.__channamelist:
            self.__chandict[0].append(chanid)
            info = self.get_all_info(chanid)
            self.hvmap[cname] = {"chanid" : chanid, "voltage": info['voltage'], "current": info['current']}
            chanid+=1
            if( chanid == 4 ):
                chanid=5

############################################    
    def __LogInfo(self):
        while self.Logging:
            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d\t%H:%M:%S")
            volts = self.walk_sense_voltage()
            voltstr = formatted_datetime+'\t'
            for v in volts:
                volt = float(v)
                measurevstr = f'{volt:.2f}\t'
                voltstr += measurevstr
            self.VoltageLog.error(voltstr)

            inlet_temp = self.get_air_inlet_temp(False)
            temps = self.walk_sensor_temp()
            tempstr = formatted_datetime+f'\t{inlet_temp:d}\t'
            for t in temps:
                temp = int(t)
                measuretempstr = f'{temp:d}\t'
                tempstr += measuretempstr
            self.TempLog.error(tempstr)
            
            fans = self.walk_fan_speed()
            fanstr = formatted_datetime+'\t'
            for f in fans:
                fan = int(f)
                measurefanstr = f'{fan:d}\t'
                fanstr += measurefanstr
            self.FanLog.error(fanstr)

            currents = self.walk_sense_current()
            currentstr = formatted_datetime+'\t'
            for c in currents:
                current = float(c)
                measureastr = f'{current:.2f}\t'
                currentstr += measureastr
            self.CurrentLog.error(currentstr)
            chrono.sleep(60)

############################################    
    def StartLogging(self,filename):
        if not self.Logging:
            self.Logging = True
            self.baselogname = filename
            if not os.path.exists(self.baselogname):
                os.makedirs(self.baselogname)
            self.VoltageFilename = filename+"/voltages.tsv"
            self.CurrentFilename = filename+"/currents.tsv"
            self.TempFilename = filename+"/temps.tsv"
            self.FanFilename = filename+"/fans.tsv"

            Volt_exists = os.path.exists(self.VoltageFilename)
            Current_exists = os.path.exists(self.CurrentFilename)
            Temp_exists = os.path.exists(self.TempFilename)
            Fan_exists = os.path.exists(self.FanFilename)

            self.VoltageLog = logging.getLogger('Volts'+self.IP) 
            self.VoltageLogHandler = logging.handlers.TimedRotatingFileHandler(self.VoltageFilename,when='H',interval=1,backupCount=168)
            self.VoltageLog.addHandler(self.VoltageLogHandler)

            self.CurrentLog = logging.getLogger('Current'+self.IP)
            self.CurrentLogHandler = logging.handlers.TimedRotatingFileHandler(self.CurrentFilename,when='H',interval=1,backupCount=168)
            self.CurrentLog.addHandler(self.CurrentLogHandler)

            self.TempLog = logging.getLogger('Temps'+self.IP) 
            self.TempLogHandler = logging.handlers.TimedRotatingFileHandler(self.TempFilename,when='H',interval=1,backupCount=168)
            self.TempLog.addHandler(self.TempLogHandler)

            self.FanLog = logging.getLogger('Fans'+self.IP) 
            self.FanLogHandler = logging.handlers.TimedRotatingFileHandler(self.FanFilename,when='H',interval=1,backupCount=168)
            self.FanLog.addHandler(self.FanLogHandler)

            if not Volt_exists:
                self.VoltageLog.error("#Voltages are in Volts\n")
            if not Current_exists:
                self.CurrentLog.error("#Currents are in Amps\n")
            if not Temp_exists:
                self.TempLog.error("#Temps are in Celsius\n")
            if not Fan_exists:
                self.FanLog.error("#Currents are in RPM\n")

            self.Logger = threading.Thread(target=self.__LogInfo)
            self.Logger.start()
        else:
            print(f"[red bold] ALREADY LOGGING CURRENTS IN {self.CurrentFilename}, VOLTAGES IN {self.VoltageFilename}, TEMPS IN {self.TempFilename}, FAN SPEEDS IN {self.FanFilename} [/]")

############################################    
    def StopLogging(self):
        self.Logging = False
        self.Logger.join()
        self.VoltageLogHandler.close()
        self.CurrentLogHandler.close()
        self.TempLogHandler.close()
        self.FanLogHandler.close()

############################################    
    def Startup(self):
        print('[magenta]Beginning Startup[/]')
        if self.GetCrateSysMainStatSTR().upper() == "ON":
            print("[magenta]The crate software switch is on[/]")
            self.ParseChannelMap()
        else:
            print("[bold red]The crate software switch is off[/]")

############################################
    def __init__(self,IP:str=None):
        self.Logging = False
        if IP != None:
            self.__SetIP_AND_OpenLockFile(IP)
            self.hvmap = {}
            if self.__IsThisAnPIXIEFRONTPANEL(IP):
                try:
                    fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.Startup()
                except IOError:
                    print(f"[red bold]Another instance of PIXIEFRONTPANEL Controller is already running at the IP Address of[/] [cyan]{IP}[/]")
                    os._exit(1)
            else:
                print(f"[red bold]THIS IS NOT AN PIXIEFRONTPANEL!!!!![/]")
                print(f"[red bold]KICKING YOU OUT OF THE SHELL NOW[/]")
                os._exit(1)
        else:
            self.ipstatus = {"PIXIEFRONTPANEL" : [], "ACTIVE" : [], "INACTIVE" : []}

            for ip in self.ListOfDefaultIPsForPIXIEFRONTPANELs:
                print(f"[red]Trying to connect to this IP[/] [cyan]{ip}[/]")
                (out,retcode) = pxp.run(f"ping -c1 -W1 {ip}",withexitstatus=True)
                if retcode == 0 :
                    if self.__IsThisAnPIXIEFRONTPANEL(ip):
                        self.ipstatus["PIXIEFRONTPANEL"].append(ip)
                    else:
                        self.ipstatus["ACTIVE"].append(ip)
                else:
                    self.ipstatus["INACTIVE"].append(ip)

            print(f"[red bold]Found these INACTIVE ports : {self.ipstatus['INACTIVE']}")
            print(f"[blue bold]Found these ACTIVE ports : {self.ipstatus['ACTIVE']}")
            print(f"[green bold]Found these PIXIEFRONTPANEL ports : {self.ipstatus['PIXIEFRONTPANEL']}")

            if len(self.ipstatus['PIXIEFRONTPANEL']) == 0:
                print('[red bold]NO PIXIEFRONTPANEL FOUND ATTACHED ON THE NETWORK. VERIFY NETWORK SETTINGS[/]')
                print('[red bold]KICKING YOU OUT OF THE SHELL NOW, BECAUSE THERE ARE NO PIXIEFRONTPANELS ON THE NETWORK[/]')
                os._exit(1)
            elif len(self.ipstatus['PIXIEFRONTPANEL']) == 1:
                print(f'[red bold]FOUND ONE PIXIEFRONTPANEL ON THE NETWORK AT IP :[/] [cyan bold]{self.ipstatus["PIXIEFRONTPANEL"][0]}')
                print("[red bold]CONTINUING WITH THIS FOR THE REST OF THE SETUP[/]")
                self.__SetIP_AND_OpenLockFile(self.ipstatus['PIXIEFRONTPANEL'][0])
                try:
                    fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.Startup()
                except IOError:
                    print(f"[red bold]Another instance of PIXIEFRONTPANEL Controller is already running at the IP Address of[/] [cyan]{self.ipstatus['PIXIEFRONTPANEL'][0]}[/]")
                    os._exit(1)
            else:
                print("[red bold]FOUND MULTIPLE PIXIEFRONTPANELS ON THE NETWORK, CURRENTLY THIS CLASS ONLY SUPPORTS A SINGLE PIXIEFRONTPANEL AT A TIME[/]")
                print(f"[red bold]HERE ARE ALL THE PIXIEFRONTPANEL IP ADDRESSES[/] [cyan bold]{self.ipstatus['PIXIEFRONTPANEL']}[/] [red bold], YOU NEED TO MAKE A SINGLE CLASS INSTANCE FOR EACH YOU WISH TO CONTROL AND SPECIFY THE IP IN THE CONSTUCTION[/]")

############################################
    def __del__(self):
        fcntl.flock(self.lockfile, fcntl.LOCK_UN)
        self.lockfile.close()
        if self.Logging:
            self.StopLogging()

############################################
    def get_system_status(self):
        smallColWidth=11
        largeColWidth=21
        fullColWidth=smallColWidth*3 + largeColWidth*4
        if self.GetCrateSysMainStatSTR().lower() == "on":
            print(f'IP: [cyan]{self.IP}[/] Software Switch: [green]ON[/] ')
            if self.Logging:
                print(f'Logging: [green]{self.Logging}[/] VoltageFile: {self.VoltageFilename} CurrentFile: {self.CurrentFilename}')
            else:
                print(f'Logging: [red]{self.Logging}[/]')
            print(f'[underline]{"[MODULEID]": ^{smallColWidth}}|{"[CHANID]": ^{smallColWidth}}|{"[CHAN]": ^{smallColWidth}}|{"[STATUS]": ^{smallColWidth}}|{"[MEASURED VOLTAGE]": ^{largeColWidth}}|{"[SET VOLTAGE]": ^{largeColWidth}}|{"[MEASURED CURRENT]" : ^{largeColWidth}}|{"[CURRENT TRIP]": ^{largeColWidth}}|{"[RAMP]": ^{smallColWidth}}[/]')

            firstmodid = self.modlist[0]
            for id,map in self.hvmap.items():
                modid = map['modid']
                chanid = map['chanid']
                status = map['state']
                setv = map['voltage']
                seta = map['current']
                
                measurev,measurea  = self.get_sense_voltage_current(modid,chanid)

                measurevstr = f'{measurev:.2f} V'
                setvstr = f'{setv:.2f} V'

                mu = chr(956)
                newline = '-'
                measureastr = f'{measurea:.2f} {mu}A'
                setastr = f'{seta:.2f} {mu}A'
                if modid != firstmodid:
                    firstmodid = modid
                    print(newline*(5*smallColWidth + 3*largeColWidth + 28))

                if status == 'OFF':
                    print(f'[white]{modid: ^{smallColWidth}}|{chanid: ^{smallColWidth}}|{id: ^{smallColWidth}}|[/][red]{status: ^{smallColWidth}}[/][white]|{measurevstr: ^{largeColWidth}}|{setvstr: ^{largeColWidth}}|{measureastr: ^{largeColWidth}}|{setastr: ^{largeColWidth}}[/]')
                else:
                    print(f'[white]{modid: ^{smallColWidth}}|{chanid: ^{smallColWidth}}|{id: ^{smallColWidth}}|[/][green]{status: ^{smallColWidth}}[/][white]|{measurevstr: ^{largeColWidth}}|{setvstr: ^{largeColWidth}}|{measureastr: ^{largeColWidth}}|{setastr: ^{largeColWidth}}[/]')
            
        else:
            print(f'IP: [cyan]{self.IP}[/] Sofware Switch: [red]OFF[/]')
