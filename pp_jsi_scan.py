### Created on: 10-2023
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
import socket

from datetime import datetime

import OSA20
from itla import ITLAConnect, ITLA
import motors_control

BUFFER_SIZE = 1024

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\JSI_" + str(filestamp)
DATADIR = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data\\JSI"+TYPE

# Creates a list of frequencies, f_list, we want to sweep depending on the range of wavelength [start,stop] [m] and increments of inc [m].
c=299792458
start=1545*1e-9
stop=1554*1e-9
inc=20*1e-12
no_points=(stop-start)/inc
w_list=np.arange(start,stop,inc)
f_list=c/w_list # In Hz

#######################
# OSA setting params
## Number of scan is 11
# :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop)
# ":INIT:SMOD 0;:INIT:TMOD 0\r\n"
set_single = ":INIT:SMOD 1;:INIT:TMOD 0\r\n"
# :TRAC1:TYPE 2 -> continuous average
trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 2\r\n"
# :SENS:SENS 6 -> max sensitivity
sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1545nm;:SENS:WAV:STOP 1554nm;:SENS:BAND NAT;:SENS:TIME:INT:ENAB 0\r\n"

try:
    # OSA starts init
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    osa = OSA20.OSA(s, set_single, trace_params, sens_params)
    osa.zero_auto()
    PARAMS = PEAKS = True

    ###############################################################################
    # Connect to Pure photonics
    sercon = ITLAConnect("COM5", baudrate=9600)
    print("sercon: ", sercon)
    ITLA(sercon, 0x31, 1800, 1) # sets the output power (Reange is [600,1800] [dBm]/100)

    for iter, freq in enumerate(f_list):
        ITLA(sercon, 0x35, int(freq * 1e-12), 1) # Setting the frequency (THz register)
        ITLA(sercon, 0x36, int((freq * 1e-12 - int(freq * 1e-12)) * 10000), 1) # Setting the frequency (GHz resgister)
        ITLA(sercon, 0x32, 0x08, 1) # Laser on

        time.sleep(25)
        print(f"iter, freq, w_list[iter]: {iter}, {freq}, {w_list[iter]}")

        osa.aquire_trace()
        time.sleep(130)
        osa.stop_acquire()
        osa.save_data(DATADIR, "_Mira_on", f"signal_{w_list[iter]}", 0, PARAMS, PEAKS)

        ITLA(sercon, 0x32, 0x00, 1) # turns the laser off # Included in the loop because I'm not sure I can change the frequency while the laser is on

    sercon.close()
    s.close()

except:
    print("Exception raised")
    s.close()
    sercon.close()