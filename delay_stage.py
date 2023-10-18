### Created on: 05-09-2023
### Author: Laura Martins

import numpy as np

import time
import clr

# Add References to .NET libraries
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.KCube.BrushlessMotorCLI.dll.")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.Benchtop.StepperMotorCLI.dll")


from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.BrushlessMotorCLI import *
from Thorlabs.MotionControl.Benchtop.StepperMotorCLI import *
from System import Decimal

# We define the serial numbers corresponding to Linear Translation Stage
SERIAL_NO = "40381974"

class Delay:
    def __init__(self):
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()

        self.serial_no = SERIAL_NO
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