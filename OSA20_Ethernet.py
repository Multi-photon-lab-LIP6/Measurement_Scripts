# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 11:17:54 2020
Sample Python program tested successfully with Python 3.7
Initial release, version 1.0
"""

import socket
import time
import numpy as np
import matplotlib.pyplot as plt

BUFFER_SIZE = 1024
    
###############################################################################
# OSA20 settings

TCP_IP = '169.254.150.80'
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

def plot_trace(s, trace, L_start, sampling, Length):
    # Plot the trace
    
    L_stop = L_start + sampling * (Length - 1) / 1000
    Wav = np.linspace(L_start, L_stop, Length)
    
    fig_raw = plt.figure()
    ax = fig_raw.add_subplot(111)
    ax.ticklabel_format(useOffset=False)
    
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Power (dBm)")
    
    ax.plot(Wav,trace)
    
    plt.title("OSA20 trace")
    fig_raw.show()  
    
###############################################################################
# Code
def scan(NUM_SCANS, set_single, trace_params, sens_params):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((TCP_IP, TCP_PORT))
        
        # Clear Error buffer
        Clear_error_buffer = "*CLS\r\n".encode()
        s.send(Clear_error_buffer)
        
        # Query_IDN
        Query_IDN = "*IDN?\r\n".encode()
        s.send(Query_IDN)
        IDN = s.recv(BUFFER_SIZE).decode()
        print(IDN)
            
        # Set units
        Set_units = ":UNIT:X WAV;:UNIT:Y DBM\r\n".encode()
        s.send(Set_units)
        
        # OSA Mode
        Set_Mode = ":OSA 1\r\n".encode()
        s.send(Set_Mode)
        # Wait_until_idle(s)
        
        # Analysis Setup
        Set_Analysis = ":CALC:AUTO 0;:CALC:SOUR 1;:CALC:NFLO -65DBM;:CALC:MARKERS:ARAN 0\r\n".encode()
        s.send(Set_Analysis)
        
        # Single, Manual
        # Set_Single_Manual = ":INIT:SMOD 0;:INIT:TMOD 0\r\n".encode()
        Set_Single_Manual = set_single.encode()
        s.send(Set_Single_Manual)
        
        # Trace setup
        # Set_Traces = ":TRAC1:STAT 1;:TRAC1:ACT;:TRAC1:TYPE 1\r\n".encode()
        Set_Traces = trace_params.encode()
        s.send(Set_Traces)
        
        # Scan setup
        # Set_scan = ":SENS:SENS 3;:SENS:WAV:STAR 1500nm;:SENS:WAV:STOP 1600nm;:SENS:BAND:NAT 1;:SENS:TIME:INT:ENAB 0\r\n".encode()
        Set_scan = sens_params.encode()
        s.send(Set_scan)
        
        # Setup Peak Trough Search Parameters
        Set_PT_search = ":CALC:PAR:PTS:DISP:STAT 1;:CALC:PAR:PTS:DISP:SHOW 1;:CALC:PAR:PTS:PTTH 3DB;:CALC:PAR:PTS:ANTH 1\r\n".encode()
        s.send(Set_PT_search)
        
        # Setup Spectral Width Parameters
        Set_SW_parameters = ":CALC:PAR:SWID:ACT 1;:CALC:PAR:SWID:DISP 1;:CALC:PAR:SWID:ALG 0;:CALC:PAR:SWID:WTHR 3DB;:CALC:PAR:SWID:MULT 1;:CALC:PAR:SWID:FMOD 0;:CALC:PAR:SWID:MAN 0\r\n".encode()
        s.send(Set_SW_parameters)

        # # Zeroing auto
        # Perform_zeroing_auto = ":SENS:ZERO:AUTO 1\r\n".encode()
        # s.send(Perform_zeroing_auto)
        
        # Zeroing
        Perform_zeroing = ":SENS:ZERO\r\n".encode()
        s.send(Perform_zeroing)
        Wait_until_idle(s)
        
        # Acquire trace
        Acquire_trace = ":INIT\r\n".encode()
        s.send(Acquire_trace)

        time.sleep(175)

        # Wait_until_scan(s, NUM_SCANS)
        Stop_trace = ":STOP\r\n".encode()
        s.send(Stop_trace)
        # Wait_until_idle(s)
        Wait_until_idle(s)
        
        # Get Trace Start Wavelength
        Query_start_wav = ":TRAC1:DATA:START?\r\n".encode()
        s.send(Query_start_wav)
        L_start = float(s.recv(BUFFER_SIZE).decode())*1E9 # L_start in nm
            
        # Get Trace Length
        Query_trace_length = ":TRAC1:DATA:LENGTH?\r\n".encode()
        s.send(Query_trace_length)
        Length = int(s.recv(BUFFER_SIZE).decode())
        
        # Get Trace Sampling
        Query_sampling = ":TRAC1:DATA:SAMP?\r\n".encode()
        s.send(Query_sampling)
        sampling = float(s.recv(BUFFER_SIZE).decode())*1E12 # sampling in pm
        
        # Get Trace Data (BIN,mW)
        Query_data = ":TRAC1:DATA? 1,0\r\n".encode()
        s.send(Query_data)
        trace_mW = Retrieve_Binary_trace(s)

        # Get Trace Data (BIN,dBm)
        Query_data = ":TRAC1:DATA? 1,1\r\n".encode()
        s.send(Query_data)
        trace_dBm = Retrieve_Binary_trace(s)

        # Analyze
        Analyze = ":CALC\r\n".encode()
        s.send(Analyze)
        Wait_until_idle(s)
        
        # Get Peaks & Troughs List
        Query_PT_list = ":CALC:DATA:PTS?\r\n".encode()
        s.send(Query_PT_list)
        PT_list = s.recv(BUFFER_SIZE).decode()
        print("Peaks Troughs list: {}".format(PT_list))
        
        # Get Spectral Width results
        Query_SW_results = ":CALC:DATA:SWID?\r\n".encode()
        s.send(Query_SW_results)
        SW_results = s.recv(BUFFER_SIZE).decode()
        print("Spectral Width results: {}".format(SW_results))
        
        # Query Error queue
        Query_Error_queue = ":SYST:ERR?\r\n".encode()
        s.send(Query_Error_queue)
        Error = s.recv(BUFFER_SIZE).decode()
        print(Error)

    return trace_mW, trace_dBm, L_start, sampling, Length, PT_list, SW_results