""""
This script runs private quantum phase estimation
"""
import numpy as np
import time
import scipy.optimize as sp
# import itertools
import random
from tqdm import tqdm
from datetime import timedelta

import motors_control
import TT
from basis import MEAS_WP_ANGLES

def unitary(angle, u_compensation, angle_rz):

    a = angle[0]
    b = angle[1]
    y = angle[2]

    rz = [[np.exp(-1j*angle_rz/2),0],
          [0,np.exp(1j*angle_rz/2)]]

    u = rz@u_compensation
    
    f = (1/2)*(-np.cos(2*(a - b))-np.cos(2*(b-y))) - np.real(u[0][0])
    g = (1/2)*(np.sin(2*(a - b)) + np.sin(2*(b - y))) - np.real(u[0][1])
    h = (1/2)*(-np.sin(2*(a - b)) - np.sin(2*(b - y))) - np.real(u[1][0])
    v = (1/2)*(-np.cos(2*(a - b))- np.cos(2*(b - y))) - np.real(u[1][1])

    k = (1/2)*(-np.cos(2*b) + np.cos(2*(a - b + y))) - np.imag(u[0][0])
    m = (1/2)*(-np.sin(2*b) + np.sin(2*(a - b + y))) - np.imag(u[0][1])
    z = (1/2)*(-np.sin(2*b) + np.sin(2*(a - b + y))) - np.imag(u[1][0])
    e = (1/2)*(np.cos(2*b) - np.cos(2*(a - b + y))) - np.imag(u[1][1])

    return  (f, g, h, v, k, m, z, e)

def solving(angle, u, angle_rz):
    result = sp.least_squares(unitary, angle, method='trf', args=[u, angle_rz], max_nfev=1000000000)
    QWP1 = result.x[0]
    HWP1 = result.x[1]
    QWP2 = result.x[2]
    return(QWP2*180/np.pi, HWP1*180/np.pi, QWP1*180/np.pi)

def main():

    players = ["arya", "bran", "cersei", "dany"]
    sample=["SQWP1","SHWP","SQWP2"]

    # Create new device, Connect, begin polling, and enable
    # arya, bran, cersei, dany = motors_control.players_init(players, sample)

    CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    TRIGGER = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.12]
    DELAY = [0, -860, -30350, -36500, -35980, -35470, -1000, -210]
    AQUISITION_TIME = int(0.25*60E12) # in picosecond
    N_REP = 1
    BUFFER_SIZE = 10000
    COINCIDENCE_WINDOW = 200 # in picosecond
    N_REP = 1

    tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "Private_Quantum_Sensing", "QPE_RealRun")


    GROUPS = [(1,3,5,7),(1,3,5,8),(1,3,6,7),(1,3,6,8),
            (1,4,5,7),(1,4,5,8),(1,4,6,7),(1,4,6,8),
            (2,3,5,7),(2,3,5,8),(2,3,6,7),(2,3,6,8),
            (2,4,5,7),(2,4,5,8),(2,4,6,7),(2,4,6,8),

            (1,3,5,7,2),(1,3,5,7,4),(1,3,5,7,6),(1,3,5,7,8),
            (1,3,5,8,2),(1,3,5,8,4),(1,3,5,8,6),(1,3,5,8,7),
            (1,3,6,7,2),(1,3,6,7,8),(1,3,6,7,4),(1,3,6,7,5),
            (1,3,6,8,4),(1,3,6,8,2),(1,3,6,8,5),(1,3,6,8,7),
            (1,4,5,7,2),(1,4,5,7,6),(1,4,5,7,8),(1,4,5,7,3),
            (1,4,5,8,2),(1,4,5,8,6),(1,4,5,8,3),(1,4,5,8,7),
            (1,4,6,7,2),(1,4,6,7,8),(1,4,6,7,5),(1,4,6,7,3),
            (1,4,6,8,2),(1,4,6,8,3),(1,4,6,8,5),(1,4,6,8,7),
            (2,3,5,7,4),(2,3,5,7,6),(2,3,5,7,8),(2,3,5,7,1),
            (2,3,5,8,4),(2,3,5,8,6),(2,3,5,8,7),(2,3,5,8,1),
            (2,3,6,7,4),(2,3,6,7,8),(2,3,6,7,1),(2,3,6,7,5),
            (2,3,6,8,1),(2,3,6,8,4),(2,3,6,8,5),(2,3,6,8,7),
            (2,4,5,7,1),(2,4,5,7,3),(2,4,5,7,6),(2,4,5,7,8),
            (2,4,5,8,6),(2,4,5,8,1),(2,4,5,8,7),(2,4,5,8,3),
            (2,4,6,7,8),(2,4,6,7,3),(2,4,6,7,5),(2,4,6,7,1),
            (2,4,6,8,1),(2,4,6,8,3),(2,4,6,8,5),(2,4,6,8,7)]         
            
    ### DEFINING ANGLES AND CORRESPONDING LOCAL UNITARIES THAT NEED TO BE APPLIED TO GET A TRUE GHZ ###
    print("Setting samples's unitary compensation")
    u_compensation = [[46.282297250730494, 116.71935075047799, 41.42340727433868],
                      [24.481702600831554, 5.535044154126424, 60.30601589399454],
                      [-39.69547157882599, 59.987239383378245, 127.41263673906985],
                      [-123.77555284080137, -19.375698630319153, 44.19271469899905]]
    
    # arya.set_sample_angles(u_compensation[0])
    # bran.set_sample_angles(u_compensation[1])
    # cersei.set_sample_angles(u_compensation[2])
    # dany.set_sample_angles(u_compensation[3])

    u_arya = np.array([[ 0.8234528 +0.56259885j , 0.06999967-0.0225402j ],
    [-0.06999967-0.0225402j ,  0.8234528 -0.56259885j]])

    u_bran = np.array([[-0.22732945-0.95592241j  ,0.16410186+0.08720236j],
    [-0.16410186+0.08720236j, -0.22732945+0.95592241j]])

    u_cersei = np.array([[ 0.82434297+0.53329889j , 0.18867697-0.02125947j],
    [-0.18867697-0.02125947j , 0.82434297-0.53329889j]])

    u_dany = np.array([[ 0.74001482-0.64305896j , 0.15772342-0.11822252j],
    [-0.15772342-0.11822252j , 0.74001482+0.64305896j]])

    u_comp_list = [u_arya, u_bran, u_cersei, u_dany]
    
    ####### THE STABILIZERS FOR THE VERIFICATION TASK #######
    stabilizers = [
        "iiii",
        "zzii",
        "izzi",
        "iizz",
        "xxxx",
        "zizi",
        "iziz",
        "zzzz",
        "xyyx",
        "yxyx",
        "xxyy",
        "yyxx",
        "ziiz",
        "xyxy",
        "yxxy",
        "yyyy"
    ]

    ##################### RANDOMNESS ######################
    random_number_list = []
    with open(r"C:\Users\Experience\Desktop\QRNG\random_sample.txt", mode ='r') as file:
        for line in file:
            random_number_list.append(int(line.split()[0]))
    file.close()

    random.shuffle(random_number_list)
    list_stabilizers = []
    for i in random_number_list:
        list_stabilizers.append(stabilizers[i])
    
    random_sample_number_list = []
    with open(r"C:\Users\Experience\Desktop\QRNG\random_round.txt", mode ='r') as file:
        for line in file:
            random_sample_number_list.append(int(line.split()[0]))
    file.close()

    random_number = random.choice(random_sample_number_list)

    ###### DEFINING EACH PLAYER'S PHASE #######
    players_phases = [0, np.pi/8, np.pi/4]
    theta_4 = np.pi/2-np.sum(players_phases)
    players_phases.append(theta_4)

    for v in tqdm(range(30)):
        print(f'Round {v}')

        start_time = time.monotonic()

        for i in range(10**4):
            print("Iteration ", i)

            if i%2 == 0:
                # Run iteration here
                while True:
                    with open(r"C:\Users\Experience\Desktop\Multipartite Entanglement Experiment\Data\Private_Quantum_Sensing\instruction.txt", mode = "r") as f:
                        if "STOP" not in f.read():
                            break
                        print("Program stopped")
                        time.sleep(5)
            print("Starting iteration")
            operator = list_stabilizers[i]
            # arya.set_meas_basis(str(operator[0]))
            # bran.set_meas_basis(str(operator[1]))
            # cersei.set_meas_basis(str(operator[2]))
            # dany.set_meas_basis(str(operator[3]))
            # tt.real_time_measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, BUFFER_SIZE, data_filename=f"\ABCD={operator}_{i}_{v}.txt", save_raw=True, save_params=True)
            

            if i == random_number :
                print('Phase Estimation')
                # arya.set_meas_basis('x')
                # bran.set_meas_basis('x')
                # cersei.set_meas_basis('x')
                # dany.set_meas_basis('x')

                player_QHQ = []
                # Random angle, solving the unitary for the WP
                for i in range(len(players)):
                    player_QHQ.append(solving([0,0,0], u_comp_list[i], players_phases[i]))
                
                # Setting the sample encoding and measure
                # arya.set_sample_angles(player_QHQ[0])
                # bran.set_sample_angles(player_QHQ[1])
                # cersei.set_sample_angles(player_QHQ[2])
                # dany.set_sample_angles(player_QHQ[3])
                tt.real_time_measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, BUFFER_SIZE, data_filename=f"\PhaseEstimation=xxxx_{theta_4}_{v}.txt", save_raw=True, save_params=True)
                
                # Setting back the samples' angles just to compensate for the unitary
                # arya.set_sample_angles(u_compensation[0])
                # bran.set_sample_angles(u_compensation[1])
                # cersei.set_sample_angles(u_compensation[2])
                # dany.set_sample_angles(u_compensation[3])

        end_time = time.monotonic()
        print(timedelta(seconds=end_time - start_time))

    with open(r'C:\Users\Experience\Desktop\Multipartite Entanglement Experiment\Data\Private_Quantum_Sensing\QPE_RealRun\QPE_angle_round_.txt','w') as f:    
        for i in players_phases:
            f.write(f'{players_phases[i]}\n')
    
   # Leave the WP's in the Z basis
    print("Setting measurements' basis to 0")
    # arya.set_meas_basis("z")
    # bran.set_meas_basis("z")
    # cersei.set_meas_basis("z")
    # dany.set_meas_basis("z")

    tt.free_swabian()
    # # Stop polling and close devices
    # arya.off()
    # bran.off()
    # cersei.off()
    # dany.off()

    # arya.off_sample()
    # bran.off_sample()
    # cersei.off_sample()

if __name__ == "__main__":
    main()


