# Created on 10/2023

import os
import time
import sys
import clr

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.SolenoidCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.SolenoidCLI import *
from System import Decimal  # necessary for real world units

# We define the serial numbers corresponding to Linear Translation Stage
SERIAL_NO = "68800559"

class Shutter:
    def __init__(self):
        # Build device list so that the library can find yours
        DeviceManagerCLI.BuildDeviceList()

        self.serial_no = SERIAL_NO
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