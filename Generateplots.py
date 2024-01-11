#!/usr/bin/python3
import PlotLogFiles as plf

if __name__ == "__main__":
    volts = "complete_v.txt"
    current = "complete.txt"
    a = plf.LogPlotter(volts,current)
    for cimo in ["C","I","M","O"]:
        for i in range(1,7):
            for fb in ["F","B"]:
                id = "{}{}{}".format(cimo,i,fb)
                a.plot_single_voltage(id,True)
                a.save_plot("plots/voltage/{}.png".format(id))
                a.plot_single_current(id,True)
                a.save_plot("plots/current/{}.png".format(id))
