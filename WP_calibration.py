import numpy as np

from players import players_init
import TT

def main():
    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [4, 6, 7]
        TRIGGER = [0.13, 0.13, 0.13]
        DELAY = [-36530, -33990, -530]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "Bran_hwp", "Cersei_hwp")

        AQUISITION_TIME = int(6E12) # in picosecond
        N_REP = 1
        GROUPS = [(4,7),(6,7)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["bran","cersei"]

        # Create new device, Connect, begin polling, and enable
        bran, cersei = players_init(players)
        meas_angles = np.linspace(-90,90,91)

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        
        for i in meas_angles:
            ### the players' motors are rotated to i
            ### In player.set_meas_angles([a,b]): a (b) is the angle of the HWP (QWP)
            print(f"Measuring angle: {i}")
            bran.set_meas_angles([i,0])
            cersei.set_meas_angles([i,0])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}.txt", save_raw=True, save_params=True)

            ######### Control Measure ##########
            ### Alternating between measuring the angles of interest and [0,0] such that we can see fluctions of power
            bran.set_meas_angles([0,0])
            cersei.set_meas_angles([0,0])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}Control.txt", save_raw=True, save_params=True)

        tt.free_swabian()
        # Stop polling and close devices
        bran.off()
        cersei.off()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()