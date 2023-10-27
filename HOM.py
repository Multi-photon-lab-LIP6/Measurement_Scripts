### Created on: 09-2023
import time

import TT
import motors_control

def main():
    try:
        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1, 2, 5, 6, 7, 8]
        TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13]
        DELAY = [0, -816, -36173, -34046, -526, -1418]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "HOM", "HOM")

        AQUISITION_TIME = int(2*60E12) # in picosecond
        N_REP = 1
        """
        Defining the coincidence channels we want to save
        If you change the order, make sure it matches with the analysis code
        """
        GROUPS = [(5,6),(1,5),(6,8),(1,5,6),(1,6,8),(1,5,8),(5,6,8),(1,5,6,8)]
        COINCIDENCE_WINDOW = 500 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["arya", "cersei", "dany"]

        # Create new device, Connect, begin polling, and enable
        arya, cersei, dany = motors_control.players_init(players)

        arya.set_meas_basis("z")
        cersei.set_meas_basis("x")
        dany.set_meas_basis("z")
        time.sleep(1.5)

        # Init Delay Stage class

        delay = motors_control.Delay()
        position = float(delay.channel.Position.ToString())
        init=0

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        while float(position)<50:
            if init!=0:
                delay.move(step=0.1)
            position = delay.channel.Position.ToString()
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\position={position}mm.txt", save_raw=True, save_params=True)
            time.sleep(1.5)
            init=1

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