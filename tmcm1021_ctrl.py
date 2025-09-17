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
DEFAULT_VELOCITY = 1000 # in pps

class Motor(QObject):
    
    def __init__(self):
        QObject.__init__(self)
        self.port = None
        self.module = None
        self.motor: TMCM1021._MotorTypeA = None
        self.interface = None
        self.zero_position = 0
        self._MICROSTEP = 8
        self.velocity_pps = DEFAULT_VELOCITY # default pulses per second
        
    
    def init_motor(self, axis): # normali axis (self, axisOne, axisTwo)
        COM_available = list(list_ports.comports())
        print(COM_available)
        COM_port_list = list(i.device for i in COM_available if i.serial_number == "TMCSTEP")
        for i in COM_available:
            print(i.device) 
        # if len(COM_port_list) == 1:
        #     COM_port_active = COM_port_list[0] 
        #     self.port = COM_port_active
        #     interface = UsbTmclInterface(self.port)
        #     self.module = TMCM1021(interface)
        #     self.motor = self.module.motors[axis]
        #     self.interface = interface

        self.port = "COM10"
        interface = UsbTmclInterface(self.port, datarate=9600)
        self.module = TMCM1021(interface)
        self.motor = self.module.motors[axis]
        self.interface = interface

            
    def set_motor_default(self, microstep):
       # with self.interface.connect() as interface:
        print(self.motor)
        self._MICROSTEP = microstep
        self.motor.drive_settings.set_max_current(192)
        self.motor.drive_settings.set_standby_current(0)
        self.motor.set_axis_parameter(self.motor.AP.MicrostepResolution, self._MICROSTEP) # 0 is none 8 is 256
        self.motor.set_axis_parameter(self.motor.AP.EncoderPrescaler, 25600)
               
    @Slot()
    def move_closer(self):
        print("Moving Closer ...")
        self.motor.rotate(self.velocity_pps)
        
    @Slot()
    def move_further(self, direction = -1):
        print("Moving Further ...")
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
        self.motor.move_by(n_steps*dir)
        while not(self.motor.get_position_reached()):
            time.sleep(0.01)
                
    def move_to(self, dest):
        print(f"Moving to {dest}")
    
    @Slot()
    def zero_distance(self):
        self.motor.actual_position = 0
        self.motor.set_axis_parameter(self.motor.AP.EncoderPosition, 0)
    @Slot(float)
    def set_velocity(self, velocity_vertical:float):
        velocity_vertical_mm = velocity_vertical / 1000
        print(f"Setting velocity to {velocity_vertical_mm} mm/s")
        self.velocity_pps = int(velocity_vertical_mm * STEPS_PER_TURN * self._MICROSTEP / VERTICAL_TRAVEL_PER_TURN)
        print(f"Velocity in pps: {self.velocity_pps}")
        if self.velocity_pps < 1:
            self.velocity_pps = 1
