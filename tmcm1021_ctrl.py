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

_STEPS_PER_TURN = 200


class Motor(QObject):
    
    def __init__(self):
        QObject.__init__(self)
        self.port = None
        self.module = None
        self.motor: TMCM1021._MotorTypeA = None
        self.interface = None
        self.zero_position = 0
        self._MICROSTEP = 8
        
    
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
        self.motor.drive_settings.set_max_current(192) # 152..159 is 1.963 [A] motor current manual p. 22 (single motor 72)
        self.motor.drive_settings.set_standby_current(0)
        self.motor.drive_settings.set_microstep_resolution(self._MICROSTEP) # 0 is none 8 is 256
        self.motor.set_axis_parameter(self.motor.AP.EncoderPrescaler, 25600)
               
    @Slot()
    def move_closer(self):
        print("Moving Closer ...")
        self.motor.rotate(1000)
        
    @Slot()
    def move_further(self, direction = -1):
        print("Moving Further ...")
        self.motor.rotate(1000*direction)
    
    @Slot()
    def stop_move(self):
        self.motor.stop()
        print("Movement stoped!")

    
    def move_by(self, n_steps, dir):
        """
        Method to move on the desired axis by some margin [%] in given direction (dir).

        Args:
            active_motor (str): axis of the movement; "Biaxial", "Axis 1" or "Axis 2"
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
