####################################################
#basic MPOD control script
####################################################


# Imports
import pexpect as pxp
import math as m
import time as chrono
import numpy as np

import re
from rich import print

import os
import fcntl
import arpreq as arp

############################################
#                set default values
# ---------------------------------------------------
class MPODController:

############################################
    # Set SNMP and Default THINGS
    ListOfDefaultIPsForMPODs = ["192.168.0.5","192.168.4.5","192.168.4.2","192.168.13.237"]
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
        self.__IP = " " + str(IPtoSet) + " "
        self.lockfile = open("/tmp/mpodcontroller_" + self.__IP.strip().replace(".","_") + ".lock", 'w')

############################################
    def SetIPOfMpod(self,ip_to_set):
        print(f"[bold red]Updated IP from {self.__IP} to {ip_to_set} :: YOU NEED TO RERUN `Startup()`[/]")
        self.__IP = ip_to_set

############################################
    def GetNumberOfModules(self):
        print(f"[white]MPOD Crate at IP[/] [cyan]{self.__IP}[/] [white]has {len(self.__modlist)} installed[/]")
        print(f"[white]They exist in the following slots {self.__modlist}, which is 0 counting[/]")

############################################
    def GetNumberOfChanPerModule(self):
        for key in self.__chandict:
            print(f"[white]MPOD CRATE AT IP[/] [cyan]{self.__IP}[/] [white]has a Module {key} with {len(self.__chandict[key])} channels[/]")

############################################
    def GetCrateSysMainStatus(self):
        retval = pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode().upper()
        print(f"[white]MPOD CRATE AT IP[/] [cyan]{self.__IP}[/] is [red]{retval}[/]")

############################################
    def get_voltage(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltage.'+mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has a voltage of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET VOLTAGE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def get_current_limit(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public")+ ' outputCurrent.' + mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has a current limit of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET CURRENT LIMIT ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def get_sensed_current(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementCurrent.' + mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has a current of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET CURRENT ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def get_sensed_voltage(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementSenseVoltage.' + mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has an actual ouput voltage of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval 
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET ACTUAL OUTPUT VOLTAGE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def get_terminal_voltage(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementTerminalVoltage.' + mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has an ouput voltage of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET OUTPUT VOLTAGE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def get_ramp(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltageRiseRate.' + mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has a ramp rate of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET RAMP RATE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None


############################################
    def get_switch_state(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = pxp.run(self.__MakeSnmpGetCommand("public") + ' outputSwitch.' + mpodID).decode().replace("\r\n","")
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has an output switch state of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET OUTPUT VOLTAGE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def get_output_status(self,mod: int, chan: int,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            retval = eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputStatus.' + mpodID))
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has a status of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return retval
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO GET STATUS ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return None

############################################
    def __get_all_info(self,mod: int,chan: int):
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

    def __get_sense_voltage_current(self,mod: int,chan: int):
        mpodID = self.__GenerateMpodID(mod, chan)
        mpodSnmpIndex = str(int(mpodID.lstrip("u"))+1)
        chanData = pxp.run(self.__MakeSnmpGetCommand("guru") + " outputIndex." + mpodSnmpIndex + " outputMeasurementSenseVoltage." + mpodSnmpIndex + " outputMeasurementCurrent." + mpodSnmpIndex).decode().split("\r\n")
        termVolStr = float(chanData[1])
        termCurStr = float(chanData[2])
        return termVolStr, termCurStr 

############################################
    def __does_mod_chan_exist(self,mod: int, chan: int):
        if mod in self.__modlist:
            if chan in self.__chandict[mod]:
                return True
        return False

############################################
    def __IsThisAnMPOD(self,IPforTest):
            macaddress=arp.arpreq(str(IPforTest))
            ## These two partial MAC addresses are the only two as of April 2023 that are registered to WEINER. ORNL currently has a mix of controllers with these addresses. The "00:50..."" address is on the older controllers while "30:32..." is on the new one (the one with the little red switch onboard)
            if macaddress[0:8].lower() == "30:32:94" or macaddress[0:13].lower() == "00:50:c2:2d:c":
                print("[green]\tThis MAC address is registered to WIENER[/]")
                selfDescription = self.__GETSYSDesc(IPforTest)
                print(f"[green]\tSNMP reports that the device at this IP address of[/] [cyan]{IPforTest}[/] [green]is an {selfDescription[1]}[/]")
                if selfDescription[1].upper() == "MPOD":
                    return True
                else:
                    return False
            else:
                return False

############################################
    def __MakeSnmpGetCommand(self,community):
        return ('snmpget ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.__IP)

############################################
    def __MakeSnmpBULKgetCommand(self,community):
        return ('snmpbulkget ' + self.__snmpStripAll + self.__snmp_base_options + "-Cr" + str(self.__NumberOfChannels) +  ' -c ' + str(community) + self.__IP)

############################################
    def __MakeSnmpSetCommand(self,community):
        return ('snmpset ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.__IP)

############################################    
    def __GETSYSDesc(self,TestIP):
        return (pxp.run("snmpget "+ self.__snmpStripAll + self.__snmp_base_options + " -c public " + str(TestIP) + " sysDescr.0").decode().strip().split(" "))
        
############################################
    def __GetCrateSysMainStatSTR(self):
        retvalue=pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode()
        return(retvalue.replace("\r\n",""))

############################################
    def SetCrateSwitch(self,Val: int):
        retval = pxp.run(self.__MakeSnmpSetCommand('private') + ' sysMainSwitch.0' + ' i ' + str(Val)).decode()
        print(f"[bold red]{retval}[/]")
        if Val == 1:
            print("[white bold]Waiting ~15 seconds for the modules to boot up[/]")
            chrono.sleep(15)

###########################################
    def set_voltage(self,mod: int, chan: int, volts,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            oldhv = self.hvmap[mpodID]['voltage']
            retval = eval(pxp.run(self.__MakeSnmpSetCommand('guru') + 'outputVoltage.' + mpodID + ' F '+str(volts)))
            self.hvmap[mpodID]['voltage'] = retval
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has been set from {oldhv} to a voltage of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return {'new':retval,'old':oldhv}
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO SET VOLTAGE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return {'new':None,'old':None}

############################################
    def set_current(self,mod: int, chan: int, current,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            currentToSet = int(current) * pow(10,-6)
            oldcurrent = self.hvmap[mpodID]["current"]
            retval = eval(pxp.run(self.__MakeSnmpSetCommand('guru') + 'outputCurrent.' + mpodID + ' F '+str(currentToSet)))
            self.hvmap[mpodID]['current'] = retval
            if verbose:
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has been set from {oldcurrent} to a current of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return {'new':retval,'old':oldcurrent}
        if verbose:
            print(f"[red bold]ERROR: UNABLE TO SET VOLTAGE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
        return {'new':None,'old':None}

############################################
    def set_on_off(self,mod: int, chan: int, onOff: int):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod, chan)
            oldstate = self.hvmap[mpodID]['state']
            retval = pxp.run(self.__MakeSnmpSetCommand('guru') + ' outputSwitch.'+mpodID+' i '+str(onOff)).decode().replace("\r\n","")
            self.hvmap[mpodID]['state'] = retval.upper()
            print(f"[bold magenta]MPOD CRATE AT IP[/][cyan]{self.__IP}[/][bold magenta] SETTING MODULE {mod} CHANNEL {chan} to [/][bold red]{retval.upper()}[/][bold magenta] from [/][bold red]{oldstate.upper()}[/]")
        else:
            print(f"[bold red]ERROR: UNABLE TO SET ON/OFF ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")

############################################    
    def set_on_off_all(self,onOff):
        for mod in self.__modlist:
            for chan in self.__chandict[mod]:
                self.set_on_off(mod,chan,onOff)
            print('\n')

############################################
    def set_current_limit_all(self,limit,verbose=True):
        for mod in self.__modlist:
            for chan in self.__chandict[mod]:
                _ = self.set_current(mod,chan,limit,verbose)
            print('\n')

############################################
    def set_ramp_all(self,rate,verbose=True):
        for mod in self.__modlist:
            for chan in self.__chandict[mod]:
                val = self.set_ramp(mod,chan,rate,verbose)

############################################
    def set_ramp(self,mod: int, chan: int, rate,verbose=True):
        if self.__does_mod_chan_exist(mod,chan):
            mpodID = self.__GenerateMpodID(mod,chan)
            oldramp = self.hvmap[mpodID]['ramp']
            retval = float(pxp.run(self.__MakeSnmpSetCommand('guru') +  ' outputVoltageRiseRate.'+ mpodID+' F '+str(rate)).decode().replace("\r\n",""))
            self.hvmap[mpodID]['ramp'] = retval
            if verbose :
                print(f"[white]MPOD CRATE AT IP [/][cyan]{self.__IP}[/] [white]has been set to a ramp rate of {retval} on MODULE {mod} CHANNEL {chan}[/]")
            return {'old' : oldramp, 'new': retval}
        else:
            if verbose:
                print(f"[red bold]ERROR: UNABLE TO SET RAMP RATE ON MODULE {mod} CHANNEL {chan} AS IT DOES NOT EXIST IN MPOD CRATE AT IP[/] [cyan]{self.__IP}[/]")
            return {'old' : None, 'new': None}

############################################    
    def ParseChannelMap(self):
        print('[dark_orange]Parsing out the current channelmap.\nThis will take a second as we\'re polling the mpod to get the current hv parameters[/]')
        self.__chandict = {}
        self.__chanlist = []
        self.__modlist = []
        self.hvmap = {}

        self.__channamelist = [ str(byte_string,encoding='utf-8').lower() for byte_string in  ( ((pxp.run('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c guru ' + self.__IP + ' outputName')).split(b'\r\n'))[:-1] ) ]

        for cname in self.__channamelist:
            m = re.findall(r"\d",cname)
            if len(m) < 3 :
                if not ( 0 in self.__modlist):
                    self.__modlist.append(0)
                    self.__chandict[0] = []
                chanid = int(''.join([str(a) for a in m]))
                self.__chandict[0].append(chanid)
                info = self.__get_all_info(0,chanid)
                self.hvmap[cname] = {"modid" : 0, "chanid" : chanid, "voltage": info['voltage'], "current": info['current'], "state": info['state'],"ramp": info['ramp']}
            else:
                modnum = int(m[0])
                if not(modnum in self.__modlist):
                    self.__modlist.append(modnum)
                    self.__chandict[modnum] = []
                chanid = int(''.join([str(a) for a in m[1:]]))
                self.__chandict[modnum].append(chanid)
                info = self.__get_all_info(modnum,chanid)
                self.hvmap[cname] = {"modid" : modnum, "chanid" : chanid, "voltage": info['voltage'], "current": info['current'], "state": info['state'],"ramp": info['ramp']}
        #print(self.__channamelist)
        #print(self.__modlist)
        #print(self.__chandict)
        #print(self.hvmap)

############################################    
    def Startup(self):
        print('[magenta]Beginning Startup[/]')
        if self.__GetCrateSysMainStatSTR().upper() == "ON":
            print("[magenta]The crate software switch is on[/]")
            self.ParseChannelMap()
        else:
            print("[bold red]The crate software switch is off[/]")

############################################
    def __init__(self,IP:str=None):
        if IP != None:
            self.__SetIP_AND_OpenLockFile(IP)
            try:
                fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.Startup()
            except IOError:
                print(f"[red bold]Another instance of MPOD Controller is already running at the IP Address of[/] [cyan]{IP}[/]")
                os._exit(1)
        else:
            self.ipstatus = {"MPOD" : [], "ACTIVE" : [], "INACTIVE" : []}

            for ip in self.ListOfDefaultIPsForMPODs:
                print(f"[red]Trying to connect to this IP[/] [cyan]{ip}[/]")
                (out,retcode) = pxp.run(f"ping -c1 -W1 {ip}",withexitstatus=True)
                if retcode == 0 :
                    if self.__IsThisAnMPOD(ip):
                        self.ipstatus["MPOD"].append(ip)
                    else:
                        self.ipstatus["ACTIVE"].append(ip)
                else:
                    self.ipstatus["INACTIVE"].append(ip)

            print(f"[red bold]Found these INACTIVE ports : {self.ipstatus['INACTIVE']}")
            print(f"[blue bold]Found these ACTIVE ports : {self.ipstatus['ACTIVE']}")
            print(f"[green bold]Found these MPOD ports : {self.ipstatus['MPOD']}")

            if len(self.ipstatus['MPOD']) == 0:
                print('[red bold]NO MPOD FOUND ATTACHED ON THE NETWORK. VERIFY NETWORK SETTINGS[/]')
                os._exit(1)
            elif len(self.ipstatus['MPOD']) == 1:
                print(f'[red bold]FOUND ONE MPOD ON THE NETWORK AT IP :[/] [cyan bold]{self.ipstatus["MPOD"][0]}')
                print("[red bold]CONTINUING WITH THIS FOR THE REST OF THE SETUP[/]")
                self.__SetIP_AND_OpenLockFile(self.ipstatus['MPOD'][0])
                try:
                    fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.Startup()
                except IOError:
                    print(f"[red bold]Another instance of MPOD Controller is already running at the IP Address of[/] [cyan]{self.ipstatus['MPOD'][0]}[/]")
                    os._exit(1)
            else:
                print("[red bold]FOUND MULTIPLE MPODS ON THE NETWORK, CURRENTLY THIS CLASS ONLY SUPPORTS A SINGLE MPOD AT A TIME[/]")
                print(f"[red bold]HERE ARE ALL THE MPOD IP ADDRESSES[/] [cyan bold]{self.ipstatus['MPOD']}[/] [red bold], YOU NEED TO MAKE A SINGLE CLASS INSTANCE FOR EACH YOU WISH TO CONTROL AND SPECIFY THE IP IN THE CONSTUCTION[/]")

############################################
    def __del__(self):
        fcntl.flock(self.lockfile, fcntl.LOCK_UN)
        self.lockfile.close()

############################################
    def get_system_status(self):
        smallColWidth=11
        largeColWidth=21
        fullColWidth=smallColWidth*3 + largeColWidth*4
        if self.__GetCrateSysMainStatSTR().lower() == "on":
            print(f'IP: [cyan]{self.__IP}[/] Sofware Switch: [green]ON[/]')
            print(f'[underline]{"[MODULEID]": ^{smallColWidth}}|{"[CHANID]": ^{smallColWidth}}|{"[CHAN]": ^{smallColWidth}}|{"[STATUS}": ^{smallColWidth}}|{"[MEASURED VOLTAGE]": ^{largeColWidth}}|{"[SET VOLTAGE]": ^{largeColWidth}}|{"[MEASURED CURRENT]" : ^{largeColWidth}}|{"[CURRENT TRIP]": ^{largeColWidth}}|{"[RAMP]": ^{smallColWidth}}[/]')

            for id,map in self.hvmap.items():
                modid = map['modid']
                chanid = map['chanid']
                status = map['state']
                setv = map['voltage']
                seta = map['current']
                ramp = map['ramp']
                
                measurev,measurea  = self.__get_sense_voltage_current(modid,chanid)

                measurevstr = f'{measurev:.2f} V'
                setvstr = f'{setv:.2f} V'
                rampstr = f'{ramp:.2f} V/s'

                mu = chr(956)
                measureastr = f'{1000*1000*measurea:.2f} {mu}A'
                setastr = f'{1000*1000*seta:.2f} {mu}A'

                if status == 'OFF':
                    print(f'[white]{modid: ^{smallColWidth}}|{chanid: ^{smallColWidth}}|{id: ^{smallColWidth}}|[/][red]{status: ^{smallColWidth}}[/][white]|{measurevstr: ^{largeColWidth}}|{setvstr: ^{largeColWidth}}|{measureastr: ^{largeColWidth}}|{setastr: ^{largeColWidth}}|{rampstr: ^{smallColWidth}}[/]')
                else:
                    print(f'[white]{modid: ^{smallColWidth}}|{chanid: ^{smallColWidth}}|{id: ^{smallColWidth}}|[/][green]{status: ^{smallColWidth}}[/][white]|{measurevstr: ^{largeColWidth}}|{setvstr: ^{largeColWidth}}|{measureastr: ^{largeColWidth}}|{setastr: ^{largeColWidth}}|{rampstr: ^{smallColWidth}}[/]')
            
        else:
            print(f'IP: [cyan]{self.__IP}[/] Sofware Switch: [red]OFF[/]')

############################################
    def write_out_HV(self,filename:str):
        filename+= "-" + chrono.strftime("%m_%d_%Y_%H%M%S") + ".csv"
        print(f"Writing out the current HV of MPOD at IP: [cyan]{self.__IP}[/] to file : {filename}")
        ouf = open(filename,'w')
        ouf.write("## Module Number , Channel Number , Set Voltage , Set Current Limit\n")
        for id in self.hvmap:
            ouf.write(f"{id} {self.hvmap[id]['modid']} {self.hvmap[id]['chanid']} {self.hvmap[id]['voltage']} {self.hvmap[id]['current']*1000*1000} {self.hvmap[id]['ramp']}\n")
        ouf.close()
        return filename

    def set_HV_from_read(self,settingsmap,verbose=False):
        print('[bold red]SETTING VOLTAGES[/]')
        for id in settingsmap:
            self.set_voltage(settingsmap[id]['modid'],settingsmap[id]['chanid'],settingsmap[id]['voltage'],verbose)

        print('[bold red]SETTING CURRENT LIMITS[/]')
        for id in settingsmap:
            self.set_current(settingsmap[id]['modid'],settingsmap[id]['chanid'],settingsmap[id]['current'],verbose)

        print('[bold red]SETTING RAMP RATES[/]')
        for id in settingsmap:
            self.set_ramp(settingsmap[id]['modid'],settingsmap[id]['chanid'],settingsmap[id]['ramp'],verbose)


############################################
def read_in_HV(filename:str):
    data = np.genfromtxt(filename,names=['uid','modid','chanid','voltage','current','ramp'],dtype=None,encoding='utf-8')
    datadict = {}
    for item in data:
        datadict[item[0]] = {'modid':int(item[1]),'chanid':int(item[2]),'voltage':float(item[3]),'current':float(item[4]),'ramp':float(item[5])}
    return datadict
