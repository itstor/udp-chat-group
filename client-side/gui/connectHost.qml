
import "components"
import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import QtQuick.Timeline 1.0

Window {
    id: connectHost
    width: 380
    height: 580
    visible: true
    color: "#00000000"
    title: qsTr("Connect to Host")

    flags: Qt.FramelessWindowHint

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
                    connectHost.x += delta.x;
                    connectHost.y += delta.y;
                }
            }
        }

        Label {
            id: appTitle
            x: 55
            y: 10
            opacity: 1
            color: "#ffffff"
            text: qsTr("Hi, Anon!")
            anchors.top: parent.top
            font.italic: false
            anchors.topMargin: 20
            anchors.horizontalCenterOffset: 0
            font.family: "Segoe UI"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 16
        }

        Image {
            id: logoImage
            x: 55
            width: 300
            height: 120
            opacity: 1
            anchors.top: appTitle.bottom
            source: "./images/logo.png"
            anchors.topMargin: 40
            anchors.horizontalCenter: parent.horizontalCenter
            fillMode: Image.PreserveAspectFit
        }


        CustomTextField {
            id: textHost
            x: 30
            width: 168
            height: 40
            opacity: 1
            anchors.right: textPort.left
            anchors.top: label1.bottom
            anchors.rightMargin: 6
            anchors.topMargin: 19
            placeholderText: "IP Address"
        }

        CustomTextField {
            id: textPort
            x: 204
            y: 310
            width: 126
            height: 40
            opacity: 1
            placeholderText: "Port"
        }

        CustomTextField {
            id: textUsername
            opacity: 1
            anchors.top: textHost.bottom
            anchors.topMargin: 10
            anchors.horizontalCenterOffset: 0
            placeholderText: "Username"
            anchors.horizontalCenter: parent.horizontalCenter
        }

        CustomTextField {
            id: textRoom
            opacity: 1
            anchors.top: textUsername.bottom
            anchors.topMargin: 10
            anchors.horizontalCenterOffset: 0
            placeholderText: "Room"
            anchors.horizontalCenter: parent.horizontalCenter
        }

        CustomButton {
            id: btnLogin
            x: 30
            width: 300
            height: 40
            opacity: 1
            text: "Join"
            anchors.top: textRoom.bottom
            anchors.topMargin: 22
            font.pointSize: 10
            font.family: "Segoe UI"
            colorPressed: "#16b195"
            colorMouseOver: "#5ef7db"
            colorDefault: "#0Df5E3"
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: backend.getInputData(textHost.text, textPort.text,  textUsername.text, textRoom.text)
        }

        Label {
            id: label1
            x: 55
            opacity: 1
            color: "#ffffff"
            text: qsTr("Connect using IP Address and Port")
            anchors.top: label.bottom
            anchors.topMargin: 10
            anchors.horizontalCenterOffset: 0
            font.family: "Segoe UI"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pointSize: 10
        }

        Label {
            id: label
            x: 100
            opacity: 1
            color: "#ffffff"
            text: qsTr("Connect to Host")
            anchors.top: logoImage.bottom
            anchors.horizontalCenterOffset: 0
            anchors.topMargin: 24
            font.family: "Segoe UI"
            font.pointSize: 16
            anchors.horizontalCenter: parent.horizontalCenter
        }

        CustomButton {
            id: btnClose
            x: 20
            width: 30
            height: 30
            opacity: 1
            text: "X"
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 15
            anchors.rightMargin: 15
            colorPressed: "#bc2626"
            font.family: "Segoe UI"
            colorMouseOver: "#dc4e4e"
            colorDefault: "#d93f3f"
            font.pointSize: 10
            onClicked: connectHost.close()
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

    Timeline {
        id: timeline
        animations: [
            TimelineAnimation {
                id: timelineAnimation
                duration: 1150
                running: true
                loops: 1
                to: 1150
                from: 0
            }
        ]
        enabled: true
        startFrame: 0
        endFrame: 3000

        KeyframeGroup {
            target: logoImage
            property: "opacity"
            Keyframe {
                frame: 0
                value: 0
            }

            Keyframe {
                frame: 499
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: label
            property: "opacity"
            Keyframe {
                frame: 98
                value: 0
            }

            Keyframe {
                frame: 595
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: label1
            property: "opacity"
            Keyframe {
                frame: 195
                value: 0
            }

            Keyframe {
                frame: 703
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: textHost
            property: "opacity"
            Keyframe {
                frame: 296
                value: 0
            }

            Keyframe {
                frame: 851
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: textPort
            property: "opacity"
            Keyframe {
                frame: 296
                value: 0
            }

            Keyframe {
                frame: 851
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: textUsername
            property: "opacity"
            Keyframe {
                frame: 389
                value: 0
            }

            Keyframe {
                frame: 995
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: textRoom
            property: "opacity"
            Keyframe {
                frame: 497
                value: 0
            }

            Keyframe {
                frame: 1150
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }

        KeyframeGroup {
            target: btnLogin
            property: "opacity"
            Keyframe {
                frame: 497
                value: 0
            }

            Keyframe {
                frame: 1150
                value: 1
            }

            Keyframe {
                frame: 0
                value: 0
            }
        }
    }

    Connections {
        target: backend

        function onShowToast(msg){
            toast.show(msg, 5000)
        }

        function onMoveChat(ismove){
            if (ismove === true){
                var component = Qt.createComponent("chatMenu.qml")
                var chat = component.createObject()
                chat.show()
                visible = false
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:1.33}
}
##^##*/
