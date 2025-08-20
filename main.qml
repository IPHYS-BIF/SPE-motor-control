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
    height: 320 
    visible: true
    title: qsTr("SPE stepper control")
    flags: Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.Dialog | Qt.WindowTitleHint
    Material.theme: Material.Dark
    Material.accent: Material.LightBlue
    
    // set variables
    property int button_width: 120

    ColumnLayout {
        spacing: 10
        anchors.fill: parent  
        RowLayout {
            anchors.fill: parent
            spacing: 20
            
            // Motor controls
            GroupBox {
                id: motor_ui
                title: qsTr("Move axis")
                Layout.preferredWidth: parent.width * 0.3
                Layout.fillHeight: true

                ColumnLayout{
                    anchors.fill: parent
                    spacing: 10
                    Button {
                        id: axis_closer
                        Layout.fillWidth: true
                        text: qsTr("Closer")
                        onPressed: {
                            motorCtrl.move_closer()
                            status_bar1.text = "Moving closer ..."       
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
                        Layout.fillWidth: true
                        text: qsTr("Further")
                        onPressed: {
                            motorCtrl.move_further()
                            status_bar1.text = "Moving further..."
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

                }
            }

            GroupBox {
                title: qsTr("Movement settings")
                Layout.preferredWidth: parent * 0.3
                Layout.fillHeight: true
                
                ColumnLayout{
                    anchors.fill: parent
                    spacing: 10

                    ComboBox {
                            id: velocityBox
                            Layout.fillWidth: true
                            model: ["0.5 m/s", "1.0 m/s", "2.0 m/s", "5.0 m/s"]
                            currentIndex: 1
                            Material.background: Material.color(Material.Blue, Material.Shade700)
                        }

                        TextField {
                            id: heightInput
                            Layout.fillWidth: true
                            placeholderText: "Height (mm)"
                            validator: DoubleValidator { bottom: 0.0; decimals: 2 }
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                        }

                        TextField {
                            id: deformationInput
                            Layout.fillWidth: true
                            placeholderText: "Deformation (mm)"
                            validator: DoubleValidator { bottom: 0.0; decimals: 2 }
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                        }

                    Button {
                        id: stop_experiment
                        Layout.fillWidth: true
                        Material.background: Material.color(Material.Red, Material.Shade700)
                        text: qsTr("Stop")
                        onClicked: motorCtrl.stop_move()
                    }
                }
            }
        }
        Rectangle {
            color: "#545663"
            width: parent.width
            height: 28
            Text {
                id: status_bar1
                anchors.left: parent.left
                anchors.leftMargin: 5
                text: qsTr("Starting ...")
                color: "white"
                font.pointSize: 12
            }     
        }
    }
}