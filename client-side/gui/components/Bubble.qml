import QtQuick 2.0

Rectangle {

    property var dynamicColor: "#222222"

    function show(text, duration, type) {
        message.text = text;
        if (typeof duration !== "undefined") { 
            time = Math.max(duration, 2 * fadeTime);
        }
        else {
            time = defaultTime;
        }
        if (type == "me") {
            dynamicColor = "#D93F3F"
        } else {
            dynamicColor = "#D93F3F"

        }
        animation.start();
    }

    property bool selfDestroying: false 

    id: root

    readonly property real defaultTime: 3000
    property real time: defaultTime
    readonly property real fadeTime: 300

    property real margin: 25

    anchors {
        right: parent.right
        margins: margin
    }

    height: message.height + margin
    radius: margin

    opacity: 0
    color: dynamicColor

    Text {
        id: message
        color: "white"
        wrapMode: Text.Wrap
        font.pointSize: 10
        font.family: "Segoe UI"
        horizontalAlignment: Text.AlignHCenter
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            margins: margin / 2
        }
    }

    SequentialAnimation on opacity {
        id: animation
        running: false

        NumberAnimation {
            to: .9
            duration: fadeTime
        }
    }
}