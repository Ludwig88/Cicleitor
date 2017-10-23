#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4.Qt import QMutex

import time, serial
from DatosIndependientes import DatosCompartidos

"""########################################################## CLASE PARA Recepcion"""

class LECTURA(QtCore.QThread):
    def __init__(self, filaPlot, Datos,
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
        #print "Initing Puerto desde Proceso Puerto"
        self.signal = QtCore.SIGNAL("signal")
        self.CONTENEDORplot = filaPlot
        self.Datos = Datos

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        por_setear = corrSet = celdaSet = celda = None
        finalizo = False
        try:
            if self.serial_port:
                self.serial_port.close()
            self.serial_port = serial.Serial(**self.serial_arg)
        except serial.SerialException:
            print "error en el try del serial port"
            return

        while self.serial_port.is_open:
            try:
                recepcion = self.RecibirPS() + '#' + str(time.time() - 1500000000)
            except:
                recepcion = "$#$#$#$"
            separado = recepcion.split('#', 4)
            # [char(celda), string(tension), string(corriente), string(tiempo)]
            """variables para guardado"""
            if separado[0] != '$' or separado[1] != '$' or separado[2] != '$':
                celda = separado[0]
                #print "[PORT]" + str(celda) + " is activa? " + str(self.Datos.xIsActive(str(celda)))
                #print "[PORT] a is activa? " + str(self.Datos.xIsActive("a"))
                # print "[PORT] a " + str(type(self.Datos.a)) + " id " +str(id(self.Datos.a))
                # print "[PORT] b " + str(type(self.Datos.b)) + " id " +str(id(self.Datos.b))
                # print "[PORT] c " + str(type(self.Datos.c)) + " id " +str(id(self.Datos.c))
                # print "[PORT] b CG " + str(self.Datos.xGetCondGuardado(5))
                # print "[PORT] b CG " + str(self.Datos.xGetCondGuardado(2))
                """chequeo que sea una de las que active, descarto los envios nulos"""
                self.mutex.lock()
                a = self.Datos.xIsActive(celda)
                print "[PORT]" + str(celda) + " is activa? " + str(self.Datos.xIsActive(str(celda)))
                self.mutex.unlock()
                if a is True:
                    """conversion de tension (pasa a mV)"""
                    #(-1)*int((int(separado[1])*(3.0/8))-6144)
                    Tension = int((int(separado[1]) * (0.375)) - 6144)
                    """conversion de corriente (pasa a uA)"""
                    Corriente = int(separado[2]) - 1024
                    Tiempo = float(separado[3])
                    self.Datos.xActualizoCampo(celda, Tension, Corriente, Tiempo)
                    Barrido, tiempo = self.Datos.xGetBarrYTiempo(celda)
                    ###################################################################PromPlot += [Tension, Corriente, tiempo],
                    self.CONTENEDORplot.append([celda, Barrido, Tension, Corriente, tiempo])
                    # if celda == str(myapp.ui.cmbCelPlot.currentText()) and Tension != '%':
                    #     # print 'tiempo ' +str(tiempo) +' tension ' +str(Tension)
                    #     self.emit(self.signal, str(Barrido), str(Tension), str(Corriente), str(tiempo))
            """Hay celdas por setear"""
            if self.Datos.enColaPorEnviar() >= 1:
                celdaSet, corrSet = self.Datos.xGetPorSetear(celda)
                print "Proceso puerto " + str(celdaSet) + "  " + str(corrSet)
                self.EnviarPS_I(corrSet, False, str(celdaSet))
                if self.Datos.xEnviarPS(celdaSet, 2):
                    print "Send - ok"
                else:
                    print "retry Send??"
            """Ninguna activa"""
            # if self.Datos.AllDisable():
            #     print "cortando loop de lectura"
            #     break

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
            print "[PORT] "+ str(s)
            return s
        else:
            return '$#$#$'
