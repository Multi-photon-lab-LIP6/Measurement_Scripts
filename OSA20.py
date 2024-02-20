# -*- coding: utf-8 -*-
"""
Initial code provided by EXFO

Created on Fri Jul 24 11:17:54 2020
Sample Python program tested successfully with Python 3.7
Initial release, version 1.0
"""

import time
import numpy as np
import matplotlib.pyplot as plt
import os

BUFFER_SIZE = 1024
    
###############################################################################
# OSA20 settings

TCP_IP = '169.254.238.155'
TCP_PORT = 5025

###############################################################################
# Functions

def Wait_until_idle(s):
    Query_condition_register = ":STAT:OPER:COND?\r\n".encode()
    while True:
        s.send(Query_condition_register)
        Condition = int(s.recv(BUFFER_SIZE).decode())
        if Condition == 0:
            break
        else:
            time.sleep(0.1)

def Wait_until_scan(s, max):
    # Counts scans
    Query_scan_count = ":INIT:CURR?\r\n".encode()
    time.sleep(0.5)
    s.send(Query_scan_count)
    scan = int(s.recv(BUFFER_SIZE).decode())

    while True:
        # Stop acquiring trace
        if scan > max:
            Stop_trace = ":STOP\r\n".encode()
            s.send(Stop_trace)
            Wait_until_idle(s)
            break
        else:
            time.sleep(2)
            s.send(Query_scan_count)
            scan = int(s.recv(BUFFER_SIZE).decode())
            print("Scan, max: ", scan, max)

def Retrieve_Binary_trace(s):
    ###############################################################################
    # Retrieve the # character
    BUFFER_SIZE = 1
    Header = s.recv(BUFFER_SIZE)
    Header = Header.decode()
    # print('Header: {}'.format(Header))
    ###############################################################################
    # Retrieve the length character
    BUFFER_SIZE = 1
    L = s.recv(BUFFER_SIZE)
    L = int(L)
    # print('Length: {}'.format(L))
    ###############################################################################
    # Retrieve the length character
    BUFFER_SIZE = L
    Nb_bytes = s.recv(BUFFER_SIZE)
    Nb_bytes = int(Nb_bytes)
    # print('Number of bytes: {}'.format(Nb_bytes))
    ###############################################################################
    # Retrieve data
    MSGLEN = Nb_bytes
    chunks = []
    bytes_recd = 0

    # See the website below for the while loop
    # https://docs.python.org/3/howto/sockets.html 
    while bytes_recd < MSGLEN:
        chunk = s.recv(min(MSGLEN - bytes_recd, 2048))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)

    # print('{} bytes expected, {} bytes received'.format(Nb_bytes,bytes_recd))

    # Trace data
    data_raw = b''.join(chunks) # merges all bytes in the list together
    data = np.frombuffer(data_raw,dtype=np.dtype('>f4')) # https://docs.scipy.org/doc/numpy/reference/generated/numpy.frombuffer.html, Big endian order

    return data
    
###############################################################################
# Code
class OSA():
    def __init__(self, s, set_single, trace_params, sens_params):
        self.s = s
        self.s.settimeout(5)
        self.s.connect((TCP_IP, TCP_PORT))

        self.set_single = set_single
        self.trace_params = trace_params
        self.sens_params = sens_params

        # Clear Error buffer
        Clear_error_buffer = "*CLS\r\n".encode()
        self.s.send(Clear_error_buffer)

        # Query_IDN
        Query_IDN = "*IDN?\r\n".encode()
        self.s.send(Query_IDN)
        IDN = self.s.recv(BUFFER_SIZE).decode()
        print(IDN)
            
        # Set units
        Set_units = ":UNIT:X WAV;:UNIT:Y DBM\r\n".encode()
        self.s.send(Set_units)
        
        # OSA Mode
        Set_Mode = ":OSA 1\r\n".encode()
        self.s.send(Set_Mode)
        # Wait_until_idle(self.s)
        
        # Analysis Setup
        Set_Analysis = ":CALC:AUTO 0;:CALC:SOUR 1;:CALC:NFLO -65DBM;:CALC:MARKERS:ARAN 0\r\n".encode()
        self.s.send(Set_Analysis)
        
        self.set_single_manual()
        self.trace()
        self.sens()

        # Setup Peak Trough Search Parameters
        Set_PT_search = ":CALC:PAR:PTS:DISP:STAT 1;:CALC:PAR:PTS:DISP:SHOW 1;:CALC:PAR:PTS:PTTH 3DB;:CALC:PAR:PTS:ANTH 1\r\n".encode()
        self.s.send(Set_PT_search)
        
        # Setup Spectral Width Parameters
        Set_SW_parameters = ":CALC:PAR:SWID:ACT 1;:CALC:PAR:SWID:DISP 1;:CALC:PAR:SWID:ALG 0;:CALC:PAR:SWID:WTHR 3DB;:CALC:PAR:SWID:MULT 1;:CALC:PAR:SWID:FMOD 0;:CALC:PAR:SWID:MAN 0\r\n".encode()
        self.s.send(Set_SW_parameters)

    def set_single_manual(self):
        # Single, Manual
        Set_Single_Manual = self.set_single.encode()
        self.s.send(Set_Single_Manual)
        
    def trace(self):
        # Trace setup
        # Set_Traces = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 1\r\n".encode()
        Set_Traces = self.trace_params.encode()
        self.s.send(Set_Traces)

    def sens(self):    
        # Scan setup
        Set_scan = self.sens_params.encode()
        self.s.send(Set_scan)

    def update_sens(self, new_sens):
        self.sens_params = new_sens
        self.sens()

    def zero(self):
        # Zeroing
        Perform_zeroing = ":SENS:ZERO\r\n".encode()
        self.s.send(Perform_zeroing)
        Wait_until_idle(self.s)

    def zero_auto(self):
        Perform_zeroing_auto = ":SENS:ZERO:AUTO 1\r\n".encode()
        self.s.send(Perform_zeroing_auto)

    def aquire_trace(self):
        # Acquire trace
        Acquire_trace = ":INIT\r\n".encode()
        self.s.send(Acquire_trace)
        # Wait_until_idle(self.s)

    def stop_acquire(self):
        # Wait_until_scan(self.s, NUM_SCANS)
        Stop_trace = ":STOP\r\n".encode()
        self.s.send(Stop_trace)
        Wait_until_idle(self.s)

    def get_results(self):

        # Get Trace Start Wavelength
        Query_start_wav = ":TRAC1:DATA:START?\r\n".encode()
        self.s.send(Query_start_wav)
        self.L_start = float(self.s.recv(BUFFER_SIZE).decode())*1E9 # L_start in nm
            
        # Get Trace Length
        Query_trace_length = ":TRAC1:DATA:LENGTH?\r\n".encode()
        self.s.send(Query_trace_length)
        self.Length = int(self.s.recv(BUFFER_SIZE).decode())
        
        # Get Trace Sampling
        Query_sampling = ":TRAC1:DATA:SAMP?\r\n".encode()
        self.s.send(Query_sampling)
        self.sampling = float(self.s.recv(BUFFER_SIZE).decode())*1E12 # sampling in pm
        
        # Get Trace Data (BIN,mW)
        Query_data = ":TRAC1:DATA? 1,0\r\n".encode()
        self.s.send(Query_data)
        self.trace_mW = Retrieve_Binary_trace(self.s)

        # Get Trace Data (BIN,dBm)
        Query_data = ":TRAC1:DATA? 1,1\r\n".encode()
        self.s.send(Query_data)
        self.trace_dBm = Retrieve_Binary_trace(self.s)
    
    def analyse(self):
        # Analyze
        Analyze = ":CALC\r\n".encode()
        self.s.send(Analyze)
        Wait_until_idle(self.s)
        
        # Get Peaks & Troughs List
        Query_PT_list = ":CALC:DATA:PTS?\r\n".encode()
        self.s.send(Query_PT_list)
        self.PT_list = self.s.recv(BUFFER_SIZE).decode()
        print("Peaks Troughs list: {}".format(self.PT_list))
        
        # Get Spectral Width results
        Query_SW_results = ":CALC:DATA:SWID?\r\n".encode()
        self.s.send(Query_SW_results)
        self.SW_results = self.s.recv(BUFFER_SIZE).decode()
        print("Spectral Width results: {}".format(self.SW_results))
        
        # Query Error queue
        Query_Error_queue = ":SYST:ERR?\r\n".encode()
        self.s.send(Query_Error_queue)
        Error = self.s.recv(BUFFER_SIZE).decode()
        print(Error)

    def save_data(self, DATADIR, FOLDER, FILE, TXT=0, PARAMS=False, PEAKS=False):
        self.get_results()
        param_dir = f"{DATADIR}_{FOLDER}\\{FILE}"
        os.makedirs(param_dir, exist_ok=True)

        with open(param_dir + f"\\trace_{TXT}_mW.txt", mode="w") as f:
            np.savetxt(f, self.trace_mW)
            f.close()

        with open(param_dir + f"\\trace_{TXT}_dBm.txt", mode="w") as f:
            np.savetxt(f, self.trace_dBm)
            f.close()

        with open(param_dir + "\params.txt", mode="w") as f:
            if PARAMS is True:
                f.write(f"L_start       sampling      Length    \n")
                f.write(f"{self.L_start}         {self.sampling}          {self.Length}\n")
            if PEAKS is True:
                self.analyse()
                f.write(f"PT_list: {self.PT_list} \n")
                f.write(f"SW_results: {self.SW_results}")
            f.close()

        
