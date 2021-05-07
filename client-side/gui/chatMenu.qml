
import "components"
import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import QtQuick.Timeline 1.0

Window {
    id: chatMenu
    width: 380
    height: 580
    visible: true
    color: "#00000000"
    title: "Menu chat"

    // Remove Title Bar
    flags: Qt.SplashScreen | Qt.FramelessWindowHint

    // Internal Functions
    ToastManager {
        id:toast
    }

    Rectangle {
        id: bg
        x: 78
        y: 131
        width: 360
        height: 560
        color: "#201A30"
        radius: 15
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        z: 1


        Rectangle {
            id: dragArea
            x: 0
            y: 0
            width: 360
            height: 26
            color: "#00000000"
            border.color: "#00000000"
            MouseArea {
                anchors.fill: parent
                property variant clickPos: "1,1"
                onPressed: {
                    clickPos  = Qt.point(mouse.x,mouse.y)
                }

                onPositionChanged: {
                    var delta = Qt.point(mouse.x-clickPos.x, mouse.y-clickPos.y)
                    chatMenu.x += delta.x;
                    chatMenu.y += delta.y;
                }
            }
        }


        CustomButton {
            id: btnClose
            x: 325
            y: 5
            width: 30
            height: 30
            opacity: 1
            text: "X"
            anchors.right: parent.right
            anchors.top: parent.top
            z: 3
            anchors.topMargin: 15
            anchors.rightMargin: 15
            colorPressed: "#bc2626"
            font.family: "Segoe UI"
            colorMouseOver: "#dc4e4e"
            colorDefault: "#d93f3f"
            font.pointSize: 10
            onClicked: { backend.closeChat(true); chatMenu.close(); }
        }

        Label {
            id: roomName
            x: 10
            y: 10
            opacity: 1
            color: "#ffffff"
            text: "Undifined"
            anchors.left: parent.left
            anchors.top: parent.top
            z: 3
            anchors.leftMargin: 20
            font.bold: true
            font.italic: false
            anchors.topMargin: 14
            font.family: "Segoe UI"
            font.pointSize: 16
        }

        RoundedRect {
            id: roundedRect
            width: 360
            height: 57
            radius: 15
            topRightCorner: true
            bottomRightCorner: false
            z: 0
        }


        RoundedRect {
            id: roundedRect1
            x: 0
            y: 503
            width: 360
            height: 57
            radius: 15
            topLeftCorner: false
            bottomLeftCorner: true
            z: 0
            bottomRightCorner: true
            topRightCorner: false

            CustomTextField {
                id: chatField
                x: 20
                y: 12
                width: 323
                height: 34
                opacity: 1
                anchors.verticalCenter: parent.verticalCenter
                z: 2
                anchors.topMargin: 10
                placeholderText: "Messages.."
                Keys.onReturnPressed: {
                    backend.getInputMsg(chatField.text);
                    chatField.text = "";
                }
            }
        }

        FocusScope {
            id: focusScope
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: roundedRect.bottom
            anchors.bottom: roundedRect1.top
            anchors.rightMargin: 10
            anchors.leftMargin: 10
            anchors.bottomMargin: 0
            anchors.topMargin: 0

            BubbleManager {
                id: bubbleManager
            }
        }
    }

    DropShadow{
        anchors.fill: bg
        source: bg
        verticalOffset: 0
        horizontalOffset: 0
        radius: 10
        color: "#40000000"
        z: 0
    }

    Connections {
        target: backend

        function onAddChat(chat, username, isme){
            bubbleManager.show(chat)
        }

        function onSetRoom(room){
            roomName.text = room;
        }
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:1.66}D{i:10}
}
##^##*/
