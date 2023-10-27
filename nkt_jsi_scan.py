### Created on: 10-2023
# -*- coding: utf-8 -*-
"""
Script should control the pure photonics and the OSA20
We choose the range that we want to sweep our seed's ("signal") wavelength
and record the spectrum of the "idler" recorded by the OSA over a fixed number of avareged scans
We save the data in diff files
"""
import socket
import numpy as np
import os
import time

from datetime import datetime

import OSA20
from lasers import NKT
import motors_control

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\Stability_Test_" + str(filestamp)
DATADIR = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data\\OSA"+TYPE

###############################################################################
# Connect to Pure photonics
# with NKT("COM6") as nkt:
nkt = NKT("COM6")
# Setting maximum power (30 mW)
nkt.set_power(3000)
nkt.on()
print("Waiting for 3 mins for NKT laser to stabilize")
time.sleep(3)

################################################################################
# Shutter init and open
shutter = motors_control.Shutter()

# NKT wavelength setpoint in 1/10 pm
# lambda_setpoint = nkt.get_wavelength_setpoint()

# In 1/10 pm
start=15480000
stop=15530000
inc=200
no_points=(stop-start)/inc


w_list=np.linspace(start,start+round(no_points)*inc,round(no_points)+1)
w_offset_list = w_list - 15501200

#######################
# OSA setting params

# :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop) ;; :INIT:SMOD 0 -> single scan
set_single = ":INIT:SMOD 0;:INIT:TMOD 1\r\n"
# :TRAC1:TYPE 2 -> continuous average ;; :TRAC1:TYPE 1 -> live
trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 2\r\n"
# :SENS:SENS 6 -> max sensitivity
# sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1535nm;:SENS:WAV:STOP 1541nm;:SENS:BAND:NAT 1;:SENS:TIME:INT:ENAB 0\r\n"
sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1548nm;:SENS:WAV:STOP 1553nm;:SENS:BAND NAT;:SENS:TIME:INT:ENAB 0\r\n"

###############################################################################
# Starting the measurement
for iter, w_offset in enumerate(w_offset_list):
    nkt.set_wavelength_offset(int(w_offset))
    time.sleep(5)

    print(f"iter, wavelength_offset: {iter}, {w_offset}")
    
    offset=0
    while w_offset!=offset:
        offset=get_wavelength_offset()

    wv = nkt.get_wavelength()
    print("Wavelength stable: ", wv)

#######################
# OSA starts DATA aquisition

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        osa = OSA20.OSA(s, set_single, trace_params, sens_params)
        osa.zero_auto()
        PARAMS = PEAKS = True

        for i in range(5000):
            shutter.open()
            osa.aquire_trace()
            time.sleep(90)
            osa.stop_acquire()

            osa.save_data(DATADIR, "_Mira_on", f"signal_{i}nm", PARAMS, PEAKS)

            #######################
            # OSA starts BACKGROUND aquisition
            shutter.close()
            osa.aquire_trace()
            time.sleep(90)
            osa.stop_acquire()

            osa.save_data(DATADIR, "_Mira_off", f"signal_{i}nm", PARAMS, PEAKS)

nkt.off()
nkt.close()