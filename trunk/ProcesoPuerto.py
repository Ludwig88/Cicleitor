#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'debug/LogProcesoPuerto.txt')
log = open(filename, "w")
#print("error en el try del serial port",file=log)

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
            print("error en el try del serial port",file=log)
            return

        while self.serial_port.is_open:
            time.sleep(0.00001) #puede llegar a necesitar estar mas alto
            flagSend = False
            try:
                recepcion = self.RecibirPS() + '#' + str(time.time() - 1500000000)
            except:
                recepcion = "$#$#$#$"
            separado = recepcion.split('#', 4)
            # [char(celda), string(tension), string(corriente), string(tiempo)]
            """variables para guardado"""

            if separado[0].startswith("ok"):
                self.mutex.lock()
                self.dequeOUT.append(["OK!", celda, None, Corriente, None])
                self.mutex.unlock()
            elif separado[0] != '$' or separado[1] != '$' or separado[2] != '$' or len(separado) !=4 :
                try:
                    celda = separado[0]
                except:
                    celda = "x"
                """conversion de tension (pasa a mV)"""
                try:
                    Tension = int((int(separado[1]) * (0.375)) - 6144)
                except:
                    Tension = "NAN"
                #(-1)*int((int(separado[1])*(3.0/8))-6144)
                """conversion de corriente (pasa a uA)"""
                try:
                    Corriente = int(separado[2]) - 1024
                except:
                    Corriente = "NAN"
                try:
                    Tiempo = float(separado[3])
                except:
                    Tiempo = "NAN"
                #Append en la deque de salida
                if celda != "x" and Tension != "NAN" and Corriente != "NAN" and Tiempo != "NAN":
                    self.mutex.lock()
                    self.dequeOUT.append(["RAW", celda, Tension, Corriente, Tiempo])
                    self.mutex.unlock()

            if int(len(self.dequeIN)) > 0:
                self.mutex.lock()
                [mensaje, celda, Corriente] = self.dequeIN.pop()
                #print "mensaje y demas " + str([mensaje, celda, Corriente])
                self.mutex.unlock()
                """Ninguna activa"""
                if mensaje is "END":
                     print("[PORT] cortando loop de lectura",file=log)
                     break
                """Hay celdas por setear"""
                if 112 >= ord(celda) >= 97:
                    if mensaje == "SETI":
                        print("[PORT|" + str(celda) + "] SETI arrived with " + str(Corriente),file=log)
                        self.EnviarPS_I(Corriente, celda)

        # clean up
        if self.serial_port:
            self.serial_port.close()

    def EnviarPS_I(self, ua, celda):
        print("[PORT|send] celda a enviar " + str(celda) +" len es: " + str(len(celda)),file=log)
        self.serial_port.write_timeout = 0.1
        #print "out waiting " + str(self.serial_port.out_waiting)
        """si uso el time out de escritura meter un try catch"""
        #print "settings " + str(self.serial_port.get_settings())
        try:
            #bytes escritos
            print(self.serial_port.write(celda),file=log)
            time.sleep(0.25)
            #print "[PORT|send] Envio OK"
            self.serial_port.flushOutput()
            print("[PORT|send] "+str(self.serial_port.write(celda)),file=log)
            self.serial_port.flushOutput()
            #time.sleep(0.25)
        except serial.SerialTimeoutException:
            print("[PORT|send] timeOut de envio Serie",file=log)
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
        elif len(s) <= 4:
            s = s[:len(s) - 1]
            return s
        else:
            return '$#$#$'

