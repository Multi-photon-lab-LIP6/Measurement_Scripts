import time

import TT

from players import players_init
import delay_stage

def main():
    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1 ,2 , 5, 6, 7, 8]
        TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13]
        DELAY = [0, -850, -11520, -9380, -510, -1390]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "HOM")

        AQUISITION_TIME = int(5*60E12) # in picosecond
        N_REP = 1
        """
        Defining the coincidence channels we want to save
        If you change the order, make sure it matches with the analysis code
        """
        GROUPS = [(1,7),(6,8),(1,6,7),(1,6,8),(1,7,8),(6,7,8),(1,6,7,8)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["arya", "cersei", "dany"]

        # Create new device, Connect, begin polling, and enable
        arya, cersei, dany = players_init(players)

        arya.set_meas_basis("z")
        cersei.set_meas_basis("x")
        dany.set_meas_basis("z")
        time.sleep(1.5)

        # Setting the measurmenet basis we want to measure

        delay = delay_stage.Delay()

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        delay.move()
        for step in range(11):
            if step>0:
                delay.move()
            position = delay.channel.Position.ToString()
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\position={position}mm.txt", save_raw=True, save_params=True)
            time.sleep(1.5)

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()
        cersei.off()
        dany.off()
        delay.off()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()