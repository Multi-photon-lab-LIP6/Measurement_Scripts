import time
import itertools
import random
import TT
from basis import MEAS_WP_ANGLES
import motors_control

def randomBit(number_player):
    playerBit = []
    playerBases = []

    for z in range(number_player-1):

        if random.random() > .5:
            playerBases.append('y')
            playerBit.append(1)
        else:
            playerBases.append('x')
            playerBit.append(0)

    if (sum(playerBit)%2) == 0:
        playerBases.append('x')
        playerBit.append(0)
    else:
        playerBases.append('y')
        playerBit.append(1)
        

    return playerBit,playerBases

def main():

    CHANNELS = [1, 2, 3, 4, 5, 6, 7, 8]
    TRIGGER = [0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.12]
    DELAY = [0, -846, -30200, -36547, -35543, -36776, -800, 1400]
    tt = TT.Swabian(CHANNELS, TRIGGER, DELAY, "PROTOCOL", "VERIFICATION")

    AQUISITION_TIME = int(0.3*60E12) # in picosecond
    N_REP = 1
    """Defining the coincidence channels we want to save
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
    arya, bran, cersei, dany = motors_control.players_init(players)

    ##################################################################
    ##################### RANDOMNESS ######################
    ##################################################################


    print("Choosing the Verifier")

    verifier = random.choice(players)

    print(f"The chosen verifier is :{verifier}")

    playerBit, playerBases = randomBit(len(players))

    print("here are player's bits : ")
    print(f"{players} = {playerBit}")

    phase=-69.009982
    arya.set_meas_basis(playerBases[0], phase)
    bran.set_meas_basis(playerBases[1])
    cersei.set_meas_basis(playerBases[2])
    dany.set_meas_basis(playerBases[3])

    time.sleep(1.5)

    label=''.join([idx for tup in playerBases for idx in tup])
    print("Gathering the counts for bad (no bad words) analysis")
    tt.measure(AQUISITION_TIME, N_REP, GROUPS, COINCIDENCE_WINDOW, count_singles=True, data_filename=f"\ABCD={label}.txt", save_raw=True, save_params=True)

    tt.free_swabian()
    arya.off()
    bran.off()
    cersei.off()
    dany.off()

if __name__ == "__main__":
    main()


