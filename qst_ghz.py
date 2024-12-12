### Created on: 10-2023

import time
import itertools
from datetime import timedelta
import TT

import motors_control

def main():
    try:
        start_time = time.monotonic()
        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["arya", "bran", "cersei", "dany"]
        sample=["SQWP1","SHWP","SQWP2"]

        # Create new device, Connect, begin polling, and enable
        arya, bran, cersei, dany = motors_control.players_init(players, sample)

        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
        TRIGGER = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.12]
        DELAY = [0, -860, -30350, -36500, -35980, -35470, -1000, -210]
        AQUISITION_TIME = int(100E12) # in picosecond
        N_REP = 1

        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "QST", f"QST_GHZ_aqtime={AQUISITION_TIME*1e-12}s")
        time.sleep(2)

        """
        Defining the coincidence channels we want to save
        If you change the order, make sure it matches with the analysis code
        """

        GROUPS=[(1,3,5,7),(1,3,5,8),(1,3,6,7),(1,3,6,8),
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
                          
        COINCIDENCE_WINDOW = 200 # in picosecond 

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################

        print("Setting samples's angles")
        arya.set_sample_angles([46.282297250730494, 116.71935075047799, 41.42340727433868])
        bran.set_sample_angles([24.481702600831554, 5.535044154126424, 60.30601589399454])
        cersei.set_sample_angles([-39.69547157882599, 59.987239383378245, 127.41263673906985])
        dany.set_sample_angles([-123.77555284080137, -19.375698630319153, 44.19271469899905])

        # Setting the measurmenet basis we want to measure
        elem_bases = ["x","y","z"]
        meas_bases = list(itertools.product(elem_bases, repeat=4))
        # # Adding to meas_basis to compensatecalculate correction factor that compensates for the different efficiencies in the different paths, detectors, etc
        eff_bases = ["z","a"]
        eff_list = list(itertools.product(eff_bases, repeat=4))
        meas_bases=meas_bases+eff_list

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        for base in meas_bases:
            ### the players' motors are rotated to the intended meas_basis²²²
            print(f"Measuring basis: {base}")
            arya.set_meas_basis(base[0])
            bran.set_meas_basis(base[1])
            cersei.set_meas_basis(base[2])
            dany.set_meas_basis(base[3])
        
            label=''.join([idx for tup in base for idx in tup])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\ABCD={label}.txt", save_raw=True, save_params=True)

        
        # Leave the WP's in the Z basis
        print("Setting measurements' basis to 0")
        arya.set_meas_basis("z")
        bran.set_meas_basis("z")
        cersei.set_meas_basis("z")
        dany.set_meas_basis("z")

        print("Setting samples's angles to 0")
        arya.set_sample_angles([0, 0, 0])
        bran.set_sample_angles([0, 0, 0])
        cersei.set_sample_angles([0, 0, 0])
        dany.set_sample_angles([0,0,0])

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()
        bran.off()
        cersei.off()
        dany.off()

        arya.off_sample()
        bran.off_sample()
        cersei.off_sample()
        dany.off_sample()
        end_time = time.monotonic()
        print(timedelta(seconds=end_time - start_time))

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()