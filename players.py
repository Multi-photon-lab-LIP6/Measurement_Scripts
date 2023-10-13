### Created on: 05-09-2023
### Author: Laura Martins

import numpy as np

import time
import clr

# Add References to .NET libraries
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.BrushlessMotorCLI.dll.")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.BrushlessMotorCLI import *
from System import Decimal

from basis import MEAS_WP_ANGLES

# We define the serial numbers corresponding to the waveplates in each player
SERIAL_NO = {
                "ARYA": {"HWP": str("28250846"), "QWP": str("28250824")},
                "BRAN": {"HWP": str("28250843"), "QWP": str("28250701")},
                "CERSEI": {"HWP": str("28250804"), "QWP": str("28250807")},
                "DANY": {"HWP": str("28250806"), "QWP": str("28250811")},
            }

# Position of the motors, relative to their respective HOME, that aligns the fast axis with the horizontal position.
# This is necessary to make sure both WP's in the same measurement station are algined and than we can more easily be self-consistent
WP_ZEROS =  {
                "ARYA": {"HWP": 179.7273, "QWP": 244.86249},
                "BRAN": {"HWP": 178.8840, "QWP": 86.4759},
                "CERSEI": {"HWP": 175.6039, "QWP": 74.8664},
                "DANY": {"HWP": 37.0029, "QWP": 35.2849},
            }

# players_init initializes the different players we are using in each script
def players_init(players):
    players_list=[]
    for i, iter in enumerate(players):
        if iter == "arya":
            arya = Player("ARYA")
            players_list.append(arya)
        elif iter == "bran":
            bran = Player("BRAN")
            players_list.append(bran)
        elif iter == "cersei":
            cersei = Player("CERSEI")
            players_list.append(cersei)
        elif iter == "dany":
            dany = Player("DANY")
            players_list.append(dany)
    return players_list

"""
This class Connects, begins polling, and enables, moves to new position, stops polling and closes devices associated with each player
The devices correspond to a HWP and to a QWP
"""

class Player:
    def __init__(self, player):
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()

        self.name=player
        self.wp_name=["HWP", "QWP"]
        self.wp_serial_no=[SERIAL_NO[str(self.name)]["HWP"], SERIAL_NO[str(self.name)]["QWP"]]
        self.wp = [KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.wp_serial_no[0]),
                    KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.wp_serial_no[1])]
        print(self.wp)

        for i in range(2):
            self.wp[i].name = str(self.name)+self.wp_name[i]
            self.wp[i].Connect(self.wp_serial_no[i])
            time.sleep(0.25)

            self.wp[i].StartPolling(250)
            time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

            self.wp[i].EnableDevice()
            time.sleep(0.25)  # Wait for device to enable

            # Wait for Settings to Initialise
            if not self.wp[i].IsSettingsInitialized():
                self.wp[i].WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.wp[i].IsSettingsInitialized() is True

            # Before homing or moving device, ensure the motors configuration is loaded
            m_config = self.wp[i].LoadMotorConfiguration(self.wp_serial_no[i],
                                DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)

            time.sleep(1)

            # Home stage
            print("Homing Device: " + str(self.name) + " " + str(self.wp_name[i]))
            self.wp[i].Home(60000)  # 60 second timeout
            time.sleep(1.5)
            print("Device Homed: " + str(self.name) + " " + str(self.wp_name[i]))


    def set_meas_basis(self, basis):
        self.wp[0].MoveTo(Decimal((MEAS_WP_ANGLES[str(basis)]["HWP"]+WP_ZEROS[self.name]["HWP"])%360), 10000)
        self.wp[1].MoveTo(Decimal((MEAS_WP_ANGLES[str(basis)]["QWP"]+WP_ZEROS[self.name]["QWP"])%360), 10000)
        time.sleep(1.5)


    def set_meas_angles(self, angles):
        self.wp[0].MoveTo(Decimal((angles[0]+WP_ZEROS[self.name]["HWP"])%360), 10000)
        self.wp[1].MoveTo(Decimal((angles[1]+WP_ZEROS[self.name]["QWP"])%360), 10000)
        time.sleep(1.5)

    def off(self):
        self.wp[0].StopPolling()
        self.wp[1].StopPolling()
        self.wp[0].Disconnect(True)
        self.wp[1].Disconnect(True)
