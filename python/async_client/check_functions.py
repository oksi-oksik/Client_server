from PyQt5.QtWidgets import *

def check_ip(ip):
    ip = ip.split('.')
    if len(ip) != 4:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "IpAddressError_Not_4_argument",
                             "Ip-address has the form 'N1.N2.N3.N4', where 0<=Ni<=255")
        return 0
    elif ip[0].isdigit() == False or ip[1].isdigit() == False or ip[2].isdigit() == False or ip[3].isdigit() == False:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "IpAddressError_not_all_int",
                             "Ip-address has the form 'N1.N2.N3.N4', where 0<=Ni<=255")
        return 0
    elif int(ip[0]) > 255 or int(ip[1]) > 255 or int(ip[2]) > 255 or int(ip[3]) > 255:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "IpAddressError",
                             "Ip-address has the form 'N1.N2.N3.N4', where 0<=Ni<=255")
        return 0
    return 1

def check_port(port):
    if port.isdigit() == False or int(port) < 0 or int(port) > 65535:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "HostError", "Host has the form 'N', where 0<=N<=65535")
        return 0
    return 1

def check_reconnection_timeout(timeout):
    if timeout.isdigit() == False:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "ValueError", "You input in 'Reconnection timeout' not a integer number")
        return 0
    elif int(timeout) < 1 or int(timeout) > 10:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "ValueError", "You could input from 1 to 10 sec in 'Reconnection timeout'")
        return 0
    return 1

def check_request_timeout(timeout):
    if timeout.isdigit() == False:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "ValueError", "You input in 'Request timeout' not a integer number")
        return 0
    elif int(timeout) < 10 or int(timeout) > 1000:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "ValueError", "You could input from 10 to 1000 ms in 'Request timeout'")
        return 0
    return 1

def check_time_sleep(time):
    if time.isdigit() == False:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "ValueError", "You input in 'Time to sleep' not a integer number")
        return 0
    elif int(time) < 1 or int(time) > 10:
        qmsgBox = QMessageBox()
        qmsgBox.setStyleSheet("background-color: #22222e;\n"
                              "color: white")
        QMessageBox.critical(qmsgBox, "ValueError", "You could input from 1 to 10 ms in 'Time to sleep'")
        return 0
    return 1