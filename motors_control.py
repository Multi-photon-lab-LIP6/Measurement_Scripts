### Created on: 10-2023
### Includes several classes to control the different Thorlabs motors in the setup
### We should test if all scripts run without the individual .py files created for each motor. If so, we can delete and replace them for just this script

import numpy as np

import time
import clr

import os
import sys

# Add References to .NET libraries
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll.")

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.BrushlessMotorCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.SolenoidCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.Benchtop.StepperMotorCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.BrushlessMotorCLI import *
from Thorlabs.MotionControl.KCube.SolenoidCLI import *
from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import *

from System import Decimal

from basis import MEAS_WP_ANGLES

# We define the serial numbers corresponding to the waveplates in each player, the delay stage and the shutter
SERIAL_NO = {
                "ARYA": {"HWP": str("28250846"), "QWP": str("28250824"), "SQWP2": str("28253100"),"SHWP": str("28252968"),"SQWP1": str("28253193")},
                "BRAN": {"HWP": str("28250843"), "QWP": str("28250701"),"SQWP2": str("28252978"),"SHWP": str("28253186"),"SQWP1": str("28253024")},
                "CERSEI": {"HWP": str("28250804"), "QWP": str("28250807"),"SQWP2": str("28253068"),"SHWP": str("28253095"),"SQWP1": str("28253074")},
                "DANY": {"HWP": str("28250806"), "QWP": str("28250811"),"SQWP2": str("28252981"),"SHWP": str("28252975"),"SQWP1": str("28252976")},
                "DELAY": str("40381974"),
                "SHUTTER": str("68800559")
            }
"""
Position of the motors, relative to their respective HOME, that aligns the fast axis with the horizontal position.
This is necessary to make sure both WP's in the same measurement station are algined and than we can more easily be self-consistent
"""
WP_ZEROS =  {
                "ARYA": {"HWP": 13.2477203, "QWP": 174.460649,"SQWP2": 148.379524, "SHWP": 48.558451, "SQWP1": 53.3219460},
                "BRAN": {"HWP": 13.91959, "QWP": 156.5907,"SQWP2": 147.75603450, "SHWP": 65.1809823, "SQWP1": 298.8269421},
                "CERSEI": {"HWP": 190.0750650, "QWP": 67.785387, "SQWP2": 59.244498, "SHWP": 205.189772, "SQWP1": 92.1837136076},
                "DANY": {"HWP": 300.91003135345167, "QWP": 214.76183, "SQWP2": 69.90931308401102, "SHWP": 194.99868056282844, "SQWP1": 136.175057930766116}
            }

"""
Default position of the delay stage. It corresponds to the position for maximum interference
between the two emitted pairs (top and bottom) - found with the hom.py and HOM.ipynb scripts 
"""
INTERFERENCE_POSITION = 57.5

# players_init initializes the different players we are using in each script
def players_init(players, sample=None):
    players_list=[]
    for i, iter in enumerate(players):
        if iter == "arya" or iter == "ARYA":
            arya = Player("ARYA", sample)
            players_list.append(arya)
        elif iter == "bran" or iter == "BRAN":
            bran = Player("BRAN", sample)
            players_list.append(bran)
        elif iter == "cersei" or iter == "CERSEI":
            cersei = Player("CERSEI", sample)
            players_list.append(cersei)
        elif iter == "dany" or iter == "DANY":
            dany = Player("DANY", sample)
            players_list.append(dany)
    return players_list

"""
This class Connects, begins polling, and enables, moves to new position, stops polling and closes devices associated with each player
The devices correspond to a HWP and to a QWP
"""
class Player:
    def __init__(self, player, sample=None):
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()

        self.name=player

        self.wp_name=["HWP", "QWP"]
        self.wp_serial_no=[SERIAL_NO[str(self.name)]["HWP"], SERIAL_NO[str(self.name)]["QWP"]]
        self.wp = [KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.wp_serial_no[0]),
                    KCubeBrushlessMotor.CreateKCubeBrushlessMotor(self.wp_serial_no[1])]
        print(self.wp)
    
        ### Connecting to the HWP-QWP measurement basis waveplates
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
            
        ### Connecting to the QWP-HWP-QWP sample waveplates
        if sample is not None:
            self.sample_wp_name = sample
            self.sample_wp_serial_no=[SERIAL_NO[str(self.name)][j] for i,j in enumerate(sample)]
            self.sample_wp = [KCubeBrushlessMotor.CreateKCubeBrushlessMotor(j) for i,j in enumerate(self.sample_wp_serial_no)] 
        
            print(self.sample_wp)

            for i in range(len(sample)):
                self.sample_wp[i].name = str(self.name)+self.sample_wp_name[i]
                self.sample_wp[i].Connect(self.sample_wp_serial_no[i])
                time.sleep(0.25)

                self.sample_wp[i].StartPolling(250)
                time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

                self.sample_wp[i].EnableDevice()
                time.sleep(0.25)  # Wait for device to enable

                # Wait for Settings to Initialise
                if not self.sample_wp[i].IsSettingsInitialized():
                    self.sample_wp[i].WaitForSettingsInitialized(10000)  # 10 second timeout
                    assert self.sample_wp[i].IsSettingsInitialized() is True

                # Before homing or moving device, ensure the motors configuration is loaded
                m_config = self.sample_wp[i].LoadMotorConfiguration(self.sample_wp_serial_no[i],
                                DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)

                time.sleep(1)

                    # Home stage
                print("Homing Device: " + str(self.name) + " " + str(self.sample_wp_name[i]))
                self.sample_wp[i].Home(60000)  # 60 second timeout
                time.sleep(1.5)
                print("Device Homed: " + str(self.name) + " " + str(self.sample_wp_name[i]))


    def set_meas_basis(self, basis):
        self.wp[0].MoveTo(Decimal((MEAS_WP_ANGLES[str(basis)]["HWP"]+WP_ZEROS[self.name]["HWP"])%360), 10000)
        self.wp[1].MoveTo(Decimal((MEAS_WP_ANGLES[str(basis)]["QWP"]+WP_ZEROS[self.name]["QWP"])%360), 10000)

    def set_meas_angles(self, angles):
        self.wp[0].MoveTo(Decimal((angles[0]+WP_ZEROS[self.name]["HWP"])%360), 10000)
        self.wp[1].MoveTo(Decimal((angles[1]+WP_ZEROS[self.name]["QWP"])%360), 10000)

    def set_sample_angles(self, angles):
        for i, angle in enumerate(angles):
            self.sample_wp[i].MoveTo(Decimal((angle+WP_ZEROS[self.name][self.sample_wp_name[i]])%360), 10000)

    def off(self):
        self.wp[0].StopPolling()
        self.wp[1].StopPolling()
        self.wp[0].Disconnect(True)
        self.wp[1].Disconnect(True)
    
    def off_sample(self):
        for i, j in enumerate(self.sample_wp):
            self.sample_wp[i].StopPolling()
            self.sample_wp[i].Disconnect(True)
            
    def set_velocity(self,velo,acc):
        for i in range(2):
            self.wp[i].SetSettings(self.wp[i].MotorDeviceSettings, True)
            self.wp[i].SetVelocityParams(Decimal(velo), Decimal(acc))
                

    
"""
This class Connects, begins polling, and enables, moves to new position, stops polling and closes the delay stage device
"""
class Delay:
    def __init__(self):
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()

        self.serial_no = SERIAL_NO["DELAY"]
        self.device = BenchtopStepperMotor.CreateBenchtopStepperMotor(self.serial_no)
        self.device.Connect(self.serial_no)
        print("Connecting and enabling delay stage")
        time.sleep(0.25)

        self.channel = self.device.GetChannel(1)

        # Ensure that the device settings have been initialized
        if not self.channel.IsSettingsInitialized():
            self.channel.WaitForSettingsInitialized(20000)  # 10 second timeout
            assert self.channel.IsSettingsInitialized() is True

        print("Delay Initialized")
        # Start polling and enable
        self.channel.StartPolling(250)  #250ms polling rate
        time.sleep(25)
        self.channel.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable
        print("Delay Enabled")

        # Get Device Information and display description
        device_info = self.channel.GetDeviceInfo()
        print(device_info.Description)

        # Load any configuration settings needed by the controller/stage
        channel_config = self.channel.LoadMotorConfiguration(self.serial_no) # If using BSC203, change serial_no to channel.DeviceID. 
        chan_settings = self.channel.MotorDeviceSettings
        self.channel.GetSettings(chan_settings)
        channel_config.DeviceSettingsName = 'HS NRT100/M Enc Stage 100mm'
        channel_config.UpdateCurrentConfiguration()
        self.channel.SetSettings(chan_settings, True, False)

        self.get_home_params()
        print(f"Delay's position currently at {self.channel.Position.ToString()} mm")

    def get_home_params(self):
        self.home_params = self.channel.GetHomingParams()
        print(f'Homing velocity: {self.home_params.Velocity}\n'
              f'Homing Direction: {self.home_params.Direction}')
        
    def set_home_params(self, velocity=10.0):
        # Get parameters related to homing/zeroing/other
        self.home_params.Velocity = Decimal(velocity)  # real units, mm/s
        # Set homing params (if changed)
        self.device.SetHomingParams(self.home_params)

    def home(self):
        # Home or Zero the device (if a motor/piezo)
        print("Homing Linear Stage Translator")
        self.channel.Home(60000) # 60 second timeout
        print("Done")

    def move(self, step=0.1):
    # Move the device to a new position
        self.channel.SetMoveRelativeDistance(Decimal(step))
        print(f"Moving Delay stage by {step} mm")
        self.channel.MoveRelative(10000)
        time.sleep(1)
        print("Done Moving")
            
    def off(self):
        # Stop Polling and Disconnect
        self.channel.StopPolling()
        self.device.Disconnect()

"""
This class Connects, begins polling, and enables, opens and closes, stops polling and turns off the mechanical shutter device
"""
class Shutter:
    def __init__(self):
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()

        self.serial_no = SERIAL_NO["SHUTTER"]
        # Connect
        self.device = KCubeSolenoid.CreateKCubeSolenoid(self.serial_no)
        self.device.Connect(self.serial_no)
        print("Connecting and enabling shutter")

        # Ensure that the device settings have been initialized
        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

        # Start polling and enable
        self.device.StartPolling(250)  #250ms polling rate
        time.sleep(0.25)
        self.device.EnableDevice()
        time.sleep(0.5)  # Wait for device to enable

        # Get Device Information and display description
        device_info = self.device.GetDeviceInfo()
        print(device_info.Description)

        self.oper_mode_manual()

    def oper_mode_manual(self):
        self.device.SetOperatingMode(SolenoidStatus.OperatingModes.Manual)

    def open(self):
        self.device.SetOperatingState(SolenoidStatus.OperatingStates.Active)
        time.sleep(2)
        print("Shutter opened")
        
    def close(self, velocity=10.0):
        self.device.SetOperatingState(SolenoidStatus.OperatingStates.Inactive)
        time.sleep(2)
        print("Shutter closed")
            
    def off(self):
        # Stop Polling and Disconnect
        self.device.StopPolling()
        self.device.Disconnect()