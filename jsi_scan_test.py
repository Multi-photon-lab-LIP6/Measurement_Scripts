# -*- coding: utf-8 -*-
"""
Script should control the pure photonics and the OSA20
We choose the range that we want to sweep our seed's ("signal") wavelength
and record the spectrum of the "idler" recorded by the OSA over a fixed number of avareged scans
We save the data in diff files
"""

import numpy as np
import os
import time
import sys

from datetime import datetime

import OSA20_Ethernet as osa
from itla import ITLAConnect, ITLA

BUFFER_SIZE = 1024

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\OSA_Test_" + str(filestamp)
DATADIR = os.getcwd()+"\Data"+TYPE

###############################################################################
# Pure photonics settings
sercon = ITLAConnect("COM5", baudrate=9600)
print("sercon: ", sercon)

ITLA(sercon, 0x31, 1800, 1) # sets the output power (Reange is [600,1800] [dBm]/100)

# # Creates a list of frequencies, f_list, we want to sweep depending on the range of wavelength [start,stop] [m] and increments of inc [m].
c=299792458
start=1548.5*1e-9
stop=1553.5*1e-9
inc=20*1e-12
no_points=(stop-start)/inc
w_list=np.linspace(start,start+round(no_points)*inc,round(no_points)+1)
f_list=c/w_list # In Hz

###############################################################################
# Startin the measurement
for iter, freq in enumerate(f_list):
    ITLA(sercon, 0x35, int(freq * 1e-12), 1) # Setting the frequency (THz register)
    ITLA(sercon, 0x36, int((freq * 1e-12 - int(freq * 1e-12)) * 10000), 1) # Setting the frequency (GHz resgister)
    ITLA(sercon, 0x32, 0x08, 1) # Laser on

    time.sleep(25)
    print(f"iter, freq, w_list[iter]: {iter}, {freq}, {w_list[iter]}")

    #######################
    # OSA starts aquisition
    NUM_SCANS = 14

    # :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop)
    set_single = ":INIT:SMOD 1;:INIT:TMOD 0\r\n"
    # :TRAC1:TYPE 2 -> continuous average
    trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 2\r\n"
    # :SENS:SENS 6 -> max sensitivity
    sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1548nm;:SENS:WAV:STOP 1554nm;:SENS:BAND:NAT 1;:SENS:TIME:INT:ENAB 0\r\n"

    trace_mW, trace_dBm, L_start, sampling, Length, PT_list, SW_results = osa.scan(NUM_SCANS, set_single, trace_params, sens_params)
    
    #######################
    # Saving data
    param_dir = DATADIR + "_Mira_on\\" + f"signal_{w_list[iter]}nm" #os.getcwd()+f"\Data\OSA_Test_20230927100000_Background\signal_{w_list[iter]}nm"
    os.makedirs(param_dir, exist_ok=True)
    with open(param_dir + "\params.txt", mode="w") as f:
        f.write(f"L_start       sampling      Length    \n")
        f.write(f"{L_start}         {sampling}          {Length}\n")
        f.write(f"PT_list: {PT_list} \n")
        f.write(f"SW_results: {SW_results}")
        f.close()

    with open(param_dir + "\\trace_mW.txt", mode="w") as f:
        np.savetxt(f, trace_mW)
        f.close()
    
    with open(param_dir + "\\trace_dBm.txt", mode="w") as f:
        np.savetxt(f, trace_dBm)
        f.close()

    time.sleep(1)
    
    """    
    It can substract 2 signals (maybe can be used in the future when we have the shutter)
    Maybe still need to change CALC:NFLO
    """

    ITLA(sercon, 0x32, 0x00, 1) # turns the laser off # Included in the loop because I'm not sure I can change the frequency while the laser is on
    time.sleep(5)

sercon.close()