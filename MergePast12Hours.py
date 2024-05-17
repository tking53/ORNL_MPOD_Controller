#!/usr/bin/python3
import numpy as np
import os
basenames = {
        'dega' : ['fans.tsv','temps.tsv','currents.tsv','voltages.tsv'],
        'mtas' : ['fans.tsv','temps.tsv','currents.tsv','voltages.tsv'],
        'vandle' : ['fans.tsv','temps.tsv','currents.tsv','voltages.tsv'],
        'mtas-mpod' : ['currents.tsv','voltages.tsv'],
        'mtas-probes' : ['temps.tsv']
        }

def get_past_files(directory:str,prefix:str):
    all_files = os.listdir(directory)
    creation_times = [(file,os.stat(os.path.join(directory,file)).st_ctime) for file in all_files if os.path.basename(file).startswith(prefix) ]
    sorted_files = sorted(creation_times, key=lambda x: x[1])
    sorted_file_names = [directory+file[0] for file in sorted_files][::-1]
    return (sorted_file_names[:min(12,len(sorted_file_names))])[::-1]

def merge_data(key:str,directory:str):
    for prefix in basenames[key]:
        currdata = get_past_files(directory,prefix)
        outputfile = directory+key+'-cumulative-'+prefix
        with open(outputfile,'w') as output:
            for datafile in currdata:
                with open(datafile,'r') as inputfile:
                    content = inputfile.read()
                    output.write(content)


if __name__ == "__main__":
    basedir="/home/pixie16/MTAS_MPOD_CONTROLLER/logs/"

    logdirs = { 'dega' : basedir+"dega/", 'mtas' : basedir+"mtas/", 'vandle' : basedir+"vandle/" , 'mtas-mpod' : basedir+"mtas_mpod/" , 'mtas-probes' : basedir+"mtas_probes/"}
    for key,item in logdirs.items():
        merge_data(key,item)
