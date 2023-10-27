# -*- coding: utf-8 -*-
"""
Script should control the pure photonics and the OSA20
We choose the range that we want to sweep our seed's ("signal") wavelength
and record the spectrum of the "idler" recorded by the OSA over a fixed number of avareged scans
We save the data in diff files
"""

import numpy as np
import socket
from time import sleep

from datetime import datetime

import OSA20
import motors_control
from itla import ITLAConnect, ITLA
# from lasers import PPCLLaser

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\Stability_Test_" + str(filestamp)
DATADIR = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data\\OSA"+TYPE

#######################
# OSA setting params
# :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop)
set_single = ":INIT:SMOD 0;:INIT:TMOD 0\r\n"
# :TRAC1:TYPE 2 -> continuous average
trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 1\r\n"
# :SENS:SENS 6 -> max sensitivity
# sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1535nm;:SENS:WAV:STOP 1541nm;:SENS:BAND:NAT 1;:SENS:TIME:INT:ENAB 0\r\n"
sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1548nm;:SENS:WAV:STOP 1553nm;:SENS:BAND NAT;:SENS:TIME:INT:ENAB 0\r\n"

try:
# OSA starts init
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ################################################################################
    # Shutter init and open
    shutter = motors_control.Shutter()
    shutter.close()

    osa = OSA20.OSA(s, set_single, trace_params, sens_params)
    osa.zero_auto()
    PARAMS = PEAKS = True
    NUM_SCANS = 1000

    ###############################################################################
    # Connect to Pure photonics

    sercon = ITLAConnect("COM5", baudrate=9600)
    print("sercon: ", sercon)

    c=299792458
    freq=c/1550e-9

    ITLA(sercon, 0x31, 1800, 1) # sets the output power (Reange is [600,1800] [dBm]/100)
    ITLA(sercon, 0x35, int(freq * 1e-12), 1) # Setting the frequency (THz register)
    ITLA(sercon, 0x36, int((freq * 1e-12 - int(freq * 1e-12)) * 10000), 1) # Setting the frequency (GHz resgister)
    ITLA(sercon, 0x32, 0x08, 1) # Laser on
    sleep(25)

    # pp = PPCLLaser("COM5")
    # pp.open()
    # pp.enable()

    for j in range(NUM_SCANS):
        osa.aquire_trace()
        osa.save_data(DATADIR, "_Mira_off", f"signal_1550_{j}nm", j, PARAMS, PEAKS)

    # pp.close()
    sercon.close()
    s.close()
    shutter.off()

except:
    # pp.close()
    s.close()
    shutter.off()
    sercon.close()
    
    