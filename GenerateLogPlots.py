#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from matplotlib.dates import date2num
from itertools import chain

#mtastemplabels=["Fan Inlet","Ext. 1","Ext. 3","Ext. 5"]
#degatemplabels=["Fan Inlet","Ext. 1"]
#mtasprobelabels=["Ext Vandle","Ext Dega","Int Front","Int Back"]

fig=plt.figure()

labels = {
        'dega' : {'fans' : ["dega-Fan1","dega-Fan2","dega-Fan3"], 'temps' : ["dega-Fan Inlet","dega-Ext. 1",None,None,None,None,None,None,None], 'currents' : ["+5V5","+12V","+5V0","+3V3","-12V","-6V0","+1V8"], 'voltages' : ["+5V5","+12V","+5V0","+3V3","-12V","-6V0","+1V8"]},
        'mtas' : {'fans' : ["mtas-Fan1","mtas-Fan2","mtas-Fan3"], 'temps' : ["mtas-Fan Inlet","mtas-Ext. 1",None,"mtas-Ext. 3",None,"mtas-Ext. 5",None,None,None], 'currents' : ["+5V5","+12V","+5V0","+3V3","-12V","-6V0","+1V8"], 'voltages' : ["+5V5","+12V","+5V0","+3V3","-12V","-6V0","+1V8"]},
        'vandle' : {'fans' : ["vandle-Fan1","vandle-Fan2","vandle-Fan3"], 'temps' : ["vandle-Fan Inlet","vandle-Ext. 1",None,"vandle-Ext. 3",None,"vandle-Ext. 5",None,None,None], 'currents' : ["+5V5","+12V","+5V0","+3V3","-12V","-6V0","+1V8"], 'voltages' : ["+5V5","+12V","+5V0","+3V3","-12V","-6V0","+1V8"]},
        'mtas-mpod' : {'currents' : [],'voltages' : []},
        'mtas-probes' : {'temps' : ["Ext. Vandle","Ext. Dega","Int. Front","Int. Back"]}
        }

ylabels = {
        'dega' : {'fans':'RPM','temps':'celcius','currents':'Amps','voltages':'volts'},
        'mtas' : {'fans':'RPM','temps':'celcius','currents':'Amps','voltages':'volts'},
        'vandle' : {'fans':'RPM','temps':'celcius','currents':'Amps','voltages':'volts'},
        'mtas-mpod' : {'currents':'microAmps','voltages':'volts'},
        'mtas-probes' : {'temps' : 'celcius'}
        }

ylimits = {
        'dega' : {'fans' : [2000,4000],'temps': [15,50],'currents':[0.0,100],'voltages':[-24,24]},
        'mtas' : {'fans' : [2000,4000],'temps': [15,50],'currents':[0.0,100],'voltages':[-24,24]},
        'vandle' : {'fans' : [2000,4000],'temps': [5,60],'currents':[0.0,100],'voltages':[-24,24]},
        'mtas-mpod' : {'currents':[0.0,500.0],'voltages':[650,1450]},
        'mtas-probes' : {'temps' : [15.0,30.0]}
        }

def transpose_arr(arr):
    transposed_arr = [[] for i in range(np.shape(arr)[1])]
    for vals in arr:
        for i in range(len(vals)):
            transposed_arr[i].append(vals[i])
    return transposed_arr

def get_all_files_with_suffix(directory:str,suffix:str):
    all_files = os.listdir(directory)
    filtered_files = {}
    for file in all_files: 
        if file.endswith(suffix):
            filtered_files[os.path.splitext(file)[0]] = directory+file
    return filtered_files

def smooth_arr(arr,window_size):
    return [(sum(arr[i:min(i+window_size,len(arr))]) / min(window_size, len(arr)-i)) for i in range(len(arr))] 

def process_logs(key:str,directory:str):
    files=get_all_files_with_suffix(directory,'tsv')
    for valtype,file in files.items():
        currlabels=labels[key][valtype]
        
        arr=[[] for x in range(len(currlabels)+1)]
        with open(file,'r') as read:
            lines=read.readlines()
        split_values = []

        for line in lines:
            values = line.rstrip('\n').split('\t')[:-1]
            measure = [float(x) for x in values[2:]]
            currdate = date2num(datetime.strptime(values[0]+' '+values[1], "%Y-%m-%d %H:%M:%S"))
            arr[0].append(currdate)
            for x in range(len(currlabels)):
                arr[x+1].append(measure[x])
        arr = np.array(arr)
        if 'cumulative' in valtype:
            temparr= [arr[0]]
            for x in arr[1:]:
                temparr.append(smooth_arr(x,10))
            arr = temparr

        fig.clear()
        for x in range(len(currlabels)):
            if currlabels[x] is not None:
                plt.plot(arr[0],arr[x+1],linewidth=1,label=currlabels[x])
                fig.show()
        fig.gca().xaxis_date()
        plt.xlabel('Date and Time')
        plt.ylabel(ylabels[key][valtype])
        #plt.ylim(ylimits[key][valtype])
        minval = min([item for sublist in arr[1:] for item in sublist])
        maxval = max([item for sublist in arr[1:] for item in sublist])
        plt.ylim(ylimits[key][valtype])
        plt.legend()
        root, _ = os.path.splitext(file)
        newfilename=root+'-'+key+".png"
        fig.savefig(newfilename)
        newfilename=root+'-'+key+".svg"
        fig.savefig(newfilename)
        if valtype == 'temps':
            outfile = os.path.dirname(file)+'/current.txt'
            finaltemps = [arr[y+1][-1] for y in range(len(currlabels)) if currlabels[y] is not None]
            with open(outfile,'w') as finaldump:
                finaldump.write(f"{' '.join(map(str,finaltemps))}")
        if key == 'mtas-mpod':
            fig.clear()
            for x in range(len(currlabels)):
                if currlabels[x] is not None:
                    fig.clear()
                    plt.plot(arr[0],arr[x+1],linewidth=1,label=currlabels[x])
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    if valtype == 'temps' :
                        plt.ylim(ylimits[key][valtype])
                    else:
                        minval = min(arr[x+1])
                        maxval = max(arr[x+1])
                        plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
                    root = os.path.dirname(file)
                    newfilename=root+"/"+valtype+'-'+currlabels[x]+".png"
                    fig.savefig(newfilename)
                    newfilename=root+"/"+valtype+'-'+currlabels[x]+".svg"
                    fig.savefig(newfilename)
            
            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 0 and index < 12:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-center-front.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-center-front.svg'
            fig.savefig(newfilename)

            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 1 and index < 12:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-center-back.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-center-back.svg'
            fig.savefig(newfilename)
            
            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 0 and index < 24 and index >= 12:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-inner-front.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-inner-front.svg'
            fig.savefig(newfilename)

            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 1 and index < 24 and index >= 12:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-inner-back.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-inner-back.svg'
            fig.savefig(newfilename)
            
            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 0 and index < 36 and index >= 24:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-middle-front.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-middle-front.svg'
            fig.savefig(newfilename)

            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 1 and index < 36 and index >= 24:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-middle-back.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-middle-back.svg'
            fig.savefig(newfilename)
            
            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 0 and index < 48 and index >= 36:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-outer-front.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-outer-front.svg'
            fig.savefig(newfilename)

            fig.clear()
            for index, value in enumerate(currlabels):
                if index % 2 == 1 and index < 48 and index >= 36:
                    plt.plot(arr[0],arr[index+1],linewidth=1,label=value)
                    fig.show()
                    fig.gca().xaxis_date()
                    plt.xlabel('Date and Time')
                    plt.ylabel(ylabels[key][valtype])
                    #plt.ylim(ylimits[key][valtype])
                    minval = min(arr[index+1])
                    maxval = max(arr[index+1])
                    plt.ylim(minval-1.0,maxval+1.0)
                    plt.legend()
            root = os.path.dirname(file)
            newfilename=root+"/"+valtype+'-outer-back.png'
            fig.savefig(newfilename)
            newfilename=root+"/"+valtype+'-outer-back.svg'
            fig.savefig(newfilename)


if __name__ == "__main__":
    basedir="/home/pixie16/MTAS_MPOD_CONTROLLER/logs/"

    logdirs = { 'dega' : basedir+"dega/", 'mtas' : basedir+"mtas/", 'vandle' : basedir+"vandle/" , 'mtas-mpod' : basedir+"mtas_mpod/" , 'mtas-probes' : basedir+'mtas_probes/'}
    for cimo in ["C","I","M","O"]:
        for i in range(1,7):
            for fb in ["F","B"]:
                id = "{}{}{}".format(cimo,i,fb)
                labels['mtas-mpod']['currents'].append(id)
                labels['mtas-mpod']['voltages'].append(id)
    labels['mtas-mpod']['currents'].append('OGS')
    labels['mtas-mpod']['voltages'].append('OGS')
    for i in range(7):
        labels['mtas-mpod']['currents'].append(None)
        labels['mtas-mpod']['voltages'].append(None)
    
    templabels = {}
    for key,value in labels.items():
        for innerkey,innervalue in value.items():
            templabels[key+'-cumulative-'+innerkey] = labels[key][innerkey]
    for key,value in logdirs.items():
        for innerkey,innervalue in templabels.items():
            labels[key][innerkey] = innervalue
    
    templabels = {}
    for key,value in ylabels.items():
        for innerkey,innervalue in value.items():
            templabels[key+'-cumulative-'+innerkey] = ylabels[key][innerkey]
    for key,value in logdirs.items():
        for innerkey,innervalue in templabels.items():
            ylabels[key][innerkey] = innervalue
 
    templabels = {}
    for key,value in ylimits.items():
        for innerkey,innervalue in value.items():
            templabels[key+'-cumulative-'+innerkey] = ylimits[key][innerkey]
    for key,value in logdirs.items():
        for innerkey,innervalue in templabels.items():
            ylimits[key][innerkey] = innervalue

    for key,value in logdirs.items():
        process_logs(key,value)
