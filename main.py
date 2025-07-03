# This Python file uses the following encoding: utf-8
import sys, os
from pathlib import Path
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtQml import *
from PySide6.QtQuickControls2 import QQuickStyle
import pyautogui
import math
from pynput import mouse, keyboard
from time import sleep
import pywinctl
import rc_style
from ahk import AHK

ahk = AHK(executable_path="C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe")

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1
# cspWindow = pyautogui.getWindowsWithTitle("CLIP STUDIO PAINT")[0]
cspWindow = ahk.find_window(title='CLIP STUDIO PAINT')
visible = False
readyToPick = False
hotkeyReady = True


hotkey = "/"

def select_toggle(value):
    global visible
    print("toggl")
    print(value)
    print(visible)
    if visible and not value:
        visible = False
        pickColour()
        # Bridge.instance.isSelecting = value
        
    Bridge.instance.isSelecting = value
    
    

def on_click(x, y, button, pressed, injected):
    pass
    # global visible
    # global readyToPick
    # # print("clicked")
    # if readyToPick:
    #     return
    # if button != mouse.Button.left:
    #     return 
    # if injected:
    #     print("injected!")
    #     return
    # if (not pressed) and visible:
    #     pass
    #     # Bridge.instance.isSelecting = pressed
    #     # visible = False
    #     # readyToPick = True
    
    # select_toggle(pressed)

def on_press(key, injected):
    global visible
    global hotkeyReady
    try:
        # print('alphanumeric key {} pressed; it was {}'.format(
        #     key.char, 'faked' if injected else 'not faked'))
        if not hotkeyReady:
            return
        if key == keyboard.KeyCode.from_char(hotkey) and (pywinctl.getActiveWindowTitle() == "CLIP STUDIO PAINT"):
            Bridge.instance.setVisibility.emit(True)
            sleep(0.004)
            Bridge.instance.mousePos = pyautogui.position()
            Bridge.instance.startedPos.emit(Bridge.instance.mousePos.x, Bridge.instance.mousePos.y)
            visible = True
            print("visible")
            hotkeyReady = False
            Bridge.instance.isSelecting = False
            # magiWindow = pyautogui.getWindowsWithTitle("MagiColour")[0]
            # magiWindow.activate()
            
        # if key == keyboard.KeyCode.from_char(']'):
        #     global readyToPick
        #     readyToPick = True
    except AttributeError:
        print('special key {} pressed'.format(
            key))

def on_release(key, injected):
    global visible
    global hotkeyReady
    try:
        # print('alphanumeric key {} pressed; it was {}'.format(
        #     key.char, 'faked' if injected else 'not faked'))
        if key == keyboard.KeyCode.from_char(hotkey):
            hotkeyReady = True
            if Bridge.instance.isSelecting:
                visible = False
                pickColour()
                return
            Bridge.instance.setVisibility.emit(False)
            visible = False
            
    except AttributeError:
        print('special key {} pressed'.format(
            key))
        
def pickColour():
    if Bridge.instance.isSelecting:
        global readyToPick
        readyToPick = True

def getColour():
    # pass
    # pyautogui.PAUSE = 0.1
    # curPos = pyautogui.position()

    curPos = ahk.mouse_position
    # cspWindow.activate()

    cspWindow.send('^+x')
    # sleep(0.1)
    ahk.send_input('{LButton up}')
    ahk.send_input('{LButton down}')
    ahk.send_input('{LButton up}')
    # ahk.click(curPos[0], curPos[1], click_count=2)
    # sleep(0.10)
    print("i'm printing")
    # pyautogui.PAUSE = 0.05
    # pyautogui.hotkey('ctrl', 'shift', 'x')
    print("printed")
    # magiWindow.activate()
    # pyautogui.click(curPos.x, curPos.y, clicks=2)
    # cspWindow.activate()
    print("after")



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
        # Define timer.
        self.isSelecting = False

        self.settingValues = False
        
        
        print(self.mousePos)
        self.timer = QTimer()
        self.timer.setInterval(16)  # msecs 100 = 1/10th sec
        self.timer.timeout.connect(self.updateVariables)
        self.timer.start()

        # self.setVisibility.emit(True);
        # setup mouse

    def updateVariables(self):
        global readyToPick
        if readyToPick:
            readyToPick = False
            self.settingValues = True
            getColour()
            sleep(0.10)
            self.settingValues = False
            self.setVisibility.emit(False)
            return
        
        
        if not self.settingValues:
            hueOffset = max(0, min(1, math.modf(pyautogui.position().x / 256)[0]))
            curMousePos = pyautogui.position()
            self.updatedHue.emit(hueOffset)
            self.updatedPos.emit(curMousePos.x - self.mousePos.x, curMousePos.y - self.mousePos.y)
                # print(pywinctl.getActiveWindowTitle())
                # self.startedPos.emit(self.mousePos.x, self.mousePos.y)
        


    @Slot(result=float)
    def getHueOffset(self):
        return max(0, min(1, (pyautogui.position().x / 1000)))
    
    @Slot(result=int)
    def getStartX(self):
        return self.mousePos.x
    
    @Slot(result=int)
    def getStartY(self):
        return self.mousePos.y
    
    @Slot(result=bool)
    def isSelected(self):
        return self.isSelecting
    
    @Slot(bool)
    def toggleSelect(self, value):
        select_toggle(value)
    
    @Slot()
    def pickColour(self):
        pickColour()


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    # QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()
    qml_file = Path(__file__).resolve().parent / "main.qml"
    # engine.load(qml_file)
    # Add the current directory to the import paths and load the main module.

    engine.addImportPath(Path(__file__).resolve().parent)
    engine.loadFromModule("App", "Main")
    if not engine.rootObjects():
        sys.exit(-1)

    mouseListener = mouse.Listener(
        on_click=on_click)
    mouseListener.start()
    
    keyboardListener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    keyboardListener.start()

    exit_code = app.exec()
    
    
    
    del engine
    sys.exit(exit_code)
