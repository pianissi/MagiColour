"""Module providing a function printing python version."""
# This Python file uses the following encoding: utf-8
import sys
import math
from pathlib import Path
from time import sleep

import pyautogui

from PySide6.QtCore import QObject, Signal, Slot, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

from pynput import keyboard
import pywinctl
from ahk import AHK

import rc_style


ahk = AHK(executable_path="C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe")

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1

REFRESH_RATE = 60.0
HOTKEY = "/"

def on_press(key, injected):
    try:
        if not Bridge.instance.hotkeyReady:
            return
        if (key == keyboard.KeyCode.from_char(HOTKEY) and 
            (pywinctl.getActiveWindowTitle() == "CLIP STUDIO PAINT")):
            Bridge.instance.windowToggle(True)
    except AttributeError:
        pass

def on_release(key, injected):
    try:
        if key == keyboard.KeyCode.from_char(HOTKEY):
            Bridge.instance.hotkeyReady = True
            if Bridge.instance.isSelecting:
                Bridge.instance.selectToggle(True)
                return
            Bridge.instance.windowToggle(False)
    except AttributeError:
        pass
# pylint: disable=invalid-name
@QmlElement
class Bridge(QObject):
    updatedHue = Signal(float, arguments=['hueOffset'])
    updatedPos = Signal(int, int, arguments=['x', 'y'])

    startedPos = Signal(int, int)
    setVisibility = Signal(bool)

    instance = None

    def __init__(self):
        super().__init__()
        Bridge.instance = self
        self.mousePos = pyautogui.position()
        self.isSelecting = False

        self.settingValues = False

        self.visible = False
        self.readyToPick = False
        self.hotkeyReady = True
        
        # Event Loop
        self.timer = QTimer()
        self.timer.setInterval(1000 / REFRESH_RATE)  # msecs 100 = 1/10th sec
        self.timer.timeout.connect(self.updateVariables)
        self.timer.start()

    # Event Loop
    # pylint: disable-next=invalid-name
    def updateVariables(self):
        if self.readyToPick:
            self.readyToPick = False
            self.settingValues = True
            self.getColour()
            sleep(0.10)
            self.settingValues = False
            self.setVisibility.emit(False)
            return
        
        if not self.settingValues:
            hueOffset = max(0, min(1, math.modf(pyautogui.position().x / 256)[0]))
            curMousePos = pyautogui.position()
            self.updatedHue.emit(hueOffset)
            self.updatedPos.emit(curMousePos.x - self.mousePos.x, curMousePos.y - self.mousePos.y)
        
    @Slot(result=float)
    # pylint: disable-next=invalid-name
    def getHueOffset(self):
        return max(0, min(1, (pyautogui.position().x / 1000)))
    
    @Slot(result=int)
    # pylint: disable-next=invalid-name
    def getStartX(self):
        return self.mousePos.x
    
    @Slot(result=int)
    # pylint: disable-next=invalid-name
    def getStartY(self):
        return self.mousePos.y
    
    @Slot(result=bool)
    # pylint: disable-next=invalid-name
    def isSelected(self):
        return self.isSelecting
    
    @Slot(bool)
    # pylint: disable-next=invalid-name
    def toggleSelect(self, value):
        self.selectToggle(value)
    
    @Slot()
    # pylint: disable-next=invalid-name
    def pickColour(self):
        if self.isSelecting:
            self.readyToPick = True

    # pylint: disable-next=invalid-name
    def selectToggle(self, value):
        if self.visible and not value:
            self.visible = False
            self.pickColour()
        self.isSelecting = value

    # pylint: disable-next=invalid-name
    def getColour(self):
        csp_window = ahk.find_window(title='CLIP STUDIO PAINT')
        csp_window.send('^+x')
        ahk.send_input('{LButton up}')
        ahk.send_input('{LButton down}')
        ahk.send_input('{LButton up}')
    
    # pylint: disable-next=invalid-name
    def windowToggle(self, value):
        if value:
            self.setVisibility.emit(True)
            sleep(0.004)
            self.mousePos = pyautogui.position()
            self.startedPos.emit(self.mousePos.x, self.mousePos.y)
            self.visible = True
            self.hotkeyReady = False
            self.isSelecting = False
        else:
            self.setVisibility.emit(False)
            self.visible = False
            self.isSelecting = False

# pylint: enable=invalid-name

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).resolve().parent / "main.qml"

    engine.addImportPath(Path(__file__).resolve().parent)
    engine.loadFromModule("App", "Main")
    if not engine.rootObjects():
        sys.exit(-1)
    
    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    keyboard_listener.start()

    exit_code = app.exec()
    
    del engine
    sys.exit(exit_code)
