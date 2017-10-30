#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4.Qt import QMutex
from collections import deque # double ended queue
import time, serial

"""########################################################## CLASE PARA Recepcion"""

class LECTURA(QtCore.QThread):
    def __init__(self, dequePLOT, dequeIN, dequeOUT,
                 port_num = '/dev/ttyACM0',
                 port_baud = 115200,
                 port_stopbits = serial.STOPBITS_ONE,
                 port_parity = serial.PARITY_NONE,
                 port_timeout = 0.1,
                 parent = None):

        QtCore.QThread.__init__(self)

        self.daemon = True
        self.mutex = QMutex()

        self.serial_port = None
        self.serial_arg = dict(port=port_num,
                               baudrate=port_baud,
                               stopbits=port_stopbits,
                               parity=port_parity,
                               timeout=port_timeout)
        self.signal = QtCore.SIGNAL("signal")
        self.CONTENEDORplot = dequePLOT
        self.dequeIN = dequeIN
        self.dequeOUT = dequeOUT

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        try:
            if self.serial_port:
                self.serial_port.close()
            self.serial_port = serial.Serial(**self.serial_arg)
        except serial.SerialException:
            print "error en el try del serial port"
            return

        while self.serial_port.is_open:
            time.sleep(0.01)
            try:
                recepcion = self.RecibirPS() + '#' + str(time.time() - 1500000000)
            except:
                recepcion = "$#$#$#$"
            separado = recepcion.split('#', 4)
            # [char(celda), string(tension), string(corriente), string(tiempo)]
            """variables para guardado"""
            if separado[0] != '$' or separado[1] != '$' or separado[2] != '$':
                celda = separado[0]
                """conversion de tension (pasa a mV)"""
                Tension = int((int(separado[1]) * (0.375)) - 6144)
                #(-1)*int((int(separado[1])*(3.0/8))-6144)
                """conversion de corriente (pasa a uA)"""
                Corriente = int(separado[2]) - 1024
                Tiempo = float(separado[3])
                #Append en la deque de salida
                #print "[PORT|" + str(celda) + "]  append Corriente: " + str(Corriente) + " Tiempo: "+str(Tiempo)
                self.mutex.lock()
                self.dequeOUT.append(["RAW", celda, Tension, Corriente, Tiempo])
                self.mutex.unlock()
            if int(len(self.dequeIN)) > 0:
                [mensaje, celda, Tension, Corriente, Tiempo] = self.dequeIN.pop()
                """Hay celdas por setear"""
                if 112 >= ord(celda) >= 97:
                    print "[PORT|" + str(celda) + "]  " + str(Corriente)
                    self.EnviarPS_I(Corriente, False, str(celda))
                    #podría hacer un append de OK
                """Ninguna activa"""
                if mensaje is "END":
                     print "cortando loop de lectura"
                     break

        # clean up
        if self.serial_port:
            self.serial_port.close()

    def EnviarPS_I(self, ua, Descarga, celda):
        print "celda a enviar " + str(celda) +" len es: " + str(len(celda))
        self.serial_port.write_timeout = 0.1
        #print "out waiting " + str(self.serial_port.out_waiting)
        """si uso el time out de escritura meter un try catch"""
        #print "settings " + str(self.serial_port.get_settings())
        try:
            #bytes escritos
            print self.serial_port.write(celda)
            time.sleep(0.25)
            print "Envio OK"
            self.serial_port.flushOutput()
        #time.sleep(0.25)
        except serial.SerialTimeoutException:
            print "timeOut de envio Serie"
        # I=0 con uA=0 en cualquier descarga
        # 2 unidades = 1uA 2048 =0A
        # global ser
        # print ser
        # print 'ua: ' + str(ua) +' ' +str(type(ua)) + 'Descarga: ' + str(Descarga) +' '
        # + str(type(Descarga)) +'Celda: '  + str(celda) +' ' + str(type(celda))
        # MatConv=[['h',2],['f',2],['d',2],['b',2],['h',1],
        #         ['f',1],['d',1],['b',1],['e',2],['g',2],['a',2],
        #         ['c',2],['e',1],['g',1],['a',1],['c',1]]
        # cada renglon es el orden en asccii, dentro la primer columna es el caracter dentro del dac cuyo numero es la otra
        # letra a enviar MatConv[NumDeCelda(str(celda))][0]
        # numero a enviar MatConv[NumDeCelda(str(celda))][1]
        # if Descarga :
        # num=int(2048-(ua*2))
        # else :
        # num=int((ua*2)+2048)
        # num = ua
        # print 'numero a enviar__: ' +str(num)
        # if num>=0 and num<=4095:
        # mil=num/1000
        # cien=(num-mil*1000)/100
        # die=(num-mil*1000-cien*100)/10
        # un=(num-mil*1000-cien*100-die*10)
        ##print(str(mil)+' '+str(cien)+' '+str(die)+' '+str(un))
        ##inicio
        # ser.write('i')
        ##time.sleep(0.25)
        # ser.write(str(mil)) #1
        ##time.sleep(0.25)
        # ser.write(str(cien)) #2
        ##time.sleep(0.25)
        # ser.write(str(die)) #3
        ##time.sleep(0.25)
        # ser.write(str(un)) #4
        ##time.sleep(0.25)
        # ser.write(str(MatConv[NumDeCelda(str(celda))][0]))
        ##time.sleep(0.25)
        # ser.write(str(MatConv[NumDeCelda(str(celda))][1]))
        ##time.sleep(0.25)
        # ser.write('f')
        ##time.sleep(0.25)
        # ser.flushInput()
        # else:
        # print 'numero incorrecto'

    def RecibirPS(self):
        s = self.serial_port.readline()
        #print 'Limpio: "' + str(s) #+ '"' + "len es: " + str(len(s))
        # print 's-1' + s[len(s)-1]
        # print 'Cortado: "' + s +'"'
        if len(s) == 13:
            s = s[:len(s) - 1]
            #print "[PORT] "+ str(s)
            return s
        else:
            return '$#$#$'
