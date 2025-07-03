// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import QtQuick 2.15
import QtQuick.Layouts 1.11
import QtQuick.Controls 2.1
import QtQuick.Window 2.1
import Qt.labs.platform 
import io.qt.textproperties 1.0

ApplicationWindow {
    id: root
    width: 512
    height: 512
    color: "transparent"
    title: "MagiColour"
    modality: Qt.ApplicationModal
    Component.onCompleted: {
        x = bridge.getStartX() - 256
        y = bridge.getStartY() - 256
        visible = false
    }
    visible: false
    property real hueOffset: 0.5
    flags: Qt.WA_TranslulcentBackground | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Window | Qt.SplashScreen
    Bridge {
        id: bridge
    }
    property real xOffset: width / 2 - 128
    property real yOffset: height / 2 - 128
    property real stripPos: -50
    Connections {
        target: bridge
        function onUpdatedHue(hueOffset) {
            if (!bridge.isSelected()) { 
                root.hueOffset = hueOffset;
            }
            // root.visible = true;
        }

        function onUpdatedPos(x, y) {
            // root.xOffset = root.width / 2 - 128 + x;
            if (!bridge.isSelected()) {
                root.x = bridge.getStartX() - 256 + x;
                circlePicker.x = 256 - circlePicker.radius;
            } else {
                let tempX = root.x - bridge.getStartX() + 256;
                circlePicker.x = 256 - circlePicker.radius + x - tempX;
            }
            circlePicker.y = 256 - circlePicker.radius + y;
        }
        
        function onStartedPos(x, y) {
            // console.log(x);
            root.width = 512
            root.height = 512
            root.x = bridge.getStartX() - 256;
            root.y = bridge.getStartY() - 256;
            circlePicker.x = 256 - circlePicker.radius;
            circlePicker.y = 256 - circlePicker.radius;

            if (root.y < 100) {
                root.stripPos = 256 + 50;
            } else {
                root.stripPos = -50;
            }
        }

        function onSetVisibility(visibility) {
            // console.log("change")
            root.visible = visibility
            root.width = 512
            root.height = 512
        }
    }
    TapHandler {
        dragThreshold: 1
        onGrabChanged: {
            console.log("transition");
            console.log(transition);
            switch (transition) {
                case PointerDevice.GrabPassive:
                    console.log("grabbing");
                    bridge.toggleSelect(true);
                    break;
                case PointerDevice.UngrabPassive:
                    console.log("ungrab");
                    // bridge.pickColour();
                    bridge.toggleSelect(false);
                    break;
                default:
                    break;
            }
        }
    }
    Rectangle {
        x: root.xOffset
        y: root.yOffset + root.stripPos
        id: colorStrip
        width: 256
        height: 20
        color: "red"
        ShaderEffect {
            id: effectStrip
            width: 256; height: 20
            // property variant source: sourceImage
            property real hueOffset: root.hueOffset
            // visible: root.step>3
            // NumberAnimation on hueOffset {
            //     from: 0.0; to: 1.0; loops: Animation.Infinite; duration: 4000
            // }

            fragmentShader: "HueEffect.frag.qsb"
        }
    }
    Rectangle {
        x: root.xOffset
        y: root.yOffset
        id: colorCube
        width: 256
        height: 256
        color: "red"
        ShaderEffect {
            id: effectCube
            width: 256; height: width
            // property variant source: sourceImage
            property real hueOffset: root.hueOffset
            // visible: root.step>3
            // NumberAnimation on hueOffset {
            //     from: 0.0; to: 1.0; loops: Animation.Infinite; duration: 4000
            // }

            fragmentShader: "CubeEffect.frag.qsb"
        }
    }
    Rectangle {
        x: root.xOffset + 128 - 20
        y: root.yOffset + root.stripPos - 10
        id: circleStrip
        width: 40
        height: 40
        color: "transparent"
        border.color: "white"
        border.width: 5
        radius: 20
    }
    Rectangle {
        x: 256 - circlePicker.radius
        y: 256 - circlePicker.radius
        id: circlePicker
        width: 40
        height: 40
        color: "transparent"
        border.color: "white"
        border.width: 5
        radius: 20
    }
    SystemTrayIcon {
        id: systemTray
        visible: true
        icon.source: "qrc:/assets/systray-icon.png"
        menu: Menu {
            MenuItem {
                text: qsTr("Quit")
                onTriggered: Qt.quit()
            }
        }
    }
}