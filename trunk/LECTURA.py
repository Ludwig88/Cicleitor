#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore

import time
import Ciclador

"""########################################################## CLASE PARA Recepcion"""


class LECTURA(QtCore.QThread):
    def __init__(self, fila, filaPlot, parent=None):
        QtCore.QThread.__init__(self)
        self.signal = QtCore.SIGNAL("signal")
        self.CONTENEDOR = fila
        self.CONTENEDORplot = filaPlot

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        global FIN
        global PorSetear
        global CondSeteo
        global CondPaBarrer
        CondPaBarrer = [['a', 0, 0], ['b', 0, 0],
                        ['c', 0, 0], ['d', 0, 0],
                        ['e', 0, 0], ['f', 0, 0],
                        ['g', 0, 0], ['h', 0, 0],
                        ['i', 0, 0], ['j', 0, 0],
                        ['k', 0, 0], ['l', 0, 0],
                        ['m', 0, 0], ['n', 0, 0],
                        ['o', 0, 0], ['p', 0, 0]]
        #         [celda, barrido (actual), Tinicio]
        global PromPlot
        PromPlot = []
        while True:
            recepcion = RecibirPS() + '#' + str(time.time() - 1400000000)
            print recepcion
            separado = recepcion.split('#',
                                       4)  # devuelve lista de lineas = caracter q separa, lineas a hacer (elementos en q separar -1)
            #                       [char(celda), string(tension), string(corriente), string(tiempo)]
            """variables para guardado"""
            if separado[0] != '$' or separado[1] != '$' or separado[2] != '$':
                celda = separado[0]
                renglon = int(NumDeCelda(celda))
                """chequeo que sea una de las que active, descarto los envios nulos"""  # verifico q sea una celda seteada
                if CondSeteo[renglon][4] != 0:
                    """primera recepcion de esa celda"""
                    if CondPaBarrer[renglon][1] == 0:
                        CondPaBarrer[renglon][2] = float(separado[3])  # guardo tiempo de inicio de ciclado
                        CondPaBarrer[renglon][1] = 1
                    """el tiempo de inicio mas real """
                    if CondPaBarrer[renglon][2] == -1:
                        CondPaBarrer[renglon][1] += 1
                        CondPaBarrer[renglon][2] = float(separado[3])  ###############################3
                    """variables de esa entrada"""
                    Tension = int((int(separado[1]) * (
                    0.375)) - 6144)  # (-1)*int((int(separado[1])*(3.0/8))-6144)    # conversion de tension (pasa a mV)
                    inicio = CondPaBarrer[renglon][2]
                    Corriente = int(separado[2]) - 1024  # conversion de corriente (pasa a uA)
                    Tiempo = float(separado[3])
                    """variables de extremo"""
                    Barridos = CondSeteo[renglon][1]
                    V_lim_sup = CondSeteo[renglon][2]
                    V_lim_inf = CondSeteo[renglon][3]
                    T_Max = CondSeteo[renglon][4]
                    """condiciones de cambio"""
                    if (Tension >= V_lim_sup or Tension <= V_lim_inf or Tiempo > inicio + T_Max):
                        """supere barridos maximos:"""
                        if CondPaBarrer[renglon][1] + 1 > Barridos:
                            # ENVIO
                            EnviarPS_I(0, False, celda)
                            Tension = Corriente = '%'  # caracter de final
                            CondPaBarrer[renglon][1] = CondPaBarrer[renglon][
                                2] = 0  # [celda, barrido (actual), Tinicio]
                            ActualizoMatriz(celda, 0, 0, 0, 0, 0)  # reinicio condiciones de seteo
                        else:
                            """guardo con barrido adicional"""
                            # CondPaBarrer[renglon][1] += 1 tambien lo tengo que sumar en la prox medida
                            CondPaBarrer[renglon][
                                2] = -1  # float(separado[3]) #pongo -1 asi en la proxima recepcion pone 0

                            # ENVIO si Barrido par descargo, si no cargo le sumo uno para poder reconocer el cambio en ese punto
                            BARRIDO = CondPaBarrer[renglon][1] + 1
                            if BARRIDO % 2 == 0:
                                Descarga = True
                            else:
                                Descarga = False
                            CORRIENTE = CondSeteo[renglon][5]  # corriente seteada
                            print 'enviando I=' + str(CORRIENTE) + ' Descarga? ' + str(Descarga) + ' celda:' + str(
                                celda)
                            EnviarPS_I(CORRIENTE, Descarga, celda)
                    """caso mas tipico"""
                    Barrido = CondPaBarrer[renglon][1]
                    if Barrido % 2 == 0:
                        Barrido = Barrido / 2
                    else:
                        Barrido = int(Barrido / 2) + 1
                    tiempo = Tiempo - inicio  # CondPaBarrer[renglon][2] #tiempo en ese barrido
                    self.CONTENEDOR.append([celda, Barrido, Tension, Corriente, tiempo])

                    PromPlot += [Tension, Corriente, tiempo],
                    self.CONTENEDORplot.append([celda, Barrido, Tension, Corriente, tiempo])
                    # if len(PromPlot)==5:
                    # Tension = Corriente = Tiempo = 0.0
                    # for i in range(len(PromPlot)):
                    # Tension += PromPlot[i][0]
                    # Corriente += PromPlot[i][1]
                    # Tiempo += PromPlot[i][2]
                    # Tension = Tension / len(PromPlot)
                    # Corriente = Corriente / len(PromPlot)
                    # Tiempo = Tiempo / len(PromPlot)
                    # self.CONTENEDORplot.append([celda , Barrido , Tension , Corriente , tiempo])
                    # PromPlot=[]

                    if celda == str(myapp.ui.cmbCelPlot.currentText()) and Tension != '%':
                        # print 'tiempo ' +str(tiempo) +' tension ' +str(Tension)
                        self.emit(self.signal, str(Barrido), str(Tension), str(Corriente), str(tiempo))

                    """Hay celdas por setear"""
            if PorSetear != None:
                #
                renglon = NumDeCelda(PorSetear)
                Corriente = CondSeteo[renglon][5]
                EnviarPS_I(Corriente, False, str(PorSetear))
                PorSetear = None
            """Ninguna activa"""
            if FIN:
                print 'cortando loop de lectura '
                break

