import time
import itertools
import random
import TT
from basis import MEAS_WP_ANGLES
import motors_control
import numpy as np

def main():

    CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    TRIGGER = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.12]
    DELAY = [0, -860, -30350, -36500, -35980, -35470, -1000, -210]
    AQUISITION_TIME = int(200E12) # in picosecond
    N_REP = 1
    tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "Protocols", f"stabilizers_aqtime={AQUISITION_TIME*1e-12}s")
    
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
    ##################################################################s

    players = ["arya", "bran", "cersei", "dany"]
    sample=["SQWP1","SHWP","SQWP2"]

    # Create new device, Connect, begin polling, and enable
    arya, bran, cersei, dany = motors_control.players_init(players, sample)

    print("Setting samples's angles")
    arya.set_sample_angles([-42.00782452129922, 25.442433914476226, -44.09805746744701])
    bran.set_sample_angles([60.81105516421106, -28.570943797728077, -111.1336745991076])
    cersei.set_sample_angles( [-35.928902014737176, -54.66030295287478, -38.0598320234497])
    dany.set_sample_angles([31.27906498116531, 37.61636310168101, 34.92838604167537])

    ##### Defining the stabilizers ######
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
        "xyxy", #This is wrong
        "yxxy", #This is wrong
        "yyyy"
    ]

    #######################################################
    ##################### RANDOMNESS ######################
    #######################################################

    for i, operator in enumerate(stabilizers):
        print(f"Measuring: {operator}")

        arya.set_meas_basis(str(operator[0]))
        bran.set_meas_basis(str(operator[1]))
        cersei.set_meas_basis(str(operator[2]))
        dany.set_meas_basis(str(operator[3]))
        time.sleep(1.5)
    
        tt.measure(AQUISITION_TIME,N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\ABCD={operator}.txt", save_raw=True, save_params=True)    
    
    # Leave the WP's in the Z basis
    print("Setting measurements' basis to 0")
    arya.set_meas_basis("z")
    bran.set_meas_basis("z")
    cersei.set_meas_basis("z")
    dany.set_meas_basis("z")

    tt.free_swabian()
    # Stop polling and close devices
    arya.off()
    bran.off()
    cersei.off()
    dany.off()

    bran.off_sample()
    cersei.off_sample()
    arya.off_sample()

if __name__ == "__main__":
    main()


