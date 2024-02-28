### Created on: 09-2023

import numpy as np

import motors_control
import TT

def init_sample(wp):
    if wp=="SQWP2":
        sample=["SQWP2"]
        angles=[]
        angles_control=[]
    elif wp=="SHWP":
        sample=["SHWP","SQWP2"]
        angles=[0]
        angles_control=[0]
    elif wp=="SQWP1":
        sample=["SQWP1","SHWP","SQWP2"]
        angles=[0,0]
        angles_control=[0,0]
    return sample, angles, angles_control
    

def main():
    try:
        ### Defining the players
        players = ['BRAN','CERSEI']
        wp=["SQWP1","SQWP1"]

        ##################################################################
        ############### DEFINING AND SAVING PARAMS #######################
        ##################################################################
        CHANNELS = [2, 4, 6, 8]
        TRIGGER = [0.13,0.13,0.13,0.12]
        DELAY = [-320, -25770, -24890, 3080]
        tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "WP_calib", f"{players[0]}_{wp[0]}", f"{players[1]}_{wp[1]}")
        

        AQUISITION_TIME = int(1E12) # in picosecond
        N_REP = 1
        GROUPS = [(2,4),(6,8)]
        COINCIDENCE_WINDOW = 200 # in picosecond

        ##################################################################
        ##################### DEFINING THE PLAYERS #######################
        ##################################################################

        # Create new device, Connect, begin polling, and enable
        sample, angles, angles_control = init_sample(wp=wp[0])

        arya, dany = motors_control.players_init(players, sample=sample)
        print("Initialized")
        meas_angles = np.linspace(-90,90,91)

        ##########################################################
        ############### START MEASUREMENTS #######################
        ##########################################################
        
        for i in meas_angles:
            ### the players' motors are rotated to i
            ### In player.set_meas_angles([a,b]): a (b) is the angle of the HWP (QWP)
            if wp[0]=="QWP" or wp[0]=="HWP":
                arya.set_meas_angles([0,i])
                dany.set_meas_angles([0,i])
            elif wp[0]=="HWP":
                arya.set_meas_angles([i,0])
                dany.set_meas_angles([i,0])
            elif wp[0]=="SQWP2" or wp[0]=="SHWP" or wp[0]=="SQWP1":
                arya.set_meas_angles([0,0])
                dany.set_meas_angles([0,0])
                arya.set_sample_angles([i]+angles)
                dany.set_sample_angles([i]+angles)
            else:
                print("Not a valid waveplate. Please set wp to either HWP or QWP")
                break

            print(f"Measuring angle: {i} of {wp[0]}")
            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}.txt", save_raw=True, save_params=True)

            ######### Control Measure ##########
            ### Alternating between measuring the angles of interest and [0,0] such that we can see fluctions of power
            arya.set_meas_angles([0,0])
            dany.set_meas_angles([0,0])
            if wp[0]=="SQWP2" or wp[0]=="SHWP" or wp[0]=="SQWP1":
                arya.set_sample_angles([0]+angles_control)
                dany.set_sample_angles([0]+angles_control)

            tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=False, data_filename=f"\{i}Control.txt", save_raw=True, save_params=True)

        tt.free_swabian()
        # Stop polling and close devices
        arya.off()
        dany.off()
        arya.off_sample()
        dany.off_sample()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()