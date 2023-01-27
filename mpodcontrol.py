####################################################
####################################################


#Import needs
import pexpect as pxp
import datetime 
import numpy as np

####################################################
#                set default values
#---------------------------------------------------

#set safetys
maxVoltIMO=1450
maxVoltC=1250
snmp_options=' -OqvU -v 2c -M /usr/share/snmp/mibs -m +WIENER-CRATE-MIB '
IP='192.168.4.2'
snmpget_command= 'snmpget ' + snmp_options + IP
snmpset_command= 'snmpset ' + snmp_options + IP

#Read in channel map. 
# channels=range(1,49)
#define dicts
# hv_response=dict()
# for i in channels:
#     hv_response[repr(i)]=[10,0,0,0]
#inf=open('response.dat','r')
#lines = inf.readlines()
#hv_response=eval(lines[0])

hvmap=dict()
lines = np.genfromtxt('hvmap.csv',(np.character,int),delimiter=' , ')
for i in lines:
    hvmap[i[1].decode()]={'id':i[0].decode(),'val':10}
       
####################################################

def GenerateMpodID(mod:str,chan:str):
    if mod == 0:
        return "u" + str(chan).zfill(2)
    else:
        return "u" + str(mod) + str(chan).zfill(2)

#Make definitions
def get_voltage(mod:str,chan:str):
    mpodID = GenerateMpodID(mod,chan)
    return(eval(pxp.run(snmpget_command + '-c guru' + ' outputVoltage.'+mpodID)m )

# def get_voltage(mtasid):
#     return(eval(pxp.run(snmpget_command + ' outputVoltage.'+hvmap[repr(mtasid+100)]['id']).decode().split('\r\n')[0]))

def get_current_limit(mtasid):
    return(eval(pxp.run(snmpget_command + ' outputCurrent.'+hvmap[repr(mtasid+100)]['id']).decode().split('\r\n')[0]))

def get_sensed_current(mtasid):
    return(eval(pxp.run(snmpget_command + ' outputMeasurementCurrent.'+hvmap[repr(mtasid+100)]['id']).decode().split('\r\n')[0]))

def get_sensed_voltage(mtasid):
    return(eval(pxp.run(snmpget_command + ' outputMeasurementSenseVoltage.'+hvmap[repr(mtasid+100)]['id']).decode().split('\r\n')[0]))

def get_output_status(mtasid):
    return(eval(pxp.run(snmpget_command + ' outputStatus.'+hvmap[repr(mtasid+100)]['id']).decode().split('\r\n')[0]))

def set_voltage(mtasid,volts):
    if mtasid<12:
        if volts>maxVoltC:
            print('C HV too high')
            return(False)
    else:
        if volts>maxVoltIMO:
            print('IMO HV too high')
            return(False)
    #pxp.time.sleep(1)
    return(eval(pxp.run(snmpset_command + ' outputVoltage.'+hvmap[str(mtasid+100)]['id']+' F '+str(volts))))

def set_all_on_off(onOff):
    for mtasid in range(0,48):
        print(pxp.run(snmpset_command + ' outputSwitch.'+hvmap[str(mtasid+100)]['id']+' i '+str(onOff)))

def set_singlechannel_on_off(mtasid,onOff):
    print(pxp.run(snmpset_command + ' outputSwitch.'+hvmap[str(mtasid+100)]['id']+' i '+str(onOff)))
    
def set_rise_rate_all(rate):
    for mtasid in range(0,48,16):
        print(eval(pxp.run(snmpset_command + ' outputVoltageRiseRate.'+hvmap[str(mtasid+100)]['id']+' F '+str(rate))))

def set_dv(mtasid,dvolts):
    print(set_voltage(mtasid,get_voltage(mtasid)+dvolts))

def write_out_HV(filename='dat_files/hv_mtas.dat'):
    ouf = open(filename,'w')
    for i in channels:
        ouf.write(str(i)+' , '+repr(get_voltage(i-1))+'\n')
    ouf.close()
    
def read_in_HV(filename='dat_files/hv_mtas.dat'):
    inf = open(filename,'r')
    lines = inf.readlines()
    hv_array =[]
    for i in lines:
        hv_array.append(eval(i))
    return(hv_array)
    
def set_HV_from_read(hv_array):
    for i in hv_array:
        print('Setting... ')
        print(set_voltage(i[0]-1,i[1]))

#def interpolate(dic,id):

def dict_add(id,dic,volt,pk):
    diff = (dic[repr(id)][1]-volt)/(dic[repr(id)][2]-pk)
    dic[repr(id)][1]=volt
    dic[repr(id)][2]=pk
    n=dic[repr(id)][3]
    if (n!=0):
        dic[repr(id)][0]=dic[repr(id)][0]*n/(n+1)+diff/(n+1)
    dic[repr(id)][3]+=1



