### Created on: 10-2023
from time import sleep

import logging
import time
from typing import Union, Optional, cast

logger = logging.getLogger(__name__)

try:
    import serial
except ImportError:
    logger.warning("serial was not imported.")

from NKTP_DLL import *

"""
NKT's Koheras BASIK X15 - K172-CR control
See SDK Instruction Manual page 42
"""
class NKT():
    def __init__(self, COM_PORT):
        # Open the COM port
        # Not nessesary, but would speed up the communication, since the functions does
        # not have to open and close the port on each call
        self.COM_PORT = COM_PORT
        openResult = openPorts(self.COM_PORT, 0, 0)
        print('Opening the comport:', PortResultTypes(openResult))

    def on(self):
        # Example - Turn on emission on BASIK (K1x2) by setting register 0x30 = 1
        wrResult = registerWriteU8(self.COM_PORT, 1, 0x30, 1, -1) 
        print('Turn on emission:', RegisterResultTypes(wrResult))

        print('sleeping for 4 seconds')
        sleep(4.0)

    def off(self):
        wrResult = registerWriteU8(self.COM_PORT, 1, 0x30, 0, -1) 
        print('Turn off emission:', RegisterResultTypes(wrResult))

    def get_power(self):
        rdResult = registerReadU16(self.COM_PORT, 1, 0x17, -1)
        print('Reading power:', rdResult)
        return rdResult

    # Power is in 1/100 mW (Max is 3000)
    def set_power(self, power):
        wrResult = registerWriteU16(self.COM_PORT, 1, 0x22, power, -1)
        print(f"Setting power to: {power/100} mW. Register Result Type: {RegisterResultTypes(wrResult)}")

    # Should be in 1/10 pm and read 15501200
    def get_wavelength_setpoint(self):
        rdResult = registerReadU32(self.COM_PORT, 1, 0x32, -1)
        print('Reading wavelength setpoint:', rdResult)
        return rdResult[-1]

    # Read wavelength offset
    def get_wavelength_offset(self):
        rdResult = registerReadS32(self.COM_PORT, 1, 0x72, -1)
        print('Reading wavelength offset:', rdResult)
        return rdResult[-1]

    def get_wavelength(self):
        l1 = self.get_wavelength_setpoint()[-1]
        l2 = self.get_wavelength_offset()[-1]
        l = l1 + l2
        print(f'Wavelength output: {l} in 1/10 pm')
        return l
        
    # Set wavelength offset in 1/10 pm
    def set_wavelength_offset(self, offset):
        wrResult = registerWriteS16(self.COM_PORT, 1, 0x2A, offset, -1)
        print(f'Setting wavelength offset to: {offset/10} pm. Register Result Type: {RegisterResultTypes(wrResult)}')

    # Close the Internet port
    def close(self):
        self.off()
        closeResult = closePorts(self.COM_PORT)
        print('Close the comport:', PortResultTypes(closeResult))

"""
PurePhotonics Laser
5th floor code
"""
class PPCLLaser():
    serial: "serial.Serial"  #: The serial object.

    location: str  #: The location of the device.
    baudrate: int  #: The baud rate for the serial connection.

    power: float  #: Power of the laser, in dBm.
    frequency: float  #: Frequency of the laser, in Hz.
    fine_tune_frequency: float  #: Fine tune parameter for the frequency, in Hz.

    DEFAULT_POWER: float = 18  #: Defaulf power of 6.50 dBm.
    DEFAULT_FREQUENCY: float = (
        193.41448903225806e12  #: Default frequency of 193.41 THz ~= 1550nm.
    )
    DEFAULT_FINE_TUNE: float = 0  #: Default fine tune frequency of 0 Hz.

    def __init__(self, location: str, baudrate: int = 9600) -> None:
        """Initialize the PurePhotonics laser.

        Args:
            location (str): location of the laser.
            baudrate (int, optional): baud rate of the serial communication. Defaults to 9600.
        """
        self.location = location
        self.baudrate = baudrate

        self.power = self.DEFAULT_POWER
        self.frequency = self.DEFAULT_FREQUENCY
        self.fine_tune_frequency = self.DEFAULT_FINE_TUNE

    def open(self) -> None:
        logger.info(
            "Opening laser connection with location %s and baud rate %i",
            self.location,
            self.baudrate,
        )
        self.serial = serial.Serial(port=self.location, baudrate=self.baudrate)

        self.serial.timeout = 1
        self._reset_serial()

    def _reset_serial(self):
        """
        Clean and reset serial connection.
        """
        self.serial.read_all()

        result = b""
        while len(result) == 0:
            self.serial.write(b"\x00")
            time.sleep(0.1)
            result = self.serial.read()

        time.sleep(0.1)
        result += self.serial.read_all()

    def close(self) -> None:
        logger.info("Closing serial connection with laser %s", self.location)
        self.serial.close()

    def _check(self, bytes_4: bytes, read: bool = False) -> bytes:
        """
        Check ITLA communication integrity.

        Computes the bip4 checksum defined in OIF-ITLA-MSA-01.2.
        Assumes 4 bytes as input and returns the 4 bytes with checksum.

        For a write, the result now contains the checksum.

        For a read, the result should be equal to the input, this is checked.
        Checking for error codes is also done on reads.

        Args:
            bytes_4 (bytes): the 4 input bytes.
            read (bool, optional): if read, it checks that the result is equal to the input. Defaults to False.

        Raises:
            ValueError: if bytes_4 is not of length 4.

        Returns:
            bytes: the first byte of the ITLA transaction.
        """
        if len(bytes_4) != 4:
            raise ValueError("bytes_4 should be 4 bytes.")

        # ! Extracting a byte from bytes returns an integer !
        read_write = bytes_4[0] & 0x0F
        bip8 = read_write ^ bytes_4[1] ^ bytes_4[2] ^ bytes_4[3]
        bip4 = ((bip8 & 0xF0) >> 4) ^ (bip8 & 0x0F)

        byte0 = ((bip4 << 4) | read_write).to_bytes(1, byteorder="big")

        res = byte0 + bytes_4[1:4]

        if read:
            assert res == bytes_4
            assert read_write == 4  # Extended addressing not implemented

        return res

    def _itla_transaction(self, bytes_4: bytes):
        """Send a command to ITLA.

        Args:
            bytes_4 (bytes): input bytes of length 4.

        Raises:
            TimeoutError: if no valid answer was retrieved after timeout.

        Returns:
            bytes: the response of the transaction.
        """
        self.serial.write(bytes_4)

        ret = self.serial.read(4)

        if len(ret) != 4:
            raise TimeoutError(
                f"Not enough bytes returned after {self.serial.timeout} s delay."
            )

        return ret

    def _write(
        self,
        address: Union[int, bytes],
        value: Union[int, bytes],
        checkret: bool = True,
        signed: bool = False,
    ):
        """
        Write to serial.

        Args:
            address (Union[int, bytes]): address of the register to write in.
            value (Union[int, bytes]): value to write.
            checkret (bool, optional): Check the return value. Defaults to True.
            signed (bool, optional): used if value is an integer to know if it's a signed one. Defaults to False.
        """
        if isinstance(address, int):
            address = address.to_bytes(1, byteorder="big")
        if isinstance(value, int):
            value = value.to_bytes(2, byteorder="big", signed=signed)

        bytes_4 = self._check(b"\x01" + address + value)
        ret = self._itla_transaction(bytes_4)

        if checkret:
            assert ret[1:4] == bytes_4[1:4]
            self._check(ret, read=True)

    def _read(self, address: Union[int, bytes]) -> bytes:
        """Read a value from register.

        Args:
            address (Union[int, bytes]): address of the register to read.

        Returns:
            bytes: value of the register.
        """
        if isinstance(address, int):
            address = address.to_bytes(1, byteorder="big")

        bytes_4 = self._check(b"\x00" + address + b"\x00\x00")

        ret = self._itla_transaction(bytes_4)

        self._check(ret, read=True)

        return ret[2:4]

    def _enable_laser(self):
        """
        Start emission of laser.
        """
        self._write(0x32, 0x08, checkret=False)

    def _disable_laser(self):
        """
        Stop emission of laser.
        """
        self._write(0x32, 0x00)

    def _get_status(self) -> Optional[bool]:
        """Get the current status of the laser.

        Returns:
            bool: if True, the laser is stable and if False, the laser is reaching stability.
        """
        stat = self._read(0x00)
        if stat[1] == 16:
            return False
        if stat[1] == 0:
            return True
        logger.error("Error while reading status with code: %s.", stat.hex())
        return None

    def _set_power(self, power: float):
        """Set the power of the laser.

        Args:
            power (float): Power of the laser in dBm.
        """
        self._write(0x31, int(power * 100))

    def _get_power(self) -> float:
        """Get the power outputted by the laser. Useful for wait_until_stable.

        Returns:
            float: the power in dBm.
        """
        return int.from_bytes(self._read(0x42), byteorder="big", signed=True) / 100

    def _set_whisper_mode(self):
        """
        Set the whisper mode.
        """
        self._write(0x90, 0x02, checkret=False)

    def _set_dither_mode(self):
        """
        Set the dither mode.
        """
        self._write(0x90, 0x00, checkret=False)

    def _set_nodither_mode(self):
        """
        Set the no-dither mode.
        """
        self._write(0x90, 0x01, checkret=False)

    def _wait_until_stable(self, precision=0.1, target_count=5, timeout=120):
        """Wait until the laser is stable.

        Each second, the power of the laser will be requested and compared to the target power. If the absolute value of
        the difference is less than precision, the counter is incremented by one, and if not the counter is resetted.
        When the counter goes above the target count (i.e. when the numer of continuous rounds where the actual power
        is close enough to the targete power), the function ends. If this does not happen before the timeout, a TimeoutError
        is raised.

        Args:
            precision (float, optional): the precision required between the current power and target power. Defaults to 0.1.
            target_count (int, optional): the number of continuous rounds the difference should be below the precision. Defaults to 5.
            timeout (int, optional): timeout in seconds. Defaults to 120.

        Raises:
            TimeoutError: if the laser failed to reach stability after the timeout.
        """
        count = 0
        logger.info("Waiting for laser status to be stable.")
        while count < target_count:
            power = self._get_power()
            logger.debug(
                "Power was measured at %f (target power %f)", power, self.power
            )
            if abs(power - self.power) < precision:
                logger.debug(
                    "Increasing count by 1 for stability (%d/%d)", count, target_count
                )
                count += 1
            else:
                logger.debug("Resetting count to 0")
                count = 0
            timeout -= 1
            if timeout == 0:
                raise TimeoutError("Laser failed to reach stability.")
            time.sleep(1)
        logger.info("Laser reached stability.")

    def _set_frequency(self, frequency: float):
        """Set the frequency of the laser.

        Args:
            frequency (float): Frequency of the laser in Hz.
        """
        self._write(0x35, int(frequency * 1e-12), checkret=False)
        self._write(
            0x36,
            int((frequency * 1e-12 - int(frequency * 1e-12)) * 10000),
            checkret=False,
        )

    def _set_fine_freqency(self, frequency: float):
        """Set the fine tune frequency of the laser.

        Args:
            frequency (float): Fine tine frequency in Hz.
        """
        self._write(0x62, int(frequency * 1e-6), checkret=False, signed=True)

    def set_parameters(self, **kwargs) -> None:
        """
        Set the parameters of the laser.

        To set the frequency, you can either give the frequency in Hz, or the wavelength in m.
        If the wavelength is given, it will be converted to a frequency with nu = c/lambda.
        If both are given, the value of the frequency is used.

        To set the fine tune frequency, you can either give the fine_tune_frequency in Hz or the
        fine_tune_wavelength in m. If the fine_tune_wavelength is given, it will be converted to a
        frequency with nu = c/lambda. If both are given, the value of fine_tune_frequency is used.

        If a parameter is not given, the default value if used.

        Args:
            power (float, optional): Power of the laser in dBm. Defaults to 6.50.
            frequency (float, optional): Frequency of the laser in Hz. Defaults to ~193.41e12.
            wavelength (float, optional): Wavelength of the laser in m. If frequency and wavelength are both given, frequency is used. Defaults to ~1550e-9.
            fine_tune_frequency (float, optional): Fine tune frequency of the laser in Hz. Defaults to 0.
            fine_tune_wavelength (float, optional): Fine tune wavelength of the laser in m. If fine_tune_frequency and fine_tune_wavelength are both given, fine_tune_frequency is used. Defaults to 0m.
        """
        if "wavelength" in kwargs:
            wavelength = kwargs.get("wavelength")
            assert wavelength is not None and wavelength != 0
            self.frequency = SPEED_OF_LIGHT / wavelength

        if "frequency" in kwargs:
            if "wavelength" in kwargs:
                logger.warning(
                    "Both frequency and wavelength were given. Using the value of the frequency."
                )
            frequency = kwargs.get("frequency")
            assert frequency is not None
            self.frequency = cast(float, frequency)

        if "wavelength" not in kwargs and "frequency" not in kwargs:
            self.frequency = self.DEFAULT_FREQUENCY
            logger.warning(
                "wavelength and frequency were not given. Using default value of %f THz (%f nm)",
                self.frequency * 1e-12,
                SPEED_OF_LIGHT / self.frequency * 1e-9,
            )

        if "power" in kwargs:
            power = kwargs.get("power")
            assert power is not None
            self.power = cast(float, power)
        else:
            self.power = self.DEFAULT_POWER
            logger.warning(
                "power was not given. Using default value of %f dBm", self.power
            )
        if "fine_tune_wavelength" in kwargs:
            fine_tune_wavelength = kwargs.get("fine_tune_wavelength")
            assert fine_tune_wavelength is not None and fine_tune_wavelength != 0
            self.fine_tune_frequency = SPEED_OF_LIGHT / fine_tune_wavelength

        if "fine_tune_frequency" in kwargs:
            if "fine_tune_wavelength" in kwargs:
                logger.warning(
                    "Both fine_tune_frequency and fine_tune_wavelength were given. Using the value of fine_tune_frequency."
                )
            fine_tune_frequency = kwargs.get("fine_tune_frequency")
            assert fine_tune_frequency is not None
            fine_tune_frequency = cast(float, fine_tune_frequency)
            self.fine_tune_frequency = fine_tune_frequency

        if "fine_tune_frequency" not in kwargs and "fine_tune_wavelength" not in kwargs:
            self.fine_tune_frequency = self.DEFAULT_FINE_TUNE
            logger.warning(
                "fine_tine and fine_tune_wavelength were not given. Using default value of %f MHz",
                self.fine_tune_frequency * 1e-6,
            )

    def enable(self) -> None:
        logger.info(
            "Enabling laser with power %f dBm, frequency %f THz (%f nm) and fine tune frequency %f MHz",
            self.power,
            self.frequency * 1e-12,
            SPEED_OF_LIGHT / self.frequency * 1e-9,
            self.fine_tune_frequency * 1e-6,
        )
        # Set dither mode
        self._set_dither_mode()

        # Set the parameters
        self._set_power(self.power)
        self._set_frequency(self.frequency)
        self._set_fine_freqency(self.fine_tune_frequency)

        # Enable the laser
        self._enable_laser()

        # Wait until it's stable
        self._wait_until_stable()

        # Set whisper mode
        self._set_whisper_mode()

    def disable(self) -> None:
        logger.info("Disabling laser.")
        self._disable_laser()



