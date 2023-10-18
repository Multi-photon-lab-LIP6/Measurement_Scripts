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

from datetime import datetime

import OSA20_Ethernet as osa
import motors_control

BUFFER_SIZE = 1024

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\OSA_Test_" + str(filestamp)
DATADIR = os.getcwd()+"\Data"+TYPE

################################################################################
# Shutter init and open
shutter = motors_control.Shutter()

#######################
# OSA setting params
NUM_SCANS = 7

# :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop)
set_single = ":INIT:SMOD 1;:INIT:TMOD 0\r\n"
# :TRAC1:TYPE 2 -> continuous average
trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 2\r\n"
# :SENS:SENS 6 -> max sensitivity
# sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1535nm;:SENS:WAV:STOP 1541nm;:SENS:BAND:NAT 1;:SENS:TIME:INT:ENAB 0\r\n"
sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1536nm;:SENS:WAV:STOP 1541nm;:SENS:BAND 50pm;:SENS:TIME:INT:ENAB 0\r\n"

for i in range(8):
#######################
    # OSA starts DATA aquisition
    shutter.close()
    trace_mW, trace_dBm, L_start, sampling, Length, PT_list, SW_results = osa.scan(NUM_SCANS, set_single, trace_params, sens_params)

    # #######################
    # # Saving data
    param_dir = DATADIR + "_Trace_Mira_on\\" + f"signal_{1540}nm_iter_{i}"
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


        # #######################
        # # OSA starts BACKGROUND aquisition
        # shutter.close()
        # trace_mW, trace_dBm, L_start, sampling, Length, PT_list, SW_results = osa.scan(NUM_SCANS, set_single, trace_params, sens_params)

        # # #######################
        # # # Saving data
        # param_dir = DATADIR + "_Mira_off\\" + f"signal_{w_list[iter]}nm" 
        # os.makedirs(param_dir, exist_ok=True)
        # with open(param_dir + "\params.txt", mode="w") as f:
        #     f.write(f"L_start       sampling      Length    \n")
        #     f.write(f"{L_start}         {sampling}          {Length}\n")
        #     f.write(f"PT_list: {PT_list} \n")
        #     f.write(f"SW_results: {SW_results}")
        #     f.close()

        # with open(param_dir + "\\trace_mW.txt", mode="w") as f:
        #     np.savetxt(f, trace_mW)
        #     f.close()

        # with open(param_dir + "\\trace_dBm.txt", mode="w") as f:
        #     np.savetxt(f, trace_dBm)
        #     f.close()
shutter.off()