import numpy as np

from players import players_init
import TT

def main():
    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [2, 4]
        TRIGGER = [0.13, 0.13]
        DELAY = [-850, -11880]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "Bran_hwp")

        AQUISITION_TIME = int(5E12) # in picosecond
        N_REP = 1
        GROUPS = [(2,4)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["bran"]

        # Create new device, Connect, begin polling, and enable
        arya = players_init(players)[0]
        meas_angles = np.linspace(-90,90,91)

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        
        for i in meas_angles:
            ### the players' motors are rotated to i
            ### In player.set_meas_angles([a,b]): a (b) is the angle of the HWP (QWP)
            print(f"Measuring angle: {i}")
            arya.set_meas_angles([i,0])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}.txt", save_raw=True, save_params=True)

            ######### Control Measure ##########
            ### Alternating between measuring the angles of interest and [0,0] such that we can see fluctions of power
            arya.set_meas_angles([0,0])
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}Control.txt", save_raw=True, save_params=True)

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()