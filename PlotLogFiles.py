import matplotlib.pyplot as plt
import numpy as np

class LogPlotter:
    def __init__(self,voltfile:str,currentfile:str):
        self.pmt_map = { 
                'C1F':  0, 'C1B':  1, 
                'C2F':  2, 'C2B':  3,
                'C3F':  4, 'C3B':  5,
                'C4F':  6, 'C4B':  7,
                'C5F':  8, 'C5B':  9,
                'C6F': 10, 'C6B': 11,
                'I1F': 12, 'I1B': 13, 
                'I2F': 14, 'I2B': 15,
                'I3F': 16, 'I3B': 17,
                'I4F': 18, 'I4B': 19,
                'I5F': 20, 'I5B': 21,
                'I6F': 22, 'I6B': 23,
                'M1F': 24, 'M1B': 25, 
                'M2F': 26, 'M2B': 27,
                'M3F': 28, 'M3B': 29,
                'M4F': 30, 'M4B': 31,
                'M5F': 32, 'M5B': 33,
                'M6F': 34, 'M6B': 35,
                'O1F': 36, 'O1B': 37, 
                'O2F': 38, 'O2B': 39,
                'O3F': 40, 'O3B': 41,
                'O4F': 42, 'O4B': 43,
                'O5F': 44, 'O5B': 45,
                'O6F': 46, 'O6B': 47
                }
        self.voltages = self.load_data(voltfile)
        self.currents = self.load_data(currentfile)
        self.fig = plt.figure()
        self.timescaling = 5

    def plot_single(self,yaxis,ylabel,label,clear = True):
        xaxis = [i*self.timescaling for i in range(len(yaxis))]
        if clear :
            self.fig.clear()
        plt.plot(xaxis,yaxis,label=label)
        plt.xlabel('seconds')
        plt.ylabel(ylabel)
        plt.legend()
        self.fig.show()

    def plot_multi_voltage(self,pmtlist:str,clear=False):
        strlist = pmtlist.split()
        if clear:
            self.fig.clear()
        for id in strlist:
            self.plot_single_voltage(id,False)

    def plot_multi_current(self,pmtlist:str,clear=False):
        strlist = pmtlist.split()
        if clear:
            self.fig.clear()
        for id in strlist:
            self.plot_single_current(id,False)

    def plot_single_voltage(self,pmtname:str,clear=False):
        yaxis = self.voltages[pmtname]
        self.plot_single(yaxis,'volts',pmtname,clear)

    def plot_single_current(self,pmtname:str,clear=False):
        yaxis = self.currents[pmtname]
        self.plot_single(yaxis,'microamps',pmtname,clear)

    def load_data(self,filename:str):
        self.pmtname = [name for name,cnt in self.pmt_map.items()]
        datatype = [float for name,cnt in self.pmt_map.items()]
        data = np.genfromtxt(filename,names=self.pmtname,dtype=datatype,encoding='utf-8')
        return data
