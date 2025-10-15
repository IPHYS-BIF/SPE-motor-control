from pytrinamic.connections import ConnectionManager
from pytrinamic.connections.usb_tmcl_interface import UsbTmclInterface
from pytrinamic.modules import TMCM1021
import threading
import sys
import serial
from serial.tools import list_ports
import glob
import time
from pathlib import Path

from PySide6.QtCore import Qt, QObject, Slot, Signal, Property
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo

STEPS_PER_TURN = 200
VERTICAL_TRAVEL_PER_TURN = 6 # in mm
DEFAULT_VELOCITY = 500   # in um/s

class Motor(QObject):
    actualPosition = Signal(float)
    
    def __init__(self):
        QObject.__init__(self)
        self.port = None
        self.module = None
        self.motor: TMCM1021._MotorTypeA = None
        self.interface = None
        self.zero_position = 0
        self._MICROSTEP = 8
        self.velocity_pps = 4000
        
    
    def init_motor(self, axis): # normali axis (self, axisOne, axisTwo)
        # COM_available = list_ports.comports()
        # COM_port_list = list(i.serial_number for i in COM_available)
        # self.port = "COM10"
        ports = list_ports.comports()
        for port in ports:
            if 'CH340' in port.description:
                self.port = port.device
        interface = UsbTmclInterface(self.port, datarate=9600)
        self.module = TMCM1021(interface)
        self.motor = self.module.motors[axis]
        self.interface = interface
        self.set_velocity(DEFAULT_VELOCITY) # default pulses per second

            
    def set_motor_default(self, microstep):
       # with self.interface.connect() as interface:
        print(self.motor)
        self._MICROSTEP = microstep
        self.motor.drive_settings.set_max_current(192)
        self.motor.drive_settings.set_standby_current(0)
        self.motor.set_axis_parameter(self.motor.AP.MicrostepResolution, self._MICROSTEP) # 0 is none 8 is 256
        self.motor.set_axis_parameter(self.motor.AP.EncoderPrescaler, 25600)
               
    @Slot()
    def move_further(self):
        print("Moving down ...")
        self.motor.rotate(self.velocity_pps)
        
    @Slot()
    def move_closer(self, direction = -1):
        print("Moving up ...")
        self.motor.rotate(self.velocity_pps*direction)
    
    @Slot()
    def stop_move(self):
        self.motor.stop()
        print("Movement stoped!")

    
    def move_by(self, n_steps, dir):
        """
        Method to move by some margin [%] in given direction (dir).

        Args:
            n_steps (int): number of steps that the motor should perform
            dir (int): direction of the movement, it either closes or opens; values={-1;1}
        
        Returns:
            None
        """
        print("Moving Closer by margin {}".format(n_steps))
        self.motor.move_by(n_steps*dir, self.velocity_pps)
        while not(self.motor.get_position_reached()):
            time.sleep(0.01)
                
    def move_to(self, dest):
        print(f"Moving to {dest}")
    
    @Slot()
    def zero_distance(self):
        self.motor.actual_position = 0
        self.motor.set_axis_parameter(self.motor.AP.EncoderPosition, 0)

    @Slot(float)
    def set_velocity(self, velocity_vertical: float):
        velocity_vertical_mm = velocity_vertical / 1000
        self.velocity_pps = int(velocity_vertical_mm * STEPS_PER_TURN * 2**self._MICROSTEP / VERTICAL_TRAVEL_PER_TURN)
        if self.velocity_pps < 1:
            self.velocity_pps = 1

    @Slot(float)
    def set_sample_height(self, height: float):
        self.sample_height = height

    @Slot(float)
    def set_sample_deformation(self, deformation: float):
        self.sample_deformation = deformation

    @Slot()
    def send_position(self):
        encoder_pos = toSigned32(self.motor.get_axis_parameter(self.motor.AP.EncoderPosition))
        vertical_pos = VERTICAL_TRAVEL_PER_TURN * encoder_pos / (STEPS_PER_TURN * 2**self._MICROSTEP)
        self.actualPosition.emit(vertical_pos)

    @Slot()
    def deform_sample(self):
        x = self.sample_height * self.sample_deformation / 100
        steps = int(x * STEPS_PER_TURN * 2**self._MICROSTEP / VERTICAL_TRAVEL_PER_TURN)
        self.move_by(steps, -1)

def toSigned32(n: int) -> int:
    n = n & 0xffffffff
    return (n ^ 0x80000000) - 0x80000000
