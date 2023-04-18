####################################################
#basic MPOD control script
####################################################


# Imports
import pexpect as pxp
import math as m
import time as chrono

import os
import fcntl
import arpreq as arp

############################################
#                set default values
# ---------------------------------------------------
class MPODController:
    # set Color Codes
    __redCode="\033[31;1m"
    __greenCode="\033[32;1m"
    __yellowCode="\033[33m"
    __resetCode="\033[0m"
    __underlineCode="\033[4m"

############################################
    # Set SNMP and Default THINGS
    __ListOfDefaultIPsForMPODs = ["192.168.0.5","192.168.4.5","192.168.4.2","192.168.13.237"]
    __snmpStripAll=" -OqvU "
    __snmp_base_options = ' -v 2c -m-WIENER-CRATE-MIB -M-/usr/share/snmp/mibs '
    __IP = ''
    __ListOfModIndexs = list()
    __NumberOfChansPerMod = list()
    __NumberOfChannels = int()
    __NumberOfModules = int()

############################################
    def __GenerateMpodID(self,mod: str, chan: str):
        if mod == 0:
            return "u" + str(chan).zfill(1)
        else:
            return "u" + str(mod) + str(chan).zfill(2)
        
############################################
    def __GetCrateSysMainStatSTR(self):
        retvalue=pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode()
        return(retvalue.replace("\r\n",""))

############################################
    def __MakeSnmpSetCommand(self,community):
        return ('snmpset ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.__IP)

############################################
    def __MakeSnmpGetCommand(self,community):
        return ('snmpget ' + self.__snmp_base_options + self.__snmpStripAll + ' -c ' + str(community) + self.__IP)

############################################
    def __MakeSnmpBULKgetCommand(self,community):
        return ('snmpbulkget ' + self.__snmpStripAll + self.__snmp_base_options + "-Cr" + str(self.__NumberOfChannels) +  ' -c ' + str(community) + self.__IP)

############################################
    def __PrintBulks(self,par):
        print('test bullk returns')
        print(pxp.run(self.__MakeSnmpBULKgetCommand("private") + str(par)).decode())
        __TestVar = pxp.run(self.__MakeSnmpBULKgetCommand("private") + str(par)).decode().strip().split("\r\n")
        print("\n\n\n Now reading from var")
        print(str(__TestVar))
        for i,it in enumerate(__TestVar):
           print(str(it) + "   " + str(i))

############################################
    def SetIPOfMpod(self,ip_to_set):
        self.__IP = ip_to_set
        print("Updated IP to " + str(self.__IP) + ":: YOU NEED TO RERUN `Startup()`")

############################################
    def ReadNumberOfModuleAndChannels(self):
        self.__ListOfModIndexs.clear()
        self.__NumberOfChansPerMod.clear()

        self.__NumberOfModules = eval(pxp.run('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c guru ' + self.__IP + ' moduleNumber'))
        self.__ListOfModIndexs= [ int(x[2]) for x in pxp.run('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c guru ' + self.__IP + ' moduleIndex').decode().rstrip("\r\n").split("\r\n") ]

        if self.__NumberOfModules != len(self.__ListOfModIndexs):
            print("ERROR:: Number of modules reported by snmp for \"moduleNumber\" != the number detected through \"moduleIndex\"")
            return 1

        for i in range(self.__ListOfModIndexs[-1]+1):
            if i not in self.__ListOfModIndexs:
                self.__NumberOfChansPerMod.append(None)
            else:
                modDes=pxp.run('snmpwalk ' + self.__snmp_base_options + self.__snmpStripAll + ' -c guru ' + self.__IP + ' moduleDescription.ma' + str(i)).decode().split(", ")[2]
                self.__NumberOfChansPerMod.append(modDes)
                self.__NumberOfChannels +=int(modDes)

############################################
    def GetNumberOfChanPerModule(self):
        for i,val in enumerate(self.__NumberOfChansPerMod):
            print("chans per mod " +str(i) + " = " + str(val))

############################################
    def GetNumberOfModules(self):
        print("MPOD Crate has " + str(self.__NumberOfModules) + " installed")

############################################
    def SetSafetys(self,detector: str):
        lowDet = detector.lower()
        if lowDet == "mtas":
            mtasC_max = 1250
            mtasIMO_max = 1450

############################################
    def GetCrateSysMainStatus(self):
        print(self.__redCode + pxp.run(self.__MakeSnmpGetCommand("public") + ' sysMainSwitch.0').decode().upper() + self.__resetCode)

############################################
    def get_voltage(self,mod: str, chan: str):
        mpodID = self.__GenerateMpodID(mod, chan)
        return (eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltage.'+mpodID)))

############################################
    def get_current_limit(self,mod: str, chan: str):
        mpodID = self.__GenerateMpodID(mod, chan)
        print(eval(pxp.run(self.__MakeSnmpGetCommand("public")+ ' outputCurrent.' + mpodID)))

############################################
    def get_sensed_current(self,mod: str, chan: str):
        mpodID = self.__GenerateMpodID(mod, chan)
        return (eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementCurrent.' + mpodID)))

############################################
    def get_sensed_voltage(self,mod: str, chan: str):
        mpodID = self.__GenerateMpodID(mod, chan)
        return (eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementSenseVoltage.' + mpodID)))


############################################
    def get_terminal_voltage(self,mod: str, chan: str):
        mpodID = self.__GenerateMpodID(mod, chan)
        return (eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputMeasurementTerminalVoltage.' + mpodID)))


############################################
    def get_output_status(self,mod: str, chan: str):
        mpodID = self.__GenerateMpodID(mod, chan)
        return (eval(pxp.run(self.__MakeSnmpGetCommand("public") + ' outputStatus.' + mpodID)))

############################################
    def set_voltage(self,mod: str, chan: str, volts):
        mpodID = self.__GenerateMpodID(mod, chan)
        print(eval(pxp.run(self.__MakeSnmpSetCommand('guru') +
              'outputVoltage.' + mpodID + ' F '+str(volts))))

############################################
    def set_current(self,mod: str, chan: str, current):
        mpodID = self.__GenerateMpodID(mod, chan)
        currentToSet = int(current) * pow(10,-6)
        print(eval(pxp.run(self.__MakeSnmpSetCommand('guru') +
              'outputCurrent.' + mpodID + ' F '+str(currentToSet))))

############################################
    def set_on_off(self,mod: str, chan: str, onOff):
        mpodID = self.__GenerateMpodID(mod, chan)
        print('\033[33m\033[1m' + pxp.run(self.__MakeSnmpSetCommand('guru') + ' outputSwitch.'+mpodID+' i '+str(onOff)).decode())

############################################
    def set_on_off_all(self,onOff):
        for id in self.__ListOfModIndexs:
            for chan in range(int(self.__NumberOfChansPerMod[id])):
                mpodID = self.__GenerateMpodID(id,chan)
                print("[" + mpodID + "] " + pxp.run(self.__MakeSnmpSetCommand('guru') + ' outputSwitch.' + mpodID+' i '+str(onOff)).strip().decode())

############################################
    def set_ramp_all(self,rate):
        for id in self.__ListOfModIndexs:
            for chan in range(int(self.__NumberOfChansPerMod[id])):
                mpodID = self.__GenerateMpodID(id,chan)
                print("[" + mpodID + "] " + pxp.run(self.__MakeSnmpSetCommand('guru') +  ' outputVoltageRiseRate.'+ mpodID+' F '+str(rate)).decode())

############################################
    def set_ramp(self,mod: str, chan: str, rate):
        mpodID = self.__GenerateMpodID(mod,chan)
        print("[" + mpodID + "] " + pxp.run(self.__MakeSnmpSetCommand('guru') +  ' outputVoltageRiseRate.'+ mpodID+' F '+str(rate)).decode())

############################################
    def set_current_limit_all(self,limit):
        limitToSet = int(limit) * pow(10,-6)
        for id in self.__ListOfModIndexs:
            for chan in range(int(self.__NumberOfChansPerMod[id])):
                mpodID = self.__GenerateMpodID(id,chan)
                print("[" + mpodID + "] " + pxp.run(self.__MakeSnmpSetCommand('guru') +  ' outputCurrent.'+ mpodID+' F '+str(limitToSet)).decode())           

############################################
    def SetCrateSwitch(self,Val: int):
        print(self.__redCode + pxp.run(self.__MakeSnmpSetCommand('private') + ' sysMainSwitch.0' + ' i ' + str(Val)).decode())
        if Val == 1:
            print("Waiting ~15 seconds for the modules to boot up")
            chrono.sleep(15)
            self.ReadNumberOfModuleAndChannels()

############################################
    def set_current_limit(self,mod: str, chan: str, limit):
        mpodID = self.__GenerateMpodID(mod, chan)
        limitToSet = int(limit) * pow(10,-6)
        print("[" + mpodID + "] " + pxp.run(self.__MakeSnmpSetCommand('guru') +  ' outputCurrent.'+ mpodID+' F '+str(limitToSet)).decode())   

############################################
    def get_system_status(self):
        smallColWidth=11
        largeColWidth=21
        fullColWidth=smallColWidth*3 + largeColWidth*4
        if self.__GetCrateSysMainStatSTR().lower() == "on":
            print("\n" + f"{'MPOD Controller IP Address::'+self.__resetCode+ self.__yellowCode+self.__IP.strip().center(len(self.__IP.strip())+4)+self.__resetCode: ^{fullColWidth+len(self.__yellowCode)+len(self.__resetCode) + len(self.__IP.strip())}}",end="\n")

            print(f"{'MPOD Chassis Switch Status::'+self.__resetCode+self.__greenCode+'ON'.center(len(self.__IP.strip())+4)+self.__resetCode: ^{fullColWidth+len(self.__greenCode)+len(self.__resetCode) + len(self.__IP.strip())}}",end="\n\n")

            print(f"{self.__underlineCode}{'[CHAN]': ^{smallColWidth}}{'|'}{'[STATUS]': ^{smallColWidth}}{'|'}{'[MEASURED VOLTAGE]': ^{largeColWidth}}{'|'}{'[SET VOLTAGE]': ^{largeColWidth}}{'|'}{'[MEASURED CURRENT]': ^{largeColWidth}}{'|'}{'[CURRENT TRIP]': ^{largeColWidth}}{'|'}{'[RAMP]': ^{smallColWidth}}{self.__resetCode}")
            # print("")

            for id in self.__ListOfModIndexs:
                module_output_string = str()
                for chan in range(int(self.__NumberOfChansPerMod[id])):
                    mpodID = self.__GenerateMpodID(id, chan)
                    mpodSnmpIndex = str(int(mpodID.lstrip("u"))+1)
                    chanData = pxp.run(self.__MakeSnmpGetCommand("guru") + " outputIndex." + mpodSnmpIndex + " outputSwitch." + mpodSnmpIndex + " outputMeasurementSenseVoltage." + mpodSnmpIndex + " outputVoltage." + mpodSnmpIndex + " outputMeasurementCurrent." + mpodSnmpIndex + " outputCurrent." + mpodSnmpIndex + " outputVoltageRiseRate." + mpodSnmpIndex + " outputVoltageFallRate." + mpodSnmpIndex).decode().split("\r\n")

                    chanStr = '[' + chanData[0] + ']' 
                    statStr = chanData[1].upper()
                    colorCode = ""
                    if statStr == "OFF":
                        colorCode = self.__redCode
                    elif statStr == "ON":
                        colorCode = self.__greenCode

                    termVolStr = '{:.2f}'.format(round(float(chanData[2]), 2))+ " V"
                    voltageSetPointStr = '{:.2f}'.format(round(float(chanData[3]), 2)) + " V"

                    # chr(956) is greak mu
                    termCurStr = '{:.3f}'.format(m.ceil(float(chanData[4]) * 1000 * 1000)) + " " + chr(956) + "A"
                    currentTripPointStr = '{:.3f}'.format(m.ceil(float(chanData[5])* 1000 * 1000)) + " " + chr(956) + "A"

                    riseFallRateStr = str(round(float(chanData[6]))) + " V/s"

                    module_output_string += "\n" + \
                        f"{chanStr : ^{smallColWidth}}{'|'}{colorCode}{statStr : ^{smallColWidth}}{self.__resetCode}{'|'}{termVolStr : ^{largeColWidth}}{'|'}{voltageSetPointStr  :^{largeColWidth}}{'|'}{termCurStr  :^{largeColWidth}}{'|'}{currentTripPointStr  :^{largeColWidth}}{'|'}{riseFallRateStr  :^{smallColWidth}}"

                print(module_output_string + "\r\n" +"-".center(fullColWidth+len(self.__underlineCode), "-"),end="")
            print("")
        else:
            print("Crate's sysMainSwitch is " + self.__redCode + "OFF" + self.__resetCode)

############################################
    def write_out_HV(self,filename='mpodcontrol_hv'):
        filename+= "-" + chrono.strftime("%m_%d_%Y_%H%M%S") + ".csv"
        print("Writing to " + filename)
        ouf = open(filename,'w')
        ouf.write("## Module Number , Channel Number , Set Voltage , Set Current Limit\n")
        for mod in self.__ListOfModIndexs:
            for chan in range(int(self.__NumberOfChansPerMod[mod])):
                mpodID=self.__GenerateMpodID(mod,chan)
                setvoltage = pxp.run(self.__MakeSnmpGetCommand("public") + ' outputVoltage.' + mpodID).strip().decode().upper()
                setcurrent = pxp.run(self.__MakeSnmpGetCommand("public") + ' outputCurrent.' + mpodID).strip().decode().upper()
                # print("Chan= " + mpodID + "   V= " + setvoltage + "   A=" + setcurrent)
                ouf.write(str(mod) + "," + str(chan) + "," + setvoltage + "," + setcurrent + "\n")
        ouf.close()

############################################
    def read_in_HV(self,filename):
        if not filename:
            print("Need File to read from.")
            return False

        file = open(filename,'r')
        lines = file.read().splitlines()
        mpodSettings_map =[]
        for curLine in lines:
            if not curLine.startswith("#"): 
                mpodSettings_map.append((curLine.split(",")))

        return(mpodSettings_map)

############################################
    def set_HV_from_read(self,mpodSettings_map):
        print('Setting... ')
        for iter in mpodSettings_map:
            mpodID=self.__GenerateMpodID(int(iter[0]),int(iter[1]))
            volts=iter[2]
            current=iter[3]
            pxp.run(self.__MakeSnmpSetCommand('guru') + 'outputVoltage.' + mpodID + ' F '+str(volts))
            pxp.run(self.__MakeSnmpSetCommand('guru') + 'outputCurrent.' + mpodID + ' F '+str(current))

############################################
    def PrintCrateInfo(self):
        if self.__GetCrateSysMainStatSTR().upper() == "ON":
            colorCode=self.__greenCode
        else:
            colorCode=self.__redCode

        print("sysMainSwitch is currently " + colorCode + self.__GetCrateSysMainStatSTR().upper() + self.__resetCode)
        if self.__GetCrateSysMainStatSTR().lower() == "on":
            print(str(self.__NumberOfModules) + " module(s) found:: Number of Channels per Module " + str(self.__NumberOfChansPerMod))
            print("Total Number of Channels = " + str(self.__NumberOfChannels))
        else:
            print("System's Main Chassis switch is off, no modules can be detected in this state.")
            print("Set the switch to \"ON\", and either rerun this script or run \"ReadNumberOfModuleAndChannels()\"")

############################################
    def Startup(self):
        if self.__GetCrateSysMainStatSTR().upper() == "ON":
            self.ReadNumberOfModuleAndChannels()
            self.PrintCrateInfo()
        else:
            print("sysMainSwitch is OFF. Please enable then run Startup() again")

############################################
    def __SetIP(self,IPtoSet):
        self.__IP = " " + str(IPtoSet) + " "

############################################
    def __init__(self,IP:str=None):
        if IP != None:
            self.__SetIP(IP)
            lockFileName="/tmp/mpodcontroller_" + self.__IP.strip().replace(".","_") + ".lock"
            self.lockfile = open(lockFileName, 'w')
            try:
                fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.Startup()
            except IOError:
                print("Another instance of MPOD Controller is already running at this IP address")
                os._exit(1)
        else:
            print("IP address not given. Trying defaults before bailing")
            counter=0
            while counter<len(self.__ListOfDefaultIPsForMPODs):
                TestIP = self.__ListOfDefaultIPsForMPODs[counter]
                print("trying " + TestIP)
                (out,retcode) = pxp.run("ping -c1 -W1 " + TestIP,withexitstatus=True)
                if retcode == 0:
                    # self.__SetIP(self.__ListOfDefaultIPsForMPODs[counter])
                    macaddress=arp.arpreq(TestIP)
                    if macaddress[0:8].lower() == "30:32:94" or macaddress[0:13].lower() == "00:50:c2:2d:c":
                        print("this is an WIENER thing")
                        thing=pxp.run("snmpget "+ self.__snmpStripAll + self.__snmp_base_options + " -c public " + TestIP + " sysDescr.0").decode().strip().split(" ")
                        print("snmp reports that this is a " + thing[1])
                        if thing[1].upper() == "MPOD":
                            self.__SetIP(TestIP)
                            lockFileName="/tmp/mpodcontroller_" + self.__IP.strip().replace(".","_") + ".lock"
                            self.lockfile = open(lockFileName, 'w')
                            try:
                                fcntl.flock(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                                self.Startup()
                            except IOError:
                                print("Another instance of MPOD Controller is already running at this IP address")
                            break
                        elif thing[1].upper() == "CRATE":
                            print("This is a crate (either pixie or VME)")
                            counter+=1
                elif counter == len(self.__ListOfDefaultIPsForMPODs) - 1:
                    print("Out of default IP addresses to try failing out.")
                    os._exit(1)
                else:
                    print("fail")
                    counter+=1

############################################
    def __del__(self):
        fcntl.flock(self.lockfile, fcntl.LOCK_UN)
        self.lockfile.close()

