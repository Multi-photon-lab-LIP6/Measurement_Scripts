import time
import numpy as np
import random
import TT
from basis import MEAS_WP_ANGLES
import scipy.optimize as sp
import motors_control


def Unitary(angle,angles):

    a = angle[0]
    b = angle[1]
    y = angle[2]
    
    f = (1/2)*(-np.cos(2*(a-b))-np.cos(2*(b-y))) - np.real(np.exp(-1j*angles/2))
    g = (1/2)*(np.sin(2*(a - b)) + np.sin(2*(b - y)))
    h = (1/2)*(-np.sin(2*(a - b)) - np.sin(2*(b - y)))
    v = (1/2)*(-np.cos(2*(a-b))- np.cos(2*(b - y))) - np.real(np.exp(1j*angles/2))

    K = (1/2)*(-np.cos(2*b) + np.cos(2*(a - b + y))) - np.imag(np.exp(-1j*angles/2))
    m = (1/2)*(-np.sin(2*b) + np.sin(2*(a - b + y)))
    z = (1/2)*(-np.sin(2*b) + np.sin(2*(a - b + y)))
    e = (1/2)*(np.cos(2*b) - np.cos(2*(a - b + y))) - np.imag(np.exp(1j*angles/2))

    return  (f,g,h,v,K,m,z,e)

def solving(angle,angles):
    result = sp.least_squares(Unitary,angle,method='trf',args=[angles],max_nfev=1000000000)
    QWP1 = result.x[0]
    HWP1 = result.x[1]
    QWP2 = result.x[2]
    return(QWP1/180*np.pi,HWP1/180*np.pi,QWP2/180*np.pi)

def main():


    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
        TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.12]
        DELAY = [0, -846, -30200, -36547, -35543, -36776, -800, 1400]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "QST", "QST_GHZ")

        AQUISITION_TIME = int(0.3*60E12) # in picosecond
        N_REP = 1
        """
        Defining the coincidence channels we want to save
        If you change the order, make sure it matches with the analysis code
        """
        GROUPS = [(1,3,5,7),(1,3,5,8),(1,3,6,7),(1,3,6,8),
                  (1,4,5,7),(1,4,5,8),(1,4,6,7),(1,4,6,8),
                  (2,3,5,7),(2,3,5,8),(2,3,6,7),(2,3,6,8),
                  (2,4,5,7),(2,4,5,8),(2,4,6,7),(2,4,6,8)] 
        COINCIDENCE_WINDOW = 500 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["arya", "bran", "cersei", "dany"]

        # Create new device, Connect, begin polling, and enable
        arya, bran, cersei, dany = motors_control.players_init(players,5)
        elem_base = ['x']
        
        arya.set_meas_basis(elem_base[0])
        bran.set_meas_basis(elem_base[0])
        cersei.set_meas_basis(elem_base[0])
        dany.set_meas_basis(elem_base[0])



        ##################################################################
        #####################     PHASE ENCODING   #######################
        ##################################################################
        
        players_random_angle = []
        player_QHQ = []

        # Random angle, solving the unitary for the WP
        for i in range(len(players)):
            players_random_angle.append(round(random.uniform(0,2*np.pi),5))
            player_QHQ.append(solving([np.pi/4,np.pi/2,np.pi/3],players_random_angle[i]))
        
        # Setting the WP
        arya.set_meas_angles_phase_estimation(player_QHQ[0])
        bran.set_meas_angles_phase_estimation(player_QHQ[1])
        cersei.set_meas_angles_phase_estimation(player_QHQ[2])
        dany.set_meas_angles_phase_estimation(player_QHQ[3])

        players_random_angle = list(map(str,players_random_angle))

        label=''.join([idx for tup in players_random_angle for idx in tup])
        tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\ABCD={label}.txt", save_raw=True, save_params=True)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()