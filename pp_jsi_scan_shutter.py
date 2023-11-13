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

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\JSI_HighRes" + str(filestamp)
DATADIR = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data\\JSI"+TYPE

#######################
# OSA setting params
# :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop)
set_single = ":INIT:SMOD 0;:INIT:TMOD 0\r\n"
# :TRAC1:TYPE 2 -> continuous average AND :TRAC1:TYPE 1 -> live
trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 1\r\n"
# :SENS:SENS 6 -> max sensitivity
sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1547nm;:SENS:WAV:STOP 1553nm;:SENS:BAND NAT;:SENS:TIME:INT:ENAB 0\r\n"

try:
    # OSA starts init
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ################################################################################
    # Shutter init and open
    shutter = motors_control.Shutter()

    osa = OSA20.OSA(s, set_single, trace_params, sens_params)
    osa.zero_auto()
    PARAMS = PEAKS = True
    NUM_SCANS = 32

    ###############################################################################
    # Connect to Pure photonics
    sercon = ITLAConnect("COM5", baudrate=9600)
    print("sercon: ", sercon)

    # Creates a list of frequencies, f_list, we want to sweep depending on the range of wavelength [start,stop] [m] and increments of inc [m].
    c=299792458
    start=1547*1e-9
    stop=1553*1e-9
    inc=20*1e-12
    no_points=(stop-start)/inc
    w_list=np.linspace(start,start+round(no_points)*inc,round(no_points)+1)
    f_list=c/w_list # In Hz

    for iter, freq in enumerate(f_list):
        wv=w_list[iter]*1e9
        print(f"Wavelength: {wv}nm")
        ITLA(sercon, 0x31, 1800, 1) # sets the output power (Reange is [600,1800] [dBm]/100)
        ITLA(sercon, 0x35, int(freq * 1e-12), 1) # Setting the frequency (THz register)
        ITLA(sercon, 0x36, int((freq * 1e-12 - int(freq * 1e-12)) * 10000), 1) # Setting the frequency (GHz resgister)

        ITLA(sercon, 0x32, 0x08, 1) # Laser on
        print("Laser ON. Wait 25 sec.")
        sleep(25)

        diff_start=abs(wv-1547)
        diff_stop=abs(wv-1553)

        if diff_start<0.5:
            start=1547
        else:
            start=float(wv-0.5)
        
        if diff_stop<0.5:
            stop=1553
        else:
            stop=float(wv+0.5)

        for j in range(NUM_SCANS):
            sens_params = f":SENS:SENS 6;:SENS:WAV:STAR {start}nm;:SENS:WAV:STOP {stop}nm;:SENS:BAND NAT;:SENS:TIME:INT:ENAB 0\r\n"
            osa.update_sens(sens_params)
            shutter.close()
            osa.aquire_trace()
            osa.save_data(DATADIR, "_Mira_off", f"signal_{w_list[iter]}nm", j, PARAMS, PEAKS)

            sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1547nm;:SENS:WAV:STOP 1553nm;:SENS:BAND NAT;:SENS:TIME:INT:ENAB 0\r\n"
            osa.update_sens(sens_params)
            shutter.open()
            osa.aquire_trace()
            osa.save_data(DATADIR, "_Mira_on", f"signal_{w_list[iter]}nm", j, PARAMS, PEAKS)
            PARAMS = PEAKS = False

        ITLA(sercon, 0x32, 0x08, 0) # Laser off
        sleep(3)

    s.close()
    shutter.off()
    sercon.close()

except:
    s.close()
    shutter.off()
    sercon.close()
    
    
















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
import time

from datetime import datetime

import OSA20
from itla import ITLAConnect, ITLA
import motors_control

###############################################################################
# Setting the directory
filestamp=datetime.now().strftime('%Y%m%d%H%M%S')
TYPE = "\JSI_scan_" + str(filestamp)
DATADIR = r"C:\\Users\\Experience\Desktop\\Multipartite Entanglement Experiment\\Data\\OSA"+TYPE

###############################################################################
# Connect to Pure photonics
with ITLAConnect("COM5", baudrate=9600) as sercon:
    print("sercon: ", sercon)

    ITLA(sercon, 0x31, 1800, 1) # sets the output power (Reange is [600,1800] [dBm]/100)

    ################################################################################
    # Shutter init and open
    shutter = motors_control.Shutter()

    # # Creates a list of frequencies, f_list, we want to sweep depending on the range of wavelength [start,stop] [m] and increments of inc [m].
    c=299792458
    start=1552.85*1e-9
    stop=1554*1e-9
    inc=50*1e-12
    no_points=(stop-start)/inc
    w_list=np.linspace(start,start+round(no_points)*inc,round(no_points)+1) #in m
    f_list=c/w_list # In Hz

    #######################
    # OSA setting params

    # :INIT:TMOD 0  -> scan mode manual and :INIT:SMOD 1 -> continuous scan mode (until we stop) ;; :INIT:SMOD 0 -> single scan
    set_single = ":INIT:SMOD 0;:INIT:TMOD 0\r\n"
    # :TRAC1:TYPE 2 -> continuous average ;; :TRAC1:TYPE 1 -> live
    trace_params = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 1\r\n"
    # :SENS:SENS 6 -> max sensitivity
    # sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1535nm;:SENS:WAV:STOP 1541nm;:SENS:BAND:NAT 1;:SENS:TIME:INT:ENAB 0\r\n"
    sens_params = ":SENS:SENS 6;:SENS:WAV:STAR 1548nm;:SENS:WAV:STOP 1554nm;:SENS:BAND 50pm;:SENS:TIME:INT:ENAB 0\r\n"

    ###############################################################################
    # Starting the measurement
    for iter, freq in enumerate(f_list):
        ITLA(sercon, 0x35, int(freq * 1e-12), 1) # Setting the frequency (THz register)
        ITLA(sercon, 0x36, int((freq * 1e-12 - int(freq * 1e-12)) * 10000), 1) # Setting the frequency (GHz resgister)
        ITLA(sercon, 0x32, 0x08, 1) # Laser on

        time.sleep(25)
        print(f"iter, freq, w_list[iter]: {iter}, {freq}, {w_list[iter]}")

        #######################
        # OSA starts DATA aquisition

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            shutter.open()
            osa = OSA20.OSA(s, set_single, trace_params, sens_params)
            osa.zero_auto()
            PARAMS = PEAKS = True
            NUM_SCANS = 10

            for j in range(NUM_SCANS):
                ### Here we can start a cycle
                shutter.open()
                osa.aquire_trace()
                osa.save_data(DATADIR, "_Mira_on", f"signal_{w_list[iter]}nm", j, PARAMS, PEAKS)

                #######################
                # OSA starts BACKGROUND aquisition
                shutter.close()
                osa.aquire_trace()
                osa.save_data(DATADIR, "_Mira_off", f"signal_{w_list[iter]}nm", j, PARAMS, PEAKS)
                PARAMS = False
            
            """    
            It can substract 2 signals (maybe can be used in the future when we have the shutter)
            Maybe still need to change CALC:NFLO
            """

        ITLA(sercon, 0x32, 0x00, 1) # turns the laser off # Included in the loop because I'm not sure I can change the frequency while the laser is on
        time.sleep(5)

    sercon.close()