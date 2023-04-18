# ORNL MPOD Controller

This Python script provides control and monitoring functionality for the MPOD Power Supply used at Oak Ridge National Laboratory (ORNL).

## Functionality

The script allows users to:

- Connect to the MPOD Power Supply over local network.
- Configure and set output voltage, current, and trip values.
- Turn on and off individual output channels.
- Monitor the status of individual output channels, including voltage, current, and trip status.

## Inputs and Outputs

The script requires the following inputs:

- IP address of the MPOD Power Supply

The script provides the following outputs:

- Status information about the MPOD Power Supply, including voltage, current, and trip status for each output channel.

## Dependencies

The script requires the following package based dependencies:
- Python 3.6 or later with pip
- snmp utilities 
    - Ubuntu: `sudo apt install snmp`
    - RHEL 7: `sudo yum install net-snmp-utils`
    - RHEL 8: `sudo dnf install net-snmp-utils`

We also require some `pip` dependencies. These dependencies can be installed with the `--user` flag in `pip`.
- [python-arpreq](https://github.com/sebschrader/python-arpreq)
- [pexpect](https://github.com/pexpect/pexpect)

Windows and MacOS are NOT supported due to the incompatibility of `python-arpreq` with those operating systems. This is not an issue for us but it should be noted. I suspect that WSL2 would work but this is not one of our use case so it is not planned.

Below you can find the one liner lazy-mode install for RHEL 7:
```bash
sudo yum install python3 python3-pip net-snmp-utils && pip3 install --user pexpect arpreq
```

## Post installation / How to Run

You need to copy the `WIENER-CRATE-MIB.txt` file to the default path of `/usr/share/snmp/mibs`. You should be able to change the `self.__snmp_base_options` variable at the head of the class to point to where you have placed the `WIENER-CRATE-MIB.txt` file (This is untested but should be supported by snmp itself). We might add a second search path for systems without root/sudo access (FRIB-DAQs for example). We will provide no dynamic way to change this unless it is found to be needed for ourselves. PRs are welcome though if your use case needs this.

You can/should add this folder to your shell's `PYTHONPATH`. This will allow you to call the module from any folder.  NOTE: When reading and writing the Channel Settings from/to files, it will be from the current working directory at launch of `ipython`. Full paths with the filename as the argument should work but as of right now ( Mid-April 2023) it hasnt been fully tested (coming soon).
```bash
export PYTHONPATH="${PYTHONPATH}:<Path/To/ClonedFolder>"
```

The script is intended to be run from ipython. An example is:

We can take the IP address of the MPOD directly incase it is not at one of our usual default IPs.
```python
import mpodcontrol as mc
a = mc.MPODController("000.000.000.000")
```

We can also query a list of our usual IPs for MPODs but it should be noted that if you use this form; we expect that there is one and only one MPOD at the IP addresses listed in `MPODController.__ListOfDefaultIPsForMPODs`. We will always pick the first one that passes the checks in this mode. These checks are against the MAC address prefix registed to WIENER, and a query of the `sysDescr` parameter via `snmp`, to identify MPODs vs U6000 Crates. 
```python
import mpodcontrol as mc
a = mc.MPODController()
```
In either case, the commands can be accessed like below: 
```python
a.get_system_status()
a.PrintCrateInfo()
```

## Use Cases

This script can be used for a variety of purposes, including:

- Setting up and configuring the MPOD Power Supply for experiments.
- Monitoring the status of the MPOD Power Supply during experiments.
- Automating the setup and configuration of the MPOD Power Supply.


## Licence
This project is licenced under the MIT licence.

The MIT License (MIT)

Copyright (c) 2023 T. T. King

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
