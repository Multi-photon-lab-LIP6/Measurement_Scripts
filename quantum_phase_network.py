import numpy as np
import scipy
import time
import math
import itertools
from scipy.stats import norm
from copy import deepcopy
from pathlib import Path
from scipy.linalg import sqrtm
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import glob
import pandas as pd

def Verif():

    working_dir_data = r"C:\Users\Experience\Desktop\Multipartite Entanglement Experiment\Data\PROTOCOL"
    folder = "\\VERIFICATION_20231215143423\counts"
    os.chdir(working_dir_data+folder)
    working_dir_data+=folder+'\\'
    filenames = [i for i in glob.glob("*.txt")]
    filenames.sort(key=os.path.getmtime)
    Number_players = 4
    Distributed_bit = []
    total_counts = 0
    Probabilities_GHZ_PASS_LIST = []  

    ################################################################## 
    #####################     VERIF ANALYSIS   #######################
    ################################################################## 

    for i in range(len(filenames)):
        total_counts = 0
        Distributed_bit = []
        print('Gathering the file and bits of players')
        name=filenames[i].split('_')[1].split('.txt')[0]
        for z in range(Number_players):
            Distributed_bit.append(int(name[z]))
        total_counts = 0
        print('Gathering counts')
        counts = []

        with open(filenames[i]) as file:
            for line in file:
                counts.append(line.split())

        Sum_bit = (1/2*sum(Distributed_bit)%2)

        print('Testing the GHZ state')
    
        for i in range(16):
            total_counts += int(float(counts[0][i]))
    
        if total_counts == 1:
            if Sum_bit == False:
             GHZ_PASS = int(float(counts[0][0])) + int(float(counts[0][15]))+int(float(counts[0][3]))+int(float(counts[0][5]))+int(float(counts[0][6]))+int(float(counts[0][9]))+int(float(counts[0][10]))+int(float(counts[0][12]))
            else: 
             GHZ_PASS = int(float(counts[0][1]))+int(float(counts[0][2]))+int(float(counts[0][4]))+int(float(counts[0][7]))+int(float(counts[0][8]))+int(float(counts[0][11]))+int(float(counts[0][13]))+int(float(counts[0][14]))
        

            print(f"GHZ states {name} passing the test : {GHZ_PASS}")
            Probabilities_GHZ_PASS_LIST.append(GHZ_PASS)
        
        else:
            print(f"Losses : {name} discard")

        Probabilities_GHZ_PASS = sum(Probabilities_GHZ_PASS_LIST)/len(Probabilities_GHZ_PASS_LIST)

        print(Probabilities_GHZ_PASS)

        return(Probabilities_GHZ_PASS)


def main():

    try:

        with open("C:\Users\nicol\Desktop\Thèse\Measurement_Scripts\verification.py") as f:
            exec(f.read())
        
        Probabilities_GHZ_PASS_MEAN = Verif()

        if Probabilities_GHZ_PASS_MEAN > 0.854 :
            print("Quantum phase esimation")
            with open("C:\Users\nicol\Desktop\Thèse\Measurement_Scripts\quantum_phase_estimation.py") as f:
                exec(f.read())
        else: 
            print("Not enough secure GHZ states")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()