import serial
import time
import csv

port_num = '/dev/ttyACM0',
port_baud = 115200,
port_stopbits = serial.STOPBITS_ONE,
port_parity = serial.PARITY_NONE,
port_timeout = 0.1,

while serial_port.is_open:
    time.sleep(0.01)
    flagSend = False
    try:
        recepcion = self.RecibirPS() + '#' + str(time.time() - 1500000000)
    except:
        recepcion = "$#$#$#$"
