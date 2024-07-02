from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QTimer
import sys
import logging
from google.protobuf.internal.encoder import _VarintBytes
from common.message_pb2 import *
from common.DelimitedMessagesStreamParser import *
from check_functions import *

class log_handler(logging.Handler):
    def __init__(self, Widget):
        super().__init__()
        self.widget = Widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class Client(QMainWindow):
    def __init__(self):
        super(Client, self).__init__()
        uic.loadUi('client.ui', self)
        self.init_UI()
        self.init_log()

        self.server = ()
        self.response = False

        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.errorOccurred.connect(self.error_handler)
        self.tcpSocket.readyRead.connect(self.reading_response)

        self.reconnectionTimer = QTimer()
        self.reconnectionTimer.setSingleShot(True)
        self.reconnectionTimer.timeout.connect(self.reconnect_to_server)

        self.requestTimer = QTimer()
        self.requestTimer.setSingleShot(True)
        self.requestTimer.timeout.connect(self.check_response)

    def init_UI(self):
        self.IPEdit.setPlaceholderText("ip-address")
        self.PortEdit.setPlaceholderText("server port")
        self.ReconnectionEdit.setPlaceholderText("reconnection timeout")
        self.RequestTimeoutEdit.setPlaceholderText("request timeout")
        self.TimeSleepEdit.setPlaceholderText("time to sleep (for slow request)")
        self.SendRequestButton.setDisabled(True)
        self.SendRequestButton.clicked.connect(self.send_request)
        self.ConnectToServerButton.clicked.connect(self.connect_to_server)
        self.plainTextEdit.setReadOnly(True)
        self.FastRequestRadioButton.toggled.connect(self.time_sleep_set_disabled)
        self.FastRequestRadioButton.setStyleSheet("QRadioButton::indicator::unchecked {background-color: white;}"
                                                  "QRadioButton::indicator::checked {background-color: #f66867;}"
                                                  "QRadioButton {color: white;}"
                                                  )
        self.SlowRequestRadioButton.toggled.connect(self.time_sleep_set_disabled)
        self.SlowRequestRadioButton.setStyleSheet("QRadioButton::indicator::unchecked {background-color: white;}"
                                                  "QRadioButton::indicator::checked {background-color: #f66867;}"
                                                  "QRadioButton {color: white;}"
                                                  )

    def init_log(self):
        logTextBox = log_handler(self.plainTextEdit)
        logTextBox.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.INFO)

    def connect_to_server(self):
        self.server = (self.IPEdit.text(), self.PortEdit.text())
        if check_ip(self.server[0]) and check_port(self.server[1]) and check_reconnection_timeout(self.ReconnectionEdit.text()):
            self.tcpSocket.connectToHost(self.server[0], int(self.server[1]))
            if self.tcpSocket.waitForConnected():
                logging.info(f"Successful connection to the server {self.server[0]} {self.server[1]}\n")
                self.ConnectToServerButton.setDisabled(True)
                self.SendRequestButton.setDisabled(False)
                return 1
        return 0


    def error_handler(self, error):
        if error == 1 and self.response:
            logging.info(f"Connection to the server {self.server[0]} {self.server[1]} is closed\n")
            self.ConnectToServerButton.setDisabled(False)
            self.SendRequestButton.setDisabled(True)
        else:
            print('else')
            logging.error(f"Error: {self.tcpSocket.errorString()}\n\nTry reconnection...\n")
            self.reconnectionTimer.start(int(self.ReconnectionEdit.text()) * 1000)


    def reconnect_to_server(self):

        # in order not to turn on the timer again when trying to connect
        self.tcpSocket.errorOccurred.disconnect(self.error_handler)

        if not self.connect_to_server():
            logging.info("Connection lost\n")
            self.tcpSocket.errorOccurred.connect(self.error_handler)
            self.ConnectToServerButton.setDisabled(False)
            self.SendRequestButton.setDisabled(True)


    def time_sleep_set_disabled(self):
        if self.SlowRequestRadioButton.isChecked():
            self.TimeSleepEdit.setDisabled(False)
            self.TimeSleepEdit.setStyleSheet("background-color: #22222e;\n"
                                             "border: 2px solid #f66867;\n"
                                             "border-radius: 25;\n"
                                             "color: white")
        if self.FastRequestRadioButton.isChecked():
            self.TimeSleepEdit.setDisabled(True)
            self.TimeSleepEdit.setStyleSheet("background-color: #22222e;\n"
                                             "border: 2px solid #f66867;\n"
                                             "border-radius: 25;\n"
                                             "color: gray")


    def send_request(self):
        if check_request_timeout(self.RequestTimeoutEdit.text()):
            if self.FastRequestRadioButton.isChecked():
                request = WrapperMessage(request_for_fast_response=RequestForFastResponse())
                timeout = int(self.RequestTimeoutEdit.text())
            elif self.SlowRequestRadioButton.isChecked():
                if check_time_sleep(self.TimeSleepEdit.text()):
                    request = WrapperMessage(request_for_slow_response=RequestForSlowResponse(time_in_seconds_to_sleep=int(self.TimeSleepEdit.text())))
                    timeout = int(self.RequestTimeoutEdit.text()) + int(self.TimeSleepEdit.text()) * 1000
                else:
                    request = None
            else:
                request = None
                qmsgBox = QMessageBox()
                qmsgBox.setStyleSheet("background-color: #22222e;\n"
                                      "color: white")
                QMessageBox.critical(qmsgBox, "ValueError", "You should choose he request to send")
            if request:
                message = _VarintBytes(request.ByteSize()) + request.SerializeToString()
                self.tcpSocket.write(message)
                self.requestTimer.start(timeout)
                self.response = False
                self.SendRequestButton.setDisabled(True)
                logging.info(f"Data sent: {request}")


    def reading_response(self):
        self.SendRequestButton.setDisabled(False)
        self.response = True
        data = bytes(self.tcpSocket.readAll())
        parser = DelimitedMessagesStreamParser(WrapperMessage)
        messages = parser.parse(data)
        if messages:
            for message in messages:
                logging.info(f"Data received: {message}")

    def check_response(self):
        if not self.response:
            self.SendRequestButton.setDisabled(True)
            logging.info("No response was received\n\nNow you can try sending a request again\n")

def application():
    app = QApplication(sys.argv)
    ui = Client()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    application()