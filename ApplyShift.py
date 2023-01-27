import matching2 as m2
import numpy as np
import datetime 

today = datetime.datetime.now()

fp = open("Shift.txt",'r')

pmts = []
shift = []

line = fp.readline()
while line != "":
	pmts.append(int(line.split()[0]))
	shift.append(float(line.split()[2]))
	line = fp.readline()

m2.write_out_HV("tempHV.txt")
for i in range(len(pmts)):
	oldvoltage = m2.get_voltage(pmts[i])
	newvoltage = oldvoltage + shift[i]
	print("Setting PMT",pmts[i],"voltage to",newvoltage)
	m2.set_voltage(pmts[i],newvoltage)


backupnewvoltages="mtasHV.dat_" + today.strftime("%m-%d-%y-%H-%M-%S")
m2.write_out_HV(backupnewvoltages)