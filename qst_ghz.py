### Created on: 10-2023

import time
import itertools

import TT

import motors_control

def main():
    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
        TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13]
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
        arya, bran, cersei, dany = motors_control.players_init(players)

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
            ### the players' motors are rotated to the intended meas_basis
            print(f"Measuring basis: {base}")
            arya.set_meas_basis(base[0])
            bran.set_meas_basis(base[1])
            cersei.set_meas_basis(base[2])
            dany.set_meas_basis(base[3])
            time.sleep(1.5)

            label=''.join([idx for tup in base for idx in tup])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\ABCD={label}.txt", save_raw=True, save_params=True)

        # Leave the WP's in the Z basis
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

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()