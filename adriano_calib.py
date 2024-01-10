### Created on: 09-2023

import numpy as np

import motors_control
import TT

def main():
    try:
        ### Defining the players
        players = ["ARYA"]

        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1, 2]
        TRIGGER = [0.13, 0.13]
        DELAY = [-830, -19600]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "adriano_calib", f"{players[0]}_{wp[0]}")
        

        AQUISITION_TIME = int(4E12) # in picosecond
        N_REP = 1
        GROUPS = [(1,2)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################

        # Create new device, Connect, begin polling, and enable
        arya = motors_control.players_init(players)
        meas_angles = np.linspace(-90,90,91)

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        
        for i in meas_angles:
            ### the players' motors are rotated to i
            ### In player.set_meas_angles([a,b]): a (b) is the angle of the HWP (QWP)
            arya.set_meas_angles([0,i])
            arya.set_meas_basis("x")

            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\{i}.txt", save_raw=True, save_params=True)

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()