####################################################
#basic MPOD control script
####################################################


# Import needs
import pexpect as pxp
import math as m
import time as chrono

####################################################
#                set default values
# ---------------------------------------------------

# set ColorCode
__redCode="\033[31;1m"
__greenCode="\033[32;1m"
__yellowCode="\033[33m"
__resetCode="\033[0m"
__underlineCode="\033[4m"

# Set SNMP and Default THINGS
__snmpStripAll=" -OqvU "
__snmp_base_options = ' -v 2c -m-WIENER-CRATE-MIB -M-/usr/share/snmp/mibs '
__IP = ' 192.168.4.2 '
__snmpget_command = 'snmpget ' + __snmpStripAll +__snmp_base_options + __IP
__snmpBULKget_command = 'snmpbulkget ' + __snmpStripAll + __snmp_base_options + __IP
__ListOfModIndexs = list()
__NumberOfChansPerMod = list()
__NumberOfChannels = int()
__NumberOfModules = int()
##Look at end of File for auto run commands

def __MakeSnmpSetCommand(community):
    return ('snmpset ' + __snmp_base_options + __snmpStripAll + ' -c ' + str(community) + __IP)

def __SetIPOfMpod(ip_to_set):
    __IP = ip_to_set
    print("Updated IP to " + str(__IP) + ":: YOU NEED TO RERUN `ReadNumberOfModuleAndChannels()`")

def __PrintBulks(par):
    print('test bullk returns')
    print(pxp.run(__snmpBULKget_command + "-Cr" + str(__NumberOfChannels) + " -c private " + str(par)).decode())
    __TestVar = pxp.run(__snmpBULKget_command + "-Cr" + str(__NumberOfChannels) + " -c private " + str(par)).decode().strip().split("\r\n")
    print("\n\n\n Now reading from var")
    print(str(__TestVar))
    for i,it in enumerate(__TestVar):
       print(str(it) + "   " + str(i))

####################################################

def ReadNumberOfModuleAndChannels():
    global __ListOfModIndexs
    global __NumberOfChansPerMod
    global __NumberOfChannels
    global __NumberOfModules
    __NumberOfModules = eval(pxp.run('snmpwalk ' + __snmp_base_options + __snmpStripAll + ' -c guru ' + __IP + ' moduleNumber'))
    __ListOfModIndexs= [ int(x[2]) for x in pxp.run('snmpwalk ' + __snmp_base_options + __snmpStripAll + ' -c guru ' + __IP + ' moduleIndex').decode().rstrip("\r\n").split("\r\n") ]
    
    if __NumberOfModules != len(__ListOfModIndexs):
        print("ERROR:: Number of modules reported by snmp for \"moduleNumber\" != the number detected through \"moduleIndex\"")
        return 1
    # print(__ListOfModIndexs)
    
    for i in range(__ListOfModIndexs[-1]+1):
        if i not in __ListOfModIndexs:
            __NumberOfChansPerMod.append(None)
        else:
            modDes=pxp.run('snmpwalk ' + __snmp_base_options + __snmpStripAll + ' -c guru ' + __IP + ' moduleDescription.ma' + str(i)).decode().split(", ")[2]
            __NumberOfChansPerMod.append(modDes)
            __NumberOfChannels +=int(modDes)

    # for i in range(int(__NumberOfModules)):
    #     test = pxp.run('snmpwalk ' + __snmp_base_options + __snmpStripAll + ' -c guru ' + __IP + ' moduleDescription.ma' + str(i)).decode().split(", ")[2]
    #     __NumberOfChansPerMod.append(test)
    #     __NumberOfChannels += int(test)

def GetNumberOfChanPerModule():
    for i,val in enumerate(__NumberOfChansPerMod):
        print("chans per mod " +str(i) + " = " + str(val))

def GetNumberOfModules():
    print("MPOD Crate has " + str(__NumberOfModules) + " installed")

def GenerateMpodID(mod: str, chan: str):
    if mod == 0:
        return "u" + str(chan).zfill(1)
    else:
        return "u" + str(mod) + str(chan).zfill(2)


def SetSafetys(detector: str):
    lowDet = detector.lower()
    if lowDet == "mtas":
        mtasC_max = 1250
        mtasIMO_max = 1450

# Make definitions


def GetCrateSysMainStatus():
    print(__redCode + pxp.run(__snmpget_command +' -c public ' + ' sysMainSwitch.0').decode().upper() + __resetCode)

def __GetCrateSysMainStatSTR():
    retvalue=pxp.run(__snmpget_command +' -c public ' + ' sysMainSwitch.0').decode()
    return(retvalue.replace("\r\n",""))
    

def __SetCrateSwitch(Val):
    print(__redCode + pxp.run(__MakeSnmpSetCommand('private') + ' sysMainSwitch.0' + ' i ' + str(Val)).decode())
    if Val == 1:
        print("Waiting ~15 seconds for the modules to boot up")
        chrono.sleep(15)
        ReadNumberOfModuleAndChannels()



def get_voltage(mod: str, chan: str):
    mpodID = GenerateMpodID(mod, chan)
    return (eval(pxp.run(__snmpget_command + ' -c public ' + ' outputVoltage.'+mpodID)))

def get_current_limit(mod: str, chan: str):
    mpodID = GenerateMpodID(mod, chan)
    print(eval(pxp.run(__snmpget_command + ' -c public outputCurrent.' + mpodID)))


def get_sensed_current(mod: str, chan: str):
    mpodID = GenerateMpodID(mod, chan)
    return (eval(pxp.run(__snmpget_command + ' -c public outputMeasurementCurrent.' + mpodID)))


def get_sensed_voltage(mod: str, chan: str):
    mpodID = GenerateMpodID(mod, chan)
    return (eval(pxp.run(__snmpget_command + ' -c public outputMeasurementSenseVoltage.' + mpodID)))


def get_terminal_voltage(mod: str, chan: str):
    mpodID = GenerateMpodID(mod, chan)
    return (eval(pxp.run(__snmpget_command + ' -c public outputMeasurementTerminalVoltage.' + mpodID)))


def get_output_status(mod: str, chan: str):
    mpodID = GenerateMpodID(mod, chan)
    return (eval(pxp.run(__snmpget_command + ' -c public outputStatus.' + mpodID)))


def set_voltage(mod: str, chan: str, volts):
    mpodID = GenerateMpodID(mod, chan)
    print(eval(pxp.run(__MakeSnmpSetCommand('guru') +
          'outputVoltage.' + mpodID + ' F '+str(volts))))

def set_current(mod: str, chan: str, current):
    mpodID = GenerateMpodID(mod, chan)
    print(eval(pxp.run(__MakeSnmpSetCommand('guru') +
          'outputCurrent.' + mpodID + ' F '+str(current))))

def set_on_off(mod: str, chan: str, onOff):
    mpodID = GenerateMpodID(mod, chan)
    print('\033[33m\033[1m' + pxp.run(__MakeSnmpSetCommand('guru') + ' outputSwitch.'+mpodID+' i '+str(onOff)).decode())

def set_on_off_all(onOff):
    for id in __ListOfModIndexs:
        for chan in range(int(__NumberOfChansPerMod[id])):
            mpodID = GenerateMpodID(id,chan)
            print("[" + mpodID + "] " + pxp.run(__MakeSnmpSetCommand('guru') + ' outputSwitch.' + mpodID+' i '+str(onOff)).strip().decode())

def set_ramp_all(rate):
    for id in __ListOfModIndexs:
        for chan in range(int(__NumberOfChansPerMod[id])):
            mpodID = GenerateMpodID(id,chan)
            print("[" + mpodID + "] " + pxp.run(__MakeSnmpSetCommand('guru') +  ' outputVoltageRiseRate.'+ mpodID+' F '+str(rate)).decode())

def set_ramp(mod: str, chan: str, rate):
    mpodID = GenerateMpodID(mod,chan)
    print("[" + mpodID + "] " + pxp.run(__MakeSnmpSetCommand('guru') +  ' outputVoltageRiseRate.'+ mpodID+' F '+str(rate)).decode())

def set_current_limit_all(limit):
    for id in __ListOfModIndexs:
        for chan in range(int(__NumberOfChansPerMod[id])):
            mpodID = GenerateMpodID(id,chan)
            print("[" + mpodID + "] " + pxp.run(__MakeSnmpSetCommand('guru') +  ' outputCurrent.'+ mpodID+' F '+str(limit)).decode())           

def set_current_limit(mod: str, chan: str, limit):
    mpodID = GenerateMpodID(mod, chan)
    print("[" + mpodID + "] " + pxp.run(__MakeSnmpSetCommand('guru') +  ' outputCurrent.'+ mpodID+' F '+str(limit)).decode())   

def get_system_status():
    smallColWidth=11
    largeColWidth=21
    fullColWidth=smallColWidth*3 + largeColWidth*4
    if __GetCrateSysMainStatSTR().lower() == "on":
        print("\n" + f"{'MPOD Controller IP Address::'+__resetCode+ __yellowCode+__IP.strip().center(len(__IP.strip())+4)+__resetCode: ^{fullColWidth+len(__yellowCode)+len(__resetCode) + len(__IP.strip())}}",end="\n")

        print(f"{'MPOD Chassis Switch Status::'+__resetCode+__greenCode+'ON'.center(len(__IP.strip())+4)+__resetCode: ^{fullColWidth+len(__greenCode)+len(__resetCode) + len(__IP.strip())}}",end="\n\n")
        
        print(f"{__underlineCode}{'[CHAN]': ^{smallColWidth}}{'|'}{'[STATUS]': ^{smallColWidth}}{'|'}{'[MEASURED VOLTAGE]': ^{largeColWidth}}{'|'}{'[SET VOLTAGE]': ^{largeColWidth}}{'|'}{'[MEASURED CURRENT]': ^{largeColWidth}}{'|'}{'[CURRENT TRIP]': ^{largeColWidth}}{'|'}{'[RAMP]': ^{smallColWidth}}{__resetCode}")
        # print("")

        for id in __ListOfModIndexs:
            module_output_string = str()
            for chan in range(int(__NumberOfChansPerMod[id])):
                mpodID = GenerateMpodID(id, chan)
                mpodSnmpIndex = str(int(mpodID.lstrip("u"))+1)
                chanData = pxp.run(__snmpget_command + "-c guru outputIndex." + mpodSnmpIndex + " outputSwitch." + mpodSnmpIndex + " outputMeasurementSenseVoltage." + mpodSnmpIndex + " outputVoltage." + mpodSnmpIndex + " outputMeasurementCurrent." + mpodSnmpIndex + " outputCurrent." + mpodSnmpIndex + " outputVoltageRiseRate." + mpodSnmpIndex + " outputVoltageFallRate." + mpodSnmpIndex).decode().split("\r\n")
                
                chanStr = '[' + chanData[0] + ']' 
                statStr = chanData[1].upper()
                colorCode = ""
                if statStr == "OFF":
                    colorCode = __redCode
                elif statStr == "ON":
                    colorCode = __greenCode
                
                termVolStr = '{:.2f}'.format(round(float(chanData[2]), 2))+ " V"
                voltageSetPointStr = '{:.2f}'.format(round(float(chanData[3]), 2)) + " V"
                
                # chr(956) is greak mu
                termCurStr = '{:.3f}'.format(m.ceil(float(chanData[4]) * 1000 * 1000)) + " " + chr(956) + "A"
                currentTripPointStr = '{:.3f}'.format(m.ceil(float(chanData[5])* 1000 * 1000)) + " " + chr(956) + "A"

                riseFallRateStr = str(round(float(chanData[6]))) + " V/s"

                module_output_string += "\n" + \
                    f"{chanStr : ^{smallColWidth}}{'|'}{colorCode}{statStr : ^{smallColWidth}}{__resetCode}{'|'}{termVolStr : ^{largeColWidth}}{'|'}{voltageSetPointStr  :^{largeColWidth}}{'|'}{termCurStr  :^{largeColWidth}}{'|'}{currentTripPointStr  :^{largeColWidth}}{'|'}{riseFallRateStr  :^{smallColWidth}}"
            
            print(module_output_string + "\r\n" +"-".center(fullColWidth+len(__underlineCode), "-"),end="")
        print("")
    else:
        print("Crate's sysMainSwitch is " + __redCode + "OFF" + __resetCode)

# def set_dv(mod:str,chan:str,dvolts):
# #     print(set_voltage(mtasid,get_voltage(mod,chan)+dvolts))

def write_out_HV(filename='mpodcontrol_hv'):
    filename+= "-" + chrono.strftime("%m_%d_%Y_%H%M%S") + ".csv"
    print("Writing to " + filename)
    ouf = open(filename,'w')
    ouf.write("## Module Number , Channel Number , Set Voltage , Set Current Limit\n")
    for mod in __ListOfModIndexs:
        for chan in range(int(__NumberOfChansPerMod[mod])):
            mpodID=GenerateMpodID(mod,chan)
            setvoltage = pxp.run(__snmpget_command + ' -c public outputVoltage.' + mpodID).strip().decode().upper()
            setcurrent = pxp.run(__snmpget_command + ' -c public outputCurrent.' + mpodID).strip().decode().upper()
            # print("Chan= " + mpodID + "   V= " + setvoltage + "   A=" + setcurrent)
            ouf.write(str(mod) + "," + str(chan) + "," + setvoltage + "," + setcurrent + "\n")
    ouf.close()

def read_in_HV(filename):
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


def set_HV_from_read(mpodSettings_map):
    print('Setting... ')
    for iter in mpodSettings_map:
        mpodID=GenerateMpodID(int(iter[0]),int(iter[1]))
        volts=iter[2]
        current=iter[3]
        pxp.run(__MakeSnmpSetCommand('guru') + 'outputVoltage.' + mpodID + ' F '+str(volts))
        pxp.run(__MakeSnmpSetCommand('guru') + 'outputCurrent.' + mpodID + ' F '+str(volts))
        



def PrintCrateInfo():
    if __GetCrateSysMainStatSTR().upper() == "ON":
        colorCode=__greenCode
    else:
        colorCode=__redCode
    
    print("sysMainSwitch is currently " + colorCode + __GetCrateSysMainStatSTR().upper() + __resetCode)
    if __GetCrateSysMainStatSTR().lower() == "on":
        print(str(__NumberOfModules) + " module(s) found:: Number of Channels per Module " + str(__NumberOfChansPerMod))
        print("Total Number of Channels = " + str(__NumberOfChannels))
    else:
        print("System's Main Chassis switch is off, no modules can be detected in this state.")
        print("Set the switch to \"ON\", and either rerun this script or run \"ReadNumberOfModuleAndChannels()\"")

def Startup():
    if __GetCrateSysMainStatSTR().upper() == "ON":
        ReadNumberOfModuleAndChannels()
        PrintCrateInfo()
    else:
        print("sysMainSwitch is OFF. Please enable then run Startup again")

Startup()

