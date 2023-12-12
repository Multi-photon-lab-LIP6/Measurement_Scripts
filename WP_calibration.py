### Created on: 09-2023

import numpy as np

import motors_control
import TT

def main():
    try:
        ### Defining the players
        players = ["ARYA",'DANY']
        wp=["HWP","HWP"]

        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [2, 3, 5, 8]
        TRIGGER = [0.13,0.13,0.13,0.12]
        DELAY = [-830, -19600,-23700, 3080 ]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "WP_calib", f"{players[0]}_{wp[0]}", f"{players[1]}_{wp[1]}")
        

        AQUISITION_TIME = int(4E12) # in picosecond
        N_REP = 1
        GROUPS = [(2,3),(5,8)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################

        # Create new device, Connect, begin polling, and enable
        arya, dany = motors_control.players_init(players)
        meas_angles = np.linspace(-90,90,91)

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        
        for i in meas_angles:
            ### the players' motors are rotated to i
            ### In player.set_meas_angles([a,b]): a (b) is the angle of the HWP (QWP)
            if wp[0]=="QWP":
                arya.set_meas_angles([0,i])
                dany.set_meas_angles([0,i])
            elif wp[0]=="HWP":
                arya.set_meas_angles([i,0])
                dany.set_meas_angles([i,0])
            else:
                print("Not a valid waveplate. Please set wp to either HWP or QWP")
                break

            print(f"Measuring angle: {i} of {wp[0]}")
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}.txt", save_raw=True, save_params=True)

            ######### Control Measure ##########
            ### Alternating between measuring the angles of interest and [0,0] such that we can see fluctions of power
            arya.set_meas_angles([0,0])
            dany.set_meas_angles([0,0])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}Control.txt", save_raw=True, save_params=True)

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()
        dany.off()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()