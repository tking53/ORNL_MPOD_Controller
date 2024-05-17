#!/usr/bin/python3
import PlotLogFiles as plf
import os

if __name__ == "__main__":
    volts = "/home/pixie16/MTAS_MPOD_CONTROLLER/complete_v.txt"
    current = "/home/pixie16/MTAS_MPOD_CONTROLLER/complete.txt"
    a = plf.LogPlotter(volts,current)
    for cimo in ["C","I","M","O"]:
        for i in range(1,7):
            for fb in ["F","B"]:
                id = "{}{}{}".format(cimo,i,fb)
                a.plot_single_voltage(id,True)
                a.save_plot("plots/voltage/{}.png".format(id))
                a.plot_single_current(id,True)
                a.save_plot("plots/current/{}.png".format(id))
