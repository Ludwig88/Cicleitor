#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore

import time, string, serial

from DatosIndependientes import DatosCompartidos

"""########################################################## CLASE PARA Recepcion"""


class LECTURA(QtCore.QThread):
    def __init__(self, fila, filaPlot, datos,
                 port_num='/dev/ttyACM0',
                 port_baud=115200,
                 port_stopbits=serial.STOPBITS_ONE,
                 port_parity=serial.PARITY_NONE,
                 port_timeout=0.01,
                 parent=None):

        QtCore.QThread.__init__(self)

        self.serial_port = None
        self.serial_arg = dict(port=port_num,
                               baudrate=port_baud,
                               stopbits=port_stopbits,
                               parity=port_parity,
                               timeout=port_timeout)

        self.signal = QtCore.SIGNAL("signal")
        self.CONTENEDOR = fila
        self.CONTENEDORplot = filaPlot
        self.DatosComp = datos

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        try:
            if self.serial_port:
                self.serial_port.close()
            self.serial_port = serial.Serial(**self.serial_arg)
        except serial.SerialException, e:
            #self.error_q.put(e.message)
            print "error en el try del serial port"
            return

        while self.serial_port.is_open:
            recepcion = self.RecibirPS() + '#' + str(time.time() - 1400000000)
            # print recepcion
            separado = recepcion.split('#', 4)
            # [char(celda), string(tension), string(corriente), string(tiempo)]
            """variables para guardado"""
            if separado[0] != '$' or separado[1] != '$' or separado[2] != '$':
                celda = separado[0]
                """chequeo que sea una de las que active, descarto los envios nulos"""
                # verifico q sea una celda seteada
                if self.DatosComp.IsSeted(celda):
                    """primera recepcion de esa celda"""
                    if CondPaBarrer[renglon][1] == 0:
                        CondPaBarrer[renglon][2] = float(separado[3])  # guardo tiempo de inicio de ciclado
                        CondPaBarrer[renglon][1] = 1
                    """el tiempo de inicio mas real """
                    if CondPaBarrer[renglon][2] == -1:
                        CondPaBarrer[renglon][1] += 1
                        CondPaBarrer[renglon][2] = float(separado[3])
                    """variables de esa entrada"""
                    Tension = int((int(separado[1]) * (0.375)) - 6144)
                    # (-1)*int((int(separado[1])*(3.0/8))-6144)
                    #  conversion de tension (pasa a mV)
                    inicio = CondPaBarrer[renglon][2]
                    Corriente = int(separado[2]) - 1024
                    # conversion de corriente (pasa a uA)
                    Tiempo = float(separado[3])
                    """variables de extremo"""
                    Barridos = CondSeteo[renglon][1]
                    V_lim_sup = CondSeteo[renglon][2]
                    V_lim_inf = CondSeteo[renglon][3]
                    T_Max = CondSeteo[renglon][4]
                    """condiciones de cambio"""
                    if Tension >= V_lim_sup or Tension <= V_lim_inf or Tiempo > inicio + T_Max:
                        """supere barridos maximos:"""
                        if CondPaBarrer[renglon][1] + 1 > Barridos:
                            # ENVIO
                            self.EnviarPS_I(0, False, celda)
                            Tension = Corriente = '%'  # caracter de final
                            # [celda, barrido (actual), Tinicio]
                            CondPaBarrer[renglon][1] = CondPaBarrer[renglon][2] = 0
                            # reinicio condiciones de seteo
                            self.ActualizoMatriz(celda, 0, 0, 0, 0, 0)
                        else:
                            """guardo con barrido adicional"""
                            # CondPaBarrer[renglon][1] += 1 tambien lo tengo que sumar en la prox medida
                            # float(separado[3]) #pongo -1 asi en la proxima recepcion pone 0
                            CondPaBarrer[renglon][2] = -1
                            # ENVIO si Barrido par descargo, si no cargo le sumo uno para poder reconocer el cambio en ese punto
                            BARRIDO = CondPaBarrer[renglon][1] + 1
                            if BARRIDO % 2 == 0:
                                Descarga = True
                            else:
                                Descarga = False
                            CORRIENTE = CondSeteo[renglon][5]  # corriente seteada
                            print 'enviando I=' + str(CORRIENTE) + ' Descarga? ' + \
                                  str(Descarga) + ' celda:' + str(celda)
                            self.EnviarPS_I(CORRIENTE, Descarga, celda)
                    """caso mas tipico"""
                    Barrido = CondPaBarrer[renglon][1]
                    if Barrido % 2 == 0:
                        Barrido = Barrido / 2
                    else:
                        Barrido = int(Barrido / 2) + 1
                    # CondPaBarrer[renglon][2] #tiempo en ese barrido
                    tiempo = Tiempo - inicio
                    self.CONTENEDOR.append([celda, Barrido, Tension, Corriente, tiempo])

                    #PromPlot += [Tension, Corriente, tiempo],
                    self.CONTENEDORplot.append([celda, Barrido, Tension, Corriente, tiempo])

                    # if celda == str(myapp.ui.cmbCelPlot.currentText()) and Tension != '%':
                    #     # print 'tiempo ' +str(tiempo) +' tension ' +str(Tension)
                    #     self.emit(self.signal, str(Barrido), str(Tension), str(Corriente), str(tiempo))
            """Hay celdas por setear"""
            PorSetear = None
            if PorSetear is not None:
                renglon = self.NumDeCelda(PorSetear)
                Corriente = CondSeteo[renglon][5]
                self.EnviarPS_I(Corriente, False, str(PorSetear))
                PorSetear = None
            """Ninguna activa"""
            FIN = 0
            if FIN:
                print 'cortando loop de lectura '
                break

        # clean up
        if self.serial_port:
            self.serial_port.close()

    def NumDeCelda(self, celda):
        for i in range(len(string.ascii_letters)):
            if celda == string.ascii_letters[i]:
                return i
                break

    def ActualizoMatriz(self, celda, barridos, VLS, VLI, TMax, Corriente):
        global CondSeteo
        for i in range(len(string.ascii_letters)):
            if celda == string.ascii_letters[i]:
                CondSeteo[i][1] = barridos
                CondSeteo[i][2] = VLS
                CondSeteo[i][3] = VLI
                CondSeteo[i][4] = TMax
                CondSeteo[i][5] = Corriente
                break

    def EnviarPS_I(self, ua, Descarga, celda):
        print str(celda)
        self.serial_port.write(str(celda))
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
        print 'Limpio: "' + str(s) + '"' + "len es: " + str(len(s))
        # print 's-1' + s[len(s)-1]
        # print 'Cortado: "' + s +'"'
        if len(s) == 13:
            s = s[:len(s) - 1]
            return s
        else:
            return '$#$#$'
