#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

templabels=["Fan Inlet","Ext. 1","Ext. 3","Ext. 5"]
degatemplabels=["Fan Inlet","Ext. 1"]
probelabels=["Ext Vandle","Ext Dega","Int Front","Int Back"]

def readfile(filename:str):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    split_values = []
    for line in lines:
        values = line.split()
        split_values.append([int(x) for x in values])
    arr = np.array(split_values) 
    transposed_arr = [[] for i in range(np.shape(arr)[1])]
    for vals in arr:
        for i in range(len(vals)):
            transposed_arr[i].append(vals[i])
    return np.array(transposed_arr)

def plottemps(data,filename,tmplbls):
    fig=plt.figure()
    for i in range(len(tmplbls)):
        plt.plot(data[0],data[i+1],label=templabels[i])
    plt.xlabel('seconds')
    plt.ylabel('temperature (celcius)')
    plt.legend()
    fig.show()
    fig.savefig('plots/temp/'+filename+'.png')
    fig.savefig('plots/temp/'+filename+'.svg')

if __name__ == "__main__":
    degatempfile="temps.pixie.dega"
    degatemps=readfile(degatempfile)
    plottemps(degatemps,degatempfile,degatemplabels)

    mtastempfile="temps.pixie.mtas"
    mtastemps=readfile(mtastempfile)
    plottemps(mtastemps,mtastempfile,templabels)

    vandletempfile="temps.pixie.vandle"
    vandletemps=readfile(vandletempfile)
    plottemps(vandletemps,vandletempfile,templabels)

    with open('plots/temp/currentdega.txt','w') as file:
        file.write('{} {}'.format(degatemps[1][-1],degatemps[2][-1]))
    
    with open('plots/temp/currentvandle.txt','w') as file:
        file.write('{} {} {} {}'.format(vandletemps[1][-1],vandletemps[2][-1],vandletemps[3][-1],vandletemps[4][-1]))
    
    with open('plots/temp/currentmtas.txt','w') as file:
        file.write('{} {} {} {}'.format(mtastemps[1][-1],mtastemps[2][-1],mtastemps[3][-1],mtastemps[4][-1]))


    #mtas temp probes
    probes='/home/pixie16/DAQ_1/kelvin/log/therm-SunJan1411:21:382024.log'
    probetemps=np.genfromtxt(probes,skip_header=3)
    transposed_arr = [[] for i in range(np.shape(probetemps)[1])]
    for vals in probetemps:
        for i in range(len(vals)):
            transposed_arr[i].append(vals[i])
    plottemps(transposed_arr,'temps.mtasprobes',probelabels)
    
    with open('plots/temp/currentmtasprobes.txt','w') as file:
        file.write('{} {} {} {}'.format(transposed_arr[1][-1],transposed_arr[2][-1],transposed_arr[3][-1],transposed_arr[4][-1]))
