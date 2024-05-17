#!/bin/bash
cmd="snmpget -v 2c -m-WIENER-CRATE-MIB -M-/usr/share/snmp/mibs -OqvU -c public "

mtasip=" 192.168.13.236 "
mtaslabels=(" fanAirTemperature.0 " " sensorTemperature.temp1 " " sensorTemperature.temp3 " " sensorTemperature.temp5 ") 
mtasfile="temps.pixie.mtas"

degaip=" 192.168.13.236 "
degalabels=(" fanAirTemperature.0 " " sensorTemperature.temp1 " ) 
degafile="temps.pixie.dega"

vandleip=" 192.168.13.236 "
vandlelabels=(" fanAirTemperature.0 " " sensorTemperature.temp1 " " sensorTemperature.temp3 " " sensorTemperature.temp5 ") 
vandlefile="temps.pixie.vandle"

pollcounts=0
maxpollcounts=3600
hourcount=0
maxhourcount=12
seconds=0
current_datetime=$(date +"%Y-%m-%d %H:%M")
timelog="pixie.log"
echo $current_datetime >> $timelog

while [ "$hourcount" -le "$maxhourcount" ];do
	while [ "$pollcounts" -le "$maxpollcounts" ]; do
		temps=()
		for lbl in "${mtaslabels[@]}";do
			fullcmd=("$cmd $mtasip $lbl")
			tmp=$($fullcmd)
			temps+=($tmp)
		done
		(echo "$pollcounts ${temps[@]}" >> $mtasfile)

		temps=()
		for lbl in "${degalabels[@]}";do
			fullcmd=("$cmd $degaip $lbl")
			tmp=$($fullcmd)
			temps+=($tmp)
		done
		(echo "$pollcounts ${temps[@]}" >> $degafile)

		temps=()
		for lbl in "${vandlelabels[@]}";do
			fullcmd=("$cmd $vandleip $lbl")
			tmp=$($fullcmd)
			temps+=($tmp)
		done
		(echo "$pollcounts ${temps[@]}" >> $vandlefile)
		sleep 5
		((pollcounts+=1))
		((seconds+=5))
	done
	((hourcount+=1))
done
