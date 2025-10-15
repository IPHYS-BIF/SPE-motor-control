import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 2.15
import QtQuick.Dialogs
import QtCharts 2.15

ApplicationWindow{    
    id: window
    width: 500
    height: 450 
    visible: true
    title: qsTr("SPE stepper control")
    flags: Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.Dialog | Qt.WindowTitleHint
    Material.theme: Material.Dark
    Material.accent: Material.LightBlue
    
    // set variables
    property int button_width: 120
    property real currentSampleHeight: 0

    Timer {
        interval: 250; running: true; repeat: true
        onTriggered: {
            motorCtrl.send_position()
        }
    }

    ColumnLayout {
        spacing: 10
        anchors.fill: parent  
        RowLayout {
            spacing: 10
            Layout.preferredWidth: parent.width
            // Motor controls
            GroupBox {
                id: motor_ui
                title: qsTr("Move axis")

                ColumnLayout{
                    anchors.fill: parent
                    Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Button {
                        id: axis_closer
                        text: qsTr("Down")
                        onPressed: {
                            motorCtrl.move_further()
                            status_bar1.text = "Moving down ..."       
                        }
                        onReleased: {
                            motorCtrl.stop_move()
                            status_bar1.text = "Ready"
                        }
                        onCanceled: {
                            status_bar1.text = "Ready"
                            motorCtrl.stop_move()
                        }
                    }
                    
                    Button {
                        id: axis_further
                        text: qsTr("Up")
                        onPressed: {
                            motorCtrl.move_closer()
                            status_bar1.text = "Moving up..."
                        }
                        onReleased: {
                            status_bar1.text = "Ready"
                            motorCtrl.stop_move()
                        }
                        onCanceled: {
                            status_bar1.text = "Ready"
                            motorCtrl.stop_move()
                        }
                    }

                    Button {
                        id: zero_position
                        Layout.fillWidth: true
                        text: qsTr("Zero\nDistance")
                        onClicked: motorCtrl.zero_distance()
                    }

                    Button {
                        id: startDeformButton
                        Material.background: Material.color(Material.Green, Material.Shade700)
                        text: qsTr("Start deformation")
                        onClicked: motorCtrl.deform_sample()
                    }

                }
            }

            GroupBox {
                title: qsTr("Movement settings")
                
                ColumnLayout{
                    Layout.alignment: Qt.AlignTop
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                
                    ComboBox {
                            id: velocityBox
                            // model: ["0.5 µm/s", "1.0 µm/s", "2.0 µm/s", "5.0 µm/s"]
                            model: ListModel {
                                ListElement {text: "1 mm/s"; value: 1000}
                                ListElement {text: "500 µm/s"; value: 500}
                                ListElement {text: "250 µm/s"; value: 250}
                                ListElement {text: "100 µm/s"; value: 100}
                                ListElement {text: "50 µm/s"; value: 50}
                            }
                            delegate: ItemDelegate {
                                text: model.text
                                width: velocityBox.width
                            }
                            textRole: "text"
                            currentIndex: 1
                            Material.background: Material.color(Material.Blue, Material.Shade700)
                            onActivated: {
                                var velocityVertical = velocityBox.model.get(velocityBox.currentIndex).value
                                motorCtrl.set_velocity(velocityVertical)
                                status_bar1.text = "Velocity set to " + velocityBox.model.get(velocityBox.currentIndex).text
                            }
                    }

                    TextField {
                        id: heightInput
                        placeholderText: "Height (mm)"
                        validator: DoubleValidator { bottom: 0.0; decimals: 3 }
                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                        onEditingFinished: {
                            motorCtrl.set_sample_height(parseFloat(heightInput.text))
                        }
                    }

                    TextField {
                        id: deformationInput
                        placeholderText: "Deformation (%)"
                        validator: DoubleValidator { bottom: 0.0; decimals: 2 }
                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                        onEditingFinished: {
                            motorCtrl.set_sample_deformation(parseFloat(deformationInput.text))
                        }
                    }


                    Button {
                        id: stop_movement
                        Material.background: Material.color(Material.Red, Material.Shade700)
                        text: qsTr("Stop")
                        onClicked: motorCtrl.stop_move()
                    }
                }
            }
        }
        GroupBox {
            id: infoBox
            title: qsTr("Info box")
            Text {
                text: "Current distance: " + currentSampleHeight.toFixed(3) + " mm"
                color: 'white'
            }
        }
        Rectangle {
            color: "#545663"
            width: parent.width
            height: 28
            Text {
                id: status_bar1
                text: qsTr("Starting ...")
                color: "white"
                font.pointSize: 12
            }     
        }
    }

    Connections {
        target: motorCtrl
        function onActualPosition(pos) {
            currentSampleHeight = pos
        }
    }
}