""""
This script was for the verification of e-voting?
"""
import time
import itertools
import random
import TT
from basis import MEAS_WP_ANGLES
import motors_control
import numpy as np

def randomBit(number_player):
    playerBit = []
    playerBases = []
    playerlabel = []

    for z in range(number_player-1):

        if random.random() > .5:
            playerBases.append('y')
            playerBit.append(1)
            playerlabel.append("1")
        else:
            playerBases.append('x')
            playerBit.append(0)
            playerlabel.append("0")


    if (sum(playerBit)%2) == 0:
        playerBases.append('x')
        playerBit.append(0)
        playerlabel.append("0")

    else:
        playerBases.append('y')
        playerBit.append(1)
        playerlabel.append("1")

        
    return playerBit,playerBases,playerlabel

def get_iterator(K,n):
    """
    Function to generate the indices used during a for loop of n indices
    starting from 0 to K-1  (n nested for loops of K iterations). 
    Returns a list of K^n tuples of n elements. 
    the r-th tuple contain the number "r" written in base K.
    """
    iterator = []
    for r in range(K**n):
        r_in_base_K = np.base_repr(r, K)
        list_r_in_base_K = [0]*n
        for c in range(len(r_in_base_K)):
            list_r_in_base_K[n - len(r_in_base_K) + c] = np.int(r_in_base_K[c])
        iterator.append(list_r_in_base_K)
    return iterator

def main():

    CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.12]
    DELAY = [0,  2750, -26650, -33020, -32230, -33210, 2720, 4990]
    AQUISITION_TIME = int(1.5*60E12) # in picosecond
    N_REP = 1
    tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "PROTOCOL", f"VERIFICATION__aqtime={AQUISITION_TIME*1e-12}s")
    
    """Defining the coincidence channels we want to save
    If you change the order, make sure it matches with the analysis code
    """
    GROUPS = [(1,3,5,7),(1,3,5,8),(1,3,6,7),(1,3,6,8),
            (1,4,5,7),(1,4,5,8),(1,4,6,7),(1,4,6,8),
            (2,3,5,7),(2,3,5,8),(2,3,6,7),(2,3,6,8),
            (2,4,5,7),(2,4,5,8),(2,4,6,7),(2,4,6,8)] 
    COINCIDENCE_WINDOW = 200 # in picosecond

    ##################################################################
    ##################### DEFINING THE PLAYERS #######################
    ##################################################################

    players = ["bran", "cersei", "dany"]
    sample=["SQWP1","SHWP","SQWP2"]

    # Create new device, Connect, begin polling, and enable
    arya = motors_control.players_init(["arya"])[0]
    bran, cersei, dany = motors_control.players_init(players, sample)

    print("Setting samples's angles")
    bran.set_sample_angles([43.51794941452298, 22.601808986092617, 42.90631184263254])
    cersei.set_sample_angles([-18.60208456082875, 70.01563655846527, -17.553712134270178])
    dany.set_sample_angles([55.239246729781016, 92.80890885315395, 35.42749172838185])

    ##################################################################
    ##################### RANDOMNESS ######################
    ##################################################################


    print("Choosing the Verifier")

    verifier = random.choice(players)

    print(f"The chosen verifier is :{verifier}")

    playerBit, playerBases, playerlabel = randomBit(len(players))

    print("here are player's bits : ")
    print(f"{players} = {playerBit}")

    arya.set_meas_basis(playerBases[0])
    bran.set_meas_basis(playerBases[1])
    cersei.set_meas_basis(playerBases[2])
    dany.set_meas_basis(playerBases[3])

    time.sleep(1.5)

    label=''.join([idx for tup in playerBases for idx in tup])
    playerlabels=''.join([idx for tup in playerlabel for idx in tup])

    print("Gathering the counts for bad (no bad words) analysis")
    
    tt.measure(AQUISITION_TIME,N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\ABCD={label}_{playerlabels}.txt", save_raw=True, save_params=True)    
    
    # Repeat = []
    # for z in range(3):
    #     Repeat.append(f"{z}")

    #     print('Starting the protocol !')

    #     Bases_label = {0: "x", 1: "y"}

    #     Bases_iterator = get_iterator(2,3)
    #     Bases = []

    #     for i in range(8):
    #         if (np.sum(Bases_iterator[i])%2) == 0:
    #                 Bases_iterator[i].append(0)
    #         else:
    #                 Bases_iterator[i].append(1)
    #         Bases.append(tuple(map(Bases_label.get, Bases_iterator[i])))

    #     for j in range(len(Bases)):
    #         phase=-69.009982
    #         arya.set_meas_basis(Bases[j][0], phase)
    #         bran.set_meas_basis(Bases[j][1])
    #         cersei.set_meas_basis(Bases[j][2])
    #         dany.set_meas_basis(Bases[j][3])

    #         time.sleep(1.5)

    #         Bits_label = list(map(str,Bases_iterator[j]))
    #         label=''.join([idx for tup in Bases[j] for idx in tup])
    #         Bit_label=''.join([idx for tup in Bits_label for idx in tup])

    #         print("Gathering the counts for analysis")
    #         tt.measure(AQUISITION_TIME,N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{label}_{Bit_label}_{z}.txt", save_raw=True, save_params=True)
        

    tt.free_swabian()
    arya.off()
    bran.off()
    cersei.off()
    dany.off()

if __name__ == "__main__":
    main()


