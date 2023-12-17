import dictmpodcontrol as mc

from rich import print

class MTASMPODController(mc.MPODController):

    center_hv_limit = 1250.0
    imo_hv_limit = 1450.0

    pmt_uid_map = { 
                      'C1F':   'u0', 'C1B':  'u1', 
                      'C2F':   'u2', 'C2B':  'u3',
                      'C3F':   'u4', 'C3B':  'u5',
                      'C4F':   'u6', 'C4B':  'u7',
                      'C5F':   'u8', 'C5B':  'u9',
                      'C6F':  'u10', 'C6B':  'u11',
                      'I1F':  'u12', 'I1B':  'u13', 
                      'I2F':  'u14', 'I2B':  'u15',
                      'I3F': 'u100', 'I3B': 'u101',
                      'I4F': 'u102', 'I4B': 'u103',
                      'I5F': 'u104', 'I5B': 'u105',
                      'I6F': 'u106', 'I6B': 'u107',
                      'M1F': 'u108', 'M1B': 'u109', 
                      'M2F': 'u110', 'M2B': 'u111',
                      'M3F': 'u112', 'M3B': 'u113',
                      'M4F': 'u114', 'M4B': 'u115',
                      'M5F': 'u200', 'M5B': 'u201',
                      'M6F': 'u202', 'M6B': 'u203',
                      'O1F': 'u204', 'O1B': 'u205', 
                      'O2F': 'u206', 'O2B': 'u207',
                      'O3F': 'u208', 'O3B': 'u209',
                      'O4F': 'u210', 'O4B': 'u211',
                      'O5F': 'u212', 'O5B': 'u213',
                      'O6F': 'u214', 'O6B': 'u215'
            }

    def __init__(self,ip=None):
        super().__init__(ip)
        self.uid_pmt_map = {}
        for pmt,uid in self.pmt_uid_map.items():
            self.uid_pmt_map[uid] = pmt

    def get_mod_chan(self,label:str):
        try:
            uid = self.get_uid(label)
            if uid != None:
                mod = self.hvmap[uid]['modid']
                chan = self.hvmap[uid]['chanid']
                return mod,chan
            else:
                return None,None
        except KeyError:
            return None,None

    def get_uid(self,label:str):
        try:
            return self.pmt_uid_map[label.upper()]
        except KeyError:
            print(f'[bold red]ERROR: KEY {label} DOESN\'T EXIST FOR MTAS[/]')
            return None

    def set_pmt_on_off(self,label:str,onOff):
        uid = self.get_uid(label)
        mod = self.hvmap[uid]['modid']
        chan = self.hvmap[uid]['chanid']
        self.set_on_off(mod,chan,onOff)

    def set_on_off_ring(self,ring:str,onOff):
        if ring.upper() == 'CENTER' or ring.upper() == 'C':
            for t in ['F','B']:
                for i in range(1,7):
                    tag = f"C{i}{t}";
                    self.set_pmt_on_off(tag,onOff)
        elif ring.upper() == 'INNER' or ring.upper() == 'I':
            for t in ['F','B']:
                for i in range(1,7):
                    tag = f"I{i}{t}";
                    self.set_pmt_on_off(tag,onOff)
        elif ring.upper() == 'MIDDLE' or ring.upper() == 'M':
            for t in ['F','B']:
                for i in range(1,7):
                    tag = f"M{i}{t}";
                    self.set_pmt_on_off(tag,onOff)
        elif ring.upper() == 'OUTER' or ring.upper() == 'O':
            for t in ['F','B']:
                for i in range(1,7):
                    tag = f"O{i}{t}";
                    self.set_pmt_on_off(tag,onOff)
        else:
            print(f'[bold red]ERROR: UNKNOWN RING TYPE: {ring.upper()}, AVAILABLE TYPES ARE [CENTER,INNER,MIDDLE,OUTER,C,I,M,O][/]')

    def set_on_off_front_back(self,label:str,onOff):
        if label.upper() == "FRONT" or label.upper() == "F":
            for t in ['C','I','M','O']:
                for i in range(1,7):
                    tag = f'{t}{i}F'
                    self.set_pmt_on_off(tag,onOff)
        elif label.upper() == "BACK" or label.upper() == "B":
            for t in ['C','I','M','O']:
                for i in range(1,7):
                    tag = f'{t}{i}B'
                    self.set_pmt_on_off(tag,onOff)
        else:
            print(f'[bold red]ERROR: UNKNOWN FRONT/BACK TYPE: {ring.upper()}, AVAILABLE TYPES ARE [FRONT,BACK,F,B][/]')

    def set_voltage(self,label:str,volt,verbose=True):
        ring = (label.upper())[0]
        if ring == "C":
            if volt <= self.center_hv_limit:
                mod,chan = self.get_mod_chan(label)
                super().set_voltage(mod,chan,volt,verbose)
            else:
                print(f'[bold red]ERROR: UNABLE TO SET VOLTAGE OF {label.upper()} to {volt} V as it exceeds the maximum voltage of {self.center_hv_limit}[/]')
        elif ring == "I" or ring == "M" or ring == "O":
            if volt <= self.imo_hv_limit:
                mod,chan = self.get_mod_chan(label)
                super().set_voltage(mod,chan,volt,verbose)
            else:
                print(f'[bold red]ERROR: UNABLE TO SET VOLTAGE OF {label.upper()} to {volt} V as it exceeds the maximum voltage of {self.center_hv_limit}[/]')
        else:
            print(f'[bold red]ERROR: UNABLE TO SET VOLTAGE AS LABEL: {label} IS INCORRECT AND DOES NOT START WITH C,I,M, OR O')
    
    def get_system_status(self):
        smallColWidth=11
        largeColWidth=21
        fullColWidth=smallColWidth*3 + largeColWidth*4
        if super().GetCrateSysMainStatSTR().lower() == "on":
            print(f'IP: [cyan]{self.IP}[/] Software Switch: [green]ON[/] ')
            if self.Logging:
                print(f'Logging: [green]{self.Logging}[/] VoltageFile: {self.VoltageFilename} CurrentFile: {self.CurrentFilename}')
            else:
                print(f'Logging: [red]{self.Logging}[/]')
            print(f'[underline]{"[PMTNAME]": ^{smallColWidth}}|{"[MODULEID]": ^{smallColWidth}}|{"[CHANID]": ^{smallColWidth}}|{"[CHAN]": ^{smallColWidth}}|{"[STATUS]": ^{smallColWidth}}|{"[MEASURED VOLTAGE]": ^{largeColWidth}}|{"[SET VOLTAGE]": ^{largeColWidth}}|{"[MEASURED CURRENT]" : ^{largeColWidth}}|{"[CURRENT TRIP]": ^{largeColWidth}}|{"[RAMP]": ^{smallColWidth}}[/]')

            firstmodid = self.modlist[0]
            for id,map in self.hvmap.items():
                modid = map['modid']
                chanid = map['chanid']
                status = map['state']
                setv = map['voltage']
                seta = map['current']
                ramp = map['ramp']
                try:
                    pmtname = self.uid_pmt_map[id]
                except KeyError:
                    pmtname = 'NULL'
                
                measurev,measurea  = super().get_sense_voltage_current(modid,chanid)

                measurevstr = f'{measurev:.2f} V'
                setvstr = f'{setv:.2f} V'
                rampstr = f'{ramp:.2f} V/s'

                mu = chr(956)
                newline = '-'
                measureastr = f'{1000*1000*measurea:.2f} {mu}A'
                setastr = f'{1000*1000*seta:.2f} {mu}A'
                if modid != firstmodid:
                    firstmodid = modid
                    print(newline*(5*smallColWidth + 3*largeColWidth + 40))

                if status == 'OFF':
                    print(f'[blue]{pmtname: ^{smallColWidth}}[/][white]|{modid: ^{smallColWidth}}|{chanid: ^{smallColWidth}}|{id: ^{smallColWidth}}|[/][red]{status: ^{smallColWidth}}[/][white]|{measurevstr: ^{largeColWidth}}|{setvstr: ^{largeColWidth}}|{measureastr: ^{largeColWidth}}|{setastr: ^{largeColWidth}}|{rampstr: ^{smallColWidth}}[/]')
                else:
                    print(f'[blue]{pmtname: ^{smallColWidth}}[/][white]|{modid: ^{smallColWidth}}|{chanid: ^{smallColWidth}}|{id: ^{smallColWidth}}|[/][green]{status: ^{smallColWidth}}[/][white]|{measurevstr: ^{largeColWidth}}|{setvstr: ^{largeColWidth}}|{measureastr: ^{largeColWidth}}|{setastr: ^{largeColWidth}}|{rampstr: ^{smallColWidth}}[/]')
            
        else:
            print(f'IP: [cyan]{self.__IP}[/] Sofware Switch: [red]OFF[/]')


    def get_voltage(self,label:str,verbose=True):
        try:
            uid = self.get_uid(label)
            mod,chan = self.get_mod_chan(label)
            if mod != None and chan != None:
                volt = super().get_voltage(mod,chan,False)
                if verbose:
                    print(f'[white] PMT {label.upper()} has a voltage of {volt}[/]')
                return volt
            else:
                print(f'[bold red]ERROR: UNABLE TO GET VOLTAGE OF {label.upper()} AS IT IS NOT A KNOWN MTAS CHANNEL[/]')
        except KeyError:
            print(f'[bold red]ERROR: UNABLE TO GET VOLTAGE OF {label.upper()} AS IT IS NOT A KNOWN MTAS CHANNEL[/]')
