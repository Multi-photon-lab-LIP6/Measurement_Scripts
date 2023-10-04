import time
import itertools

import TT

from players import players_init

def main():
    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1 ,2 ,3, 4, 5, 6, 7, 8]
        TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13]
        DELAY = [0, -850, 4825, -1550, 0, 2110, 660, -220]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "QST")

        AQUISITION_TIME = int(60E12) # in picosecond
        N_REP = 1
        """
        Defining the coincidence channels we want to save
        If you change the order, make sure it matches with the analysis code
        """
        GROUPS = [(1,3),(1,4),(2,3),(2,4),(5,7),(5,8),(6,7),(6,8), #pair coincidences we want to generate
                  (1,2,3),(1,2,4),(1,3,4),(2,3,4),(1,2,3,4), # unwanted double emission coincidences we need to account for in the QST
                  (5,6,7),(5,6,8),(5,7,8),(6,7,8),(5,6,7,8)] # unwanted double emission coincidences we need to account for in the QST
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["arya", "bran", "cersei", "dany"]

        # Create new device, Connect, begin polling, and enable
        arya, bran, cersei, dany = players_init(players)

        # Setting the measurmenet basis we want to measure
        elem_bases = ["x","y","z"]
        meas_bases = list(itertools.product(elem_bases, repeat=2))
        for iter, value in enumerate(meas_bases): meas_bases[iter]=value+value
        # Adding to meas_basis to compensatecalculate correction factor that compensates for the different efficiencies in the different paths, detectors, etc
        eff_list = [("z","z","z","z"),("z","a","z","a"),("a","z","a","z"),("a","a","a","a")]
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