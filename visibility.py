### Created on: 09-2023
import time

import TT
import motors_control

def main():
    try:

        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
        TRIGGER = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.12]
        DELAY = [0, -860, -30350, -36500, -35980, -35470, -1000, -210]
        AQUISITION_TIME = int(15E12) # in picosecond
        N_REP = 1
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "Visibility", "Vis")

        """
        Defining the coincidence channels we want to save
        If you change the order, make sure it matches with the analysis code
        """
        GROUPS=[(1,3,5,7),(1,3,5,8),(1,3,6,7),(1,3,6,8),
                (1,4,5,7),(1,4,5,8),(1,4,6,7),(1,4,6,8),
                (2,3,5,7),(2,3,5,8),(2,3,6,7),(2,3,6,8),
                (2,4,5,7),(2,4,5,8),(2,4,6,7),(2,4,6,8)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################
        players = ["arya", "bran", "cersei", "dany"]
        sample=["SQWP1","SHWP","SQWP2"]

        # Create new device, Connect, begin polling, and enable
        arya, bran, cersei, dany = motors_control.players_init(players, sample)
        # dany = motors_control.players_init(["dany"])[0]

        print("Setting samples's angles")
        arya.set_sample_angles([45.834279397646945, 18.228164683424932, 43.469316413428494])
        bran.set_sample_angles([-132.4976980856427, -50.90790743923844, 45.17063791251477])
        cersei.set_sample_angles([-49.05899688705664, 8.228519568104886, -36.44645550182834])
        dany.set_sample_angles([39.4492140870581, 78.4269631184705, 43.520951622247125])

        print("Setting measurement basis")
        arya.set_meas_basis("x")
        bran.set_meas_basis("x")
        cersei.set_meas_basis("x")
        dany.set_meas_basis("x")

        # Init Delay Stage class
        delay = motors_control.Delay()
        # position_ini = float(delay.channel.Position.ToString())
        position_final = float(56.5)
        position = float(delay.channel.Position.ToString())
        init=0

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        while float(position)<position_final:
            if init!=0:
                delay.move(step=0.02)
            position = delay.channel.Position.ToString()
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\position={position}mm.txt", save_raw=True, save_params=True)
            time.sleep(0.5)
            init=1

        # Leave the WP's in the Z basis
        print("Setting measurements' basis to 0")
        arya.set_meas_basis("z")
        bran.set_meas_basis("z")
        cersei.set_meas_basis("z")
        dany.set_meas_basis("z")

        print("Setting samples's angles to 0")
        bran.set_sample_angles([0,0,0])
        cersei.set_sample_angles([0,0,0])
        dany.set_sample_angles([0,0,0])

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()
        bran.off()
        cersei.off()
        dany.off()

        bran.off_sample()
        cersei.off_sample()
        dany.off_sample()

        delay.device.Disconnect()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()