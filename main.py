import sys
import os
import ctypes
from tmcm1021_ctrl import Motor
import time

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6 import QtGui

if __name__ == "__main__":
    app = QApplication([])
    
    motorCtrl = Motor()
    motorCtrl.init_motor(0)
    motorCtrl.set_motor_default(microstep=8) #velocity fullsteps per second 200 = 2mm/s (each side)
    
    time.sleep(0.1) # obcas to vyhazovalo error protoze se nestihly nainicalizovat veci v jednotlivych vlaknech, tak jsem pridal mensi sleep
    
    #show the icon in taskbar
    myappid = 'IPHYS-BIF.utense.0.5' # arbitrary string - 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    if motorCtrl.motor is None:
        msgBox = QMessageBox()
        msgBox.setText('Motor not initialized...')
        msgBox.setWindowTitle("Error")
        msgBox.exec()
        sys.exit(-1)
    else:
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty("motorCtrl", motorCtrl)
        engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))
        if not engine.rootObjects():
            sys.exit(-1)
        
        ret = app.exec()
        sys.exit(ret)

    motorCtrl = Motor()
    time.sleep(0.1)
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("motorCtrl", motorCtrl)
    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    
    ret = app.exec()
    sys.exit(ret)
