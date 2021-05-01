import QtQuick 2.0

ListView {
    function show(text, duration) {
        model.insert(0, {text: text, duration: duration});
    }

    id: root

    z: Infinity
    spacing: 5
    anchors.fill: parent
    anchors.bottomMargin: 20
    verticalLayoutDirection: ListView.ToptoBottom

    interactive: false

    displaced: Transition {
        NumberAnimation {
            properties: "y"
            easing.type: Easing.InOutQuad
        }
    }
    
    delegate: Toast {
        Component.onCompleted: {
            if (typeof duration === "undefined") {
                show(text);
            }
            else {
                show(text, duration);
            }
        }
    }

    model: ListModel {id: model}
}