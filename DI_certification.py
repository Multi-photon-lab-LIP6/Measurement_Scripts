import time
import itertools
import random
import TT
from basis import MEAS_WP_ANGLES
import motors_control
import numpy as np

def main():

    CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    TRIGGER = [0.12, 0.12, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13]
    DELAY = [0,  2790, -26700, -33000, -39640, -40470, -4500, -3010]
    AQUISITION_TIME = int(0.25*60E12) # in picosecond
    N_REP = 1
    tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "PROTOCOL", f"DI_CERTIFICATION_aqtime={AQUISITION_TIME*1e-12}s")
    
    """Defining the coincidence channels we want to save
    If you change the order, make sure it matches with the analysis code
    """
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
            (2,4,6,8,1),(2,4,6,8,3),(2,4,6,8,5),(2,4,6,8,7),]         
            
    COINCIDENCE_WINDOW = 200 # in picosecond

    ##################################################################
    ##################### DEFINING THE PLAYERS #######################
    ##################################################################

    players = ["arya", "bran", "cersei"]
    sample=["SQWP1","SHWP","SQWP2"]

    # Create new device, Connect, begin polling, and enable

    arya, bran, cersei = motors_control.players_init(players, sample)
    dany = motors_control.players_init(["dany"])[0]

    print("Setting samples's angles")
    arya.set_sample_angles([45.78026274995648, 19.05861788018144, 41.35234860141521])
    bran.set_sample_angles([56.137231503957636, -35.427286939093186, -122.45435442606853])
    cersei.set_sample_angles([41.98625880438878, 31.326657323798784, 43.129514519815515])


    ##### Defining the Mermin operators ######
    
    stabilizers = ["zzzz","xxxx","yyxx","yxyx","yxxy","yyyy","xxyy","xyxy","xyyx","zzzz","zzzz","zzzz"]

    #######################################################
    ##################### RANDOMNESS ######################
    #######################################################

    for i in range(300):
        print("Choosing the stabilizer")
        operator = random.choice(stabilizers)
        print(f"Measuring: {operator}")
        arya.set_meas_basis(str(operator[0]))
        bran.set_meas_basis(str(operator[1]))
        cersei.set_meas_basis(str(operator[2]))
        dany.set_meas_basis(str(operator[3]))
        time.sleep(0.2)
        tt.measure(AQUISITION_TIME,N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\ABCD={operator}_{i}.txt", save_raw=True, save_params=True)    
    
   # Leave the WP's in the Z basis
    print("Setting measurements' basis to 0")
    arya.set_meas_basis("z")
    bran.set_meas_basis("z")
    cersei.set_meas_basis("z")
    dany.set_meas_basis("z")

    # print("Setting samples's angles to 0")
    # arya.set_sample_angles([0,0,0])
    # bran.set_sample_angles([0,0,0])
    # cersei.set_sample_angles([0,0,0])

    tt.free_swabian()
    # # Stop polling and close devices
    arya.off()
    bran.off()
    cersei.off()
    dany.off()

    arya.off_sample()
    bran.off_sample()
    cersei.off_sample()

if __name__ == "__main__":
    main()


