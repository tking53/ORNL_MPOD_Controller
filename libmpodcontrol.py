##############################################

# Libary of mpod commands

import subprocess as sup


class mpodcontrol:
    def __init__(self,ip_str = " "):
        self.__setIP(ip_str)
        if self.ip_str == " ":
            pingcheck = sup.Popen   

#            -OqvU -v 2c -M /usr/share/snmp/mibs -m +WIENER-CRATE-MIB"


    def __getIP(self):
        return self.__ip_str

    def __setIP(self,ip_str):
        self.__ip_str = ip_str
    
    def __delIP(self):
        del self.__ip_str 

    ip_str = property(__getIP,__setIP,__delIP,"IPv4 address of the MPOD controller")
