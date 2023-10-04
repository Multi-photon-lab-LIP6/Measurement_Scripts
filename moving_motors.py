import clr

from matplotlib import pyplot as plt
from time import sleep

# Add References to .NET libraries
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.BrushlessMotorCLI.dll.")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.BrushlessMotorCLI import *
from System import Decimal

from players import Player, players_init

def main():

    try:
        # Define the players
        players = ["arya", "bran"]

        """
        WP Motors init
        """
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()
        # Create new device, Connect, begin polling, and enable
        arya, bran = players_init(players)

        # Move Device to a new position:
        arya.set_meas_basis("Z")
        bran.set_meas_basis("Z")

        # # Stop polling and close devices
        arya.off()
        bran.off()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()