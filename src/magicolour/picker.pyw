"""Module providing a function printing python version."""
# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path
from time import sleep
import colorsys
import pyautogui

from PySide6.QtCore import QObject, Signal, Slot, QTimer, QPoint
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

from pynput import keyboard, mouse
import pywinctl
from ahk import AHK

import yaml


ahk = AHK(executable_path="C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe")

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1

with open('config.yml', 'a') as file:
    pass
# import our config
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

if not config:
    config = {}

REFRESH_RATE = config.get("refresh_rate", 60.0)
COLOUR_REFRESH_RATE = config.get("colour_refresh_rate", 10.0)
WINDOW_DELAY = config.get("window_delay", 0.08)
HOTKEY = config.get("hotkey", "/")
WATCH_COLOUR_ON_START = config.get("watch_colour_on_start", False)
WATCHED_PIXEL_X = config.get("watched_pixel_x", 0)
WATCHED_PIXEL_Y = config.get("watched_pixel_y", 0)

running_config = {
    "refresh_rate": REFRESH_RATE,
    "colour_refresh_rate": COLOUR_REFRESH_RATE,
    "window_delay": WINDOW_DELAY,
    "hotkey": HOTKEY,
    "watched_pixel_x": WATCHED_PIXEL_X,
    "watched_pixel_y": WATCHED_PIXEL_Y
}

if not config.get("watch_colour_on_start"):
    running_config["watch_colour_on_start"] = True
else:
    running_config["watch_colour_on_start"] = WATCH_COLOUR_ON_START


def save_config(config):
    with open('config.yml', 'w') as file:
        yaml.dump(config, file)

save_config(running_config)

def on_click(x, y, button, pressed, injected):
    if Bridge.instance.isSelectingWatchedPixel:
        if pressed:
            Bridge.instance.setWatchedPixel()
            Bridge.instance.isSelectingWatchedPixel = False

def on_press(key, injected):
    try:
        if not Bridge.instance.hotkeyReady:
            return
        if (key == keyboard.KeyCode.from_char(HOTKEY) and
            (pywinctl.getActiveWindowTitle() == "CLIP STUDIO PAINT")):
            Bridge.instance.windowToggle(True)
            Bridge.instance.hotkeyReady = False
    except AttributeError:
        pass

def on_release(key, injected):
    try:
        if key == keyboard.KeyCode.from_char(HOTKEY):
            Bridge.instance.hotkeyReady = True
            if Bridge.instance.isSelecting:
                sleep(0.01)
                ahk.send_input('{LButton up}')
                # Bridge.instance.selectToggle(False)
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
    startedOffset = Signal(int, int)
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
        # self.cursor = QCursor()

        self.watchedPixel = (WATCHED_PIXEL_X, WATCHED_PIXEL_Y)
        self.curColour = (1.0, 1.0, 1.0)
        self.isSelectingWatchedPixel = False
        self.isWatchingPixel = WATCH_COLOUR_ON_START
        
        # Event Loop
        self.timer = QTimer()
        self.timer.setInterval(1000 / REFRESH_RATE)  # msecs 100 = 1/10th sec
        self.timer.timeout.connect(self.updateVariables)
        self.timer.start()

        self.colourTimer = QTimer()
        self.colourTimer.setInterval(1000 / COLOUR_REFRESH_RATE)  # msecs 100 = 1/10th sec
        self.colourTimer.timeout.connect(self.updateWatchedColour)
        self.colourTimer.start()

    # Event Loop
    # pylint: disable-next=invalid-name
    def updateWatchedColour(self):
        if not (pywinctl.getActiveWindowTitle() == "CLIP STUDIO PAINT"):
            return
        if not self.isWatchingPixel:
            return
        if self.visible:
            return
        self.getWatchedColour()

    def updateVariables(self):
        if self.readyToPick:
            self.readyToPick = False
            self.settingValues = True
            self.getColour()
            sleep(WINDOW_DELAY)
            self.settingValues = False
            self.windowToggle(False)
            return
        
        if not self.settingValues:
            curMousePos = pyautogui.position()
            mouseHueOffset = (curMousePos.x - self.mousePos.x) / 256
            
            # if self.isWatchingPixel:
            h,s,v = self.getHSV()
            hueOffset = h + mouseHueOffset
            
            self.updatedHue.emit(hueOffset)
            self.updatedPos.emit(curMousePos.x - self.mousePos.x, curMousePos.y - self.mousePos.y)

    def getHSV(self):
        r, g, b = self.curColour
        return colorsys.rgb_to_hsv(r, g, b)

    def transformFloatToInt(self, value):
        return int(value * 256) - 128

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
    
    @Slot(result=QPoint)
    # pylint: disable-next=invalid-name
    def getCursorPos(self):
        return QCursor.pos()
    
    @Slot(QPoint)
    # pylint: disable-next=invalid-name
    def setCursorPos(self, point):
        # print(QCursor.pos())
        return QCursor.setPos(point)
    
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
        if not value:
            self.visible = False
            self.pickColour()
        self.isSelecting = value

    # pylint: disable-next=invalid-name
    def getColour(self):
        temp_pos = ahk.mouse_position
        csp_window = ahk.find_window(title='CLIP STUDIO PAINT')
        csp_window.send('^+x')
        ahk.send_input('{LButton up}')
        ahk.mouse_position = temp_pos
        ahk.send_input('{LButton down}')
        ahk.send_input('{LButton up}')
    
    # pylint: disable-next=invalid-name
    def windowToggle(self, value):
        if value:
            self.setVisibility.emit(True)
            sleep(0.004)
            self.mousePos = pyautogui.position()
            h, s, v = self.getHSV()
            self.startedOffset.emit(self.transformFloatToInt(s), self.transformFloatToInt(v))
            self.startedPos.emit(self.mousePos.x, self.mousePos.y)
            self.visible = True
            
            self.isSelecting = False
        else:
            self.setVisibility.emit(False)
            self.visible = False
            self.isSelecting = False
    
    @Slot()
    def startWatchPixel(self):
        self.isSelectingWatchedPixel = True

    @Slot()
    def stopWatchPixel(self):
        self.isWatchingPixel = False

    def setWatchedPixel(self):
        x, y = pyautogui.position()
        self.watchedPixel = (x, y)
        self.isWatchingPixel = True
        running_config["watched_pixel_x"] = x
        running_config["watched_pixel_y"] = y
        save_config(running_config)

    def getWatchedColour(self):
        
        r,g,b = pyautogui.pixel(self.watchedPixel[0], self.watchedPixel[1])
        self.curColour = (float(r) / 256, float(g) / 256, float(b) / 256)

# pylint: enable=invalid-name

def start():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    engine.addImportPath("qrc:///resources/qml")
    engine.loadFromModule("MagiColour", "ColourCube")
    if not engine.rootObjects():
        sys.exit(-1)
    
    mouse_listener = mouse.Listener(
        on_click=on_click
    )
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    keyboard_listener.start()

    exit_code = app.exec()
    
    del engine
    sys.exit(exit_code)
