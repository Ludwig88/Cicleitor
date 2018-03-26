# global CondSeteo
# global CondGuardado
# global CondPaBarrer
# CondGuardado = [['a', False, 0.0], ['b', False, 0.0], ['c', False, 0.0], ['d', False, 0.0], ['e', False, 0.0],
#                 ['f', False, 0.0], ['g', False, 0.0], ['h', False, 0.0], ['i', False, 0.0], ['j', False, 0.0],
#                 ['k', False, 0.0], ['l', False, 0.0], ['m', False, 0.0], ['n', False, 0.0], ['o', False, 0.0],
#                 ['p', False, 0.0]]
# #            [celda, Activa?, Promediado]
# CondSeteo = [['a', 0, 0, 0, 0, 0], ['b', 0, 0, 0, 0, 0], ['c', 0, 0, 0, 0, 0], ['d', 0, 0, 0, 0, 0],
#              ['e', 0, 0, 0, 0, 0], ['f', 0, 0, 0, 0, 0], ['g', 0, 0, 0, 0, 0], ['h', 0, 0, 0, 0, 0],
#              ['i', 0, 0, 0, 0, 0], ['j', 0, 0, 0, 0, 0], ['k', 0, 0, 0, 0, 0], ['l', 0, 0, 0, 0, 0],
#              ['m', 0, 0, 0, 0, 0], ['n', 0, 0, 0, 0, 0], ['o', 0, 0, 0, 0, 0], ['p', 0, 0, 0, 0, 0]]
# # [celda, barr, vli, vls, tmax, corr]
# CondPaBarrer = [['a', 0, 0], ['b', 0, 0],
#                 ['c', 0, 0], ['d', 0, 0],
#                 ['e', 0, 0], ['f', 0, 0],
#                 ['g', 0, 0], ['h', 0, 0],
#                 ['i', 0, 0], ['j', 0, 0],
#                 ['k', 0, 0], ['l', 0, 0],
#                 ['m', 0, 0], ['n', 0, 0],
#                 ['o', 0, 0], ['p', 0, 0]]
#         [celda, barrido (actual), Tinicio]
# asas
# nombre = ''
# activa = False
# promediado = 0.0
# barridoActual = 0
# voltajeLimInferior = 0
# voltajeLimSuperior = 0
# corriente = 0
# tiempoMaxBarrido = 0

from __future__ import print_function

import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'debug/Log.txt')
log = open(filename, "a+")

import csv
from PyQt4 import QtCore
from PyQt4.QtCore import QTimer
from PyQt4.Qt import QMutex
from collections import deque
from DatosIndividualesCelda import DatosCelda
import ProcesoPuerto
import datetime, time


class DatosCompartidos(QtCore.QThread):

    class Modos:
        inactiva, ciclando, voc = range(3)
    PoolThread = []
    celdasAenviar = []
    hayAlgo = 0
    #timerOkRececpcion = QTimer()

    def __init__(self, dequeSettings, dequePLOT, parent = None):
        print("["+str(datetime.datetime.now())+"][DCOMP] initing", file=log)
        self.a = DatosCelda("a")
        self.b = DatosCelda("b") #2
        self.c = DatosCelda("c") #3
        self.d = DatosCelda("d") #4
        self.e = DatosCelda("e") #5
        self.f = DatosCelda("f") #6
        self.g = DatosCelda("g") #7
        self.h = DatosCelda("h") #8
        self.i = DatosCelda("i") #9
        self.j = DatosCelda("j") #10
        self.k = DatosCelda("k") #11
        self.l = DatosCelda("l") #12
        self.m = DatosCelda("m") #13
        self.n = DatosCelda("n") #14
        self.o = DatosCelda("o") #15
        self.p = DatosCelda("p") #16

        QtCore.QThread.__init__(self)
        self.mutex = QMutex()
        self.daemon = True

        self.signal = QtCore.SIGNAL("realTimeData")
        self.signalSingleShot = QtCore.SIGNAL("UIConditions")
        self.celdaEnTiempoReal = None
        self.celdaCondUI = None
        self.celdaPLOTTR = None

        """DEQUES de comunicacion"""
        self.dequeSettings = dequeSettings #desde UI
        self.dequePLOT = dequePLOT  #hacia UI??
        self.dequeOUT = deque(maxlen=16000) #seteos de celdas a puerto
        self.dequeIN = deque(maxlen=16000) #desde puerto crudo
        """"""
        #print( "arranco thread de lectura desde DatosIndependientes", file=log)
        self.PoolThread.append(ProcesoPuerto.LECTURA(self.dequePLOT, self.dequeOUT, self.dequeIN))
        #self.PoolThread[len(self.PoolThread) - 1].start()

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        self.PoolThread[len(self.PoolThread) - 1].start()
        while True:
            time.sleep(0.001)
            #proceso desde UI hacia puerto
            if int(len(self.dequeSettings)) >= 1:
                try:
                    self.mutex.lock()
                    [mensaje, Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga] = self.dequeSettings.pop()
                    self.mutex.unlock()
                except IndexError:
                    mensaje = Celda = Corriente = None
                if mensaje == "SETC" or mensaje == "SETV" or mensaje == "FINV":
                    print("["+str(datetime.datetime.now())+"][DIND] recibo set" + str([Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga]), file=log)
                    if self.xIsActive(Celda):
                        print("["+str(datetime.datetime.now())+"][DIND|"+str(Celda)+"]activada", file=log)
                        if mensaje == "FINV":
                            print("["+str(datetime.datetime.now())+"][DIND|" + str(Celda) + "] desactiva por boton", file=log)
                            self.xPararCelda(Celda)
                            if Celda == self.celdaPLOTTR:
                                # Intento Parar Plot
                                self.mutex.lock()
                                self.dequePLOT.append([Celda, 0, 0, 0, 0])
                                self.mutex.unlock()
                            if Celda == self.celdaPLOTTR:
                                # Parar datos en tiempo real
                                self.emit(self.signal, str(0), str(0), str(0), str(0), str(0), str(0))
                    else:
                        if mensaje == "SETC":
                            self.xSetActive(Celda, self.Modos.ciclando)
                        elif mensaje == "SETV":
                            self.xSetActive(Celda, self.Modos.voc)
                        self.xEnviarPS(Celda, 1)
                        self.xCondicionesDeGuardado(Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga)
                if mensaje == "VTR":
                    print("["+str(datetime.datetime.now())+"][DIND] Celda en tiempo REAL " + str(Celda), file=log)
                    self.celdaEnTiempoReal = Celda
                if mensaje == "FTR":
                    print("["+str(datetime.datetime.now())+"][DIND] FINALIZA Celda en tiempo REAL " + str(self.celdaEnTiempoReal), file=log)
                    self.celdaEnTiempoReal = None
                if mensaje == "Plot":
                    print("["+str(datetime.datetime.now())+"][DIND] Celda PLOTEO en tiempo REAL " + str(Celda), file=log)
                    self.celdaPLOTTR = Celda
                if mensaje == "FPlot":
                    print("["+str(datetime.datetime.now())+"][DIND] FINALIZA Celda PLOTEO en tiempo REAL " + str(Celda), file=log)
                    if Celda == self.celdaPLOTTR:
                        # Intento Parar Plot
                        self.mutex.lock()
                        self.dequePLOT.append([Celda, 0, 0, 0, 0])
                        self.mutex.unlock()
                    self.celdaPLOTTR = None
                    self.dequePLOT.clear()
                if mensaje == "AUI":
                    print("["+str(datetime.datetime.now())+"][DIND] Celda valores en tiempo REAL " + str(Celda), file=log)
                    self.celdaCondUI = Celda
            # proceso desde puerto hacia csv's
            if int(len(self.dequeIN)) >= 1:
                try:
                    self.mutex.lock()
                    [mensaje, Celda, Tension, Corriente, Tiempo] = self.dequeIN.pop()
                    self.mutex.unlock()
                except IndexError:
                    mensaje = Celda = Tension = Corriente = Tiempo = None
                    print("["+str(datetime.datetime.now())+"][DIND] error extrayendo datos", file=log)
                if mensaje == "RAW":
                    if self.xIsActive(Celda):
                        cambio = self.xActualizoCampo(Celda, Tension, Corriente, Tiempo)
                        #print( "["+str(datetime.datetime.now())+"][DIND] Cambio = "+str(cambio), file=log)
                        if cambio == 1 or cambio == 2:
                            Corriente, ciclos, vli, vls, tmax, prom = self.xGetCondGuardado(Celda)
                            self.mutex.lock()
                            self.dequeOUT.append(["SETI", Celda, Corriente])
                            self.mutex.unlock()
                            if cambio == 2:
                                print("["+str(datetime.datetime.now())+"][DIND] termino ploteo en TR y datos en tiempo R ", file=log)
                                self.xPararCelda(Celda)
                                if Celda == self.celdaPLOTTR:
                                    # Intento Parar Plot
                                    self.mutex.lock()
                                    self.dequePLOT.append([Celda, 0, 0, 0, 0])
                                    self.mutex.unlock()
                                if Celda == self.celdaPLOTTR:
                                    # Parar datos en tiempo real
                                    self.emit(self.signal, str(0), str(0), str(0), str(0), str(0), str(0))
                        if self.enColaPorEnviar() != 0:
                            Celda, Corriente = self.xGetPorSetear()
                            self.mutex.lock()
                            self.dequeOUT.append(["SETI", Celda, Corriente])
                            self.mutex.unlock()
                            self.xEnviarPS(Celda, 2)
                        if Celda == self.celdaEnTiempoReal:
                            [corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct] = self.xGetCondTiempoReal(Celda)
                            #print("["+str(datetime.datetime.now())+"][DIND] EMIT val en tiempo REAL (ingresos " + str(ingresos) + ")", file=log)
                            self.emit(self.signal, str(ciclos), str(voltios), str(corriente),
                                      str(tiempoCAct), str(tiempoTot), str(ingresos))
                        if Celda == self.celdaCondUI:
                            print("["+str(datetime.datetime.now())+"][DIND] -ui-", file=log)
                            [corriente, ciclos, vli, vls, tmax, prom] = self.xGetCondGuardado(Celda)
                            self.emit(self.signalSingleShot,
                                      str(corriente), str(ciclos),
                                      str(vli), str(vls),
                                      str(tmax), str(prom))
                        if Celda == self.celdaPLOTTR:
                            #print( "["+str(datetime.datetime.now())+"][DIND] PLOT TIEMPO REAL", file=log)
                            [corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct] = self.xGetCondTiempoReal(Celda)
                            self.mutex.lock()
                            self.dequePLOT.append([Celda, ciclos, voltios, corriente, tiempoCAct])
                            self.mutex.unlock()
                if mensaje == "OK!":
                    print("["+str(datetime.datetime.now())+"][DIND] recibo OK!", file=log)
                    #self.xEnviarPS(Celda, 2)
                #if self.AllDisable() == True:
                #    self.mutex.lock()
                #    self.dequeOUT.append(["END", None, None])
                #    self.mutex.unlock()


    def xIsActive(self, num):
        if num == "a" or num == 1:
            return self.a.Activada()
        elif num == "b" or num == 2:
            return self.b.Activada()
        elif num == "c" or num == 3:
            return self.c.Activada()
        elif num == "d" or num == 4:
            return self.d.Activada()
        elif num == "e" or num == 5:
            return self.e.Activada()
        elif num == "f" or num == 6:
            return self.f.Activada()
        elif num=="g" or num == 7:
            return self.g.Activada()
        elif num=="h" or num == 8:
            return self.h.Activada()
        elif num=="i" or num == 9:
            return self.i.Activada()
        elif num=="j" or num == 10:
            return self.j.Activada()
        elif num=="k" or num == 11:
            return self.k.Activada()
        elif num=="l" or num == 12:
            return self.l.Activada()
        elif num=="m" or num == 13:
            return self.m.Activada()
        elif num=="n" or num == 14:
            return self.n.Activada()
        elif num == "o" or num == 15:
            return self.o.Activada()
        elif num == "p" or num == 16:
            return self.p.Activada()
        else:
            print("["+str(datetime.datetime.now())+"][DIND|xIsActive]- Atrib error", file=log)
            return False

    def xSetActive(self, num, modo):
        if num in (1, "a"):
            return self.a.CambiaModo(modo)
        elif num == "b" or num == 2:
            return self.b.CambiaModo(modo)
        elif num == "c" or num == 3:
            return self.c.CambiaModo(modo)
        elif num == "d" or num == 4:
            return self.d.CambiaModo(modo)
        elif num == "e" or num == 5:
            return self.e.CambiaModo(modo)
        elif num == "f" or num == 6:
            return self.f.CambiaModo(modo)
        elif num == "g" or num == 7:
            return self.g.CambiaModo(modo)
        elif num == "h" or num == 8:
            return self.h.CambiaModo(modo)
        elif num == "i" or num == 9:
            return self.i.CambiaModo(modo)
        elif num == "j" or num == 10:
            return self.j.CambiaModo(modo)
        elif num == "k" or num == 11:
            return self.k.CambiaModo(modo)
        elif num == "l" or num == 12:
            return self.l.CambiaModo(modo)
        elif num == "m" or num == 13:
            return self.m.CambiaModo(modo)
        elif num == "n" or num == 14:
            return self.n.CambiaModo(modo)
        elif num == "o" or num == 15:
            return self.o.CambiaModo(modo)
        elif num == "p" or num == 16:
            return self.p.CambiaModo(modo)
        else:
            print("["+str(datetime.datetime.now())+"][DIND|xSetActive]- Atrib error", file=log)
            return False

    def xCondicionesDeGuardado(self, num, ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga):
        if num == "a" or num == 1:
            return self.a.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "b" or num == 2:
            return self.b.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "c" or num == 3:
            return self.c.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "d" or num == 4:
            return self.d.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "e" or num == 5:
            return self.e.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "f" or num == 6:
            return self.f.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "g" or num == 7:
            return self.g.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "h" or num == 8:
            return self.h.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "i" or num == 9:
            return self.i.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "j" or num == 10:
            return self.j.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "k" or num == 11:
            return self.k.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "l" or num == 12:
            return self.l.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "m" or num == 13:
            return self.m.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "n" or num == 14:
            return self.n.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "o" or num == 15:
            return self.o.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num == "p" or num == 16:
            return self.p.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        else:
            print( "["+str(datetime.datetime.now())+"][DIND|xCondGuard] Attr Error", file=log)
            return False

    def enColaPorEnviar(self):
        #print("[" + str(datetime.datetime.now()) + "][DIND] longitud de cola de envio " + str(self.celdasAenviar.__len__()), file=log)
        return self.celdasAenviar.__len__()

    def xEnviarPS(self, num, val):
        #############################self.timerOkRececpcion.start(0.1)
        print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] longitud de cola de envio para " + str(num) + " es " + str(self.enColaPorEnviar()), file=log)
        #print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] num y val " + str(num) + "  " + str(val), file=log)
        if val == 2:
            self.hayAlgo = 0
            if self.enColaPorEnviar() >= 1:
                num = self.celdasAenviar.pop(0)
                print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] saco a " + num + " de la fila para enviar", file=log)
            else:
                print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] no tengo ninguna celda en cola, error ", file=log)
        if val == 1:
            self.hayAlgo = self.hayAlgo + 1
            self.celdasAenviar.extend(str(num))
        print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] hay algo " + str(self.hayAlgo), file=log)
        return True

        """
        if num == "a" or num == 1:
            if self.a.NecesitoEnviar(val):
                print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "b" or num == 2:
            if self.b.NecesitoEnviar(val):
                print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "c" or num == 3:
            if self.c.NecesitoEnviar(val):
                print("["+str(datetime.datetime.now())+"][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "d" or num == 4:
            if self.d.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "e" or num == 5:
            if self.e.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "f" or num == 6:
            if self.f.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "g" or num == 7:
            if self.g.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "h" or num == 8:
            if self.h.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "i" or num == 9:
            if self.i.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "j" or num == 10:
            if self.j.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "k" or num == 11:
            if self.k.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "l" or num == 12:
            if self.l.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "m" or num == 13:
            if self.m.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "n" or num == 14:
            if self.n.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "o" or num == 15:
            if self.o.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        elif num == "p" or num == 16:
            if self.p.NecesitoEnviar(val):
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] por enviar corriente", file=log)
                return True
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND][xEnvPS] no se pudo enviar corriente", file=log)
                return False
        else:
            print("datos independientes- EnviarPS - Atrib error", file=log)
        """

    def xPararCelda(self, num):
        if num == "a" or num == 1:
            if self.a.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda " + str(num), file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda " + str(num), file=log)

        elif num == "b" or num == 2:
            if self.b.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "c" or num == 3:
            if self.c.PararCelda() :
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "d" or num == 4:
            if self.d.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "e" or num == 5:
            if self.e.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "f" or num == 6:
            if self.f.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "g" or num == 7:
            if self.g.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "h" or num == 8:
            if self.h.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "i" or num == 9:
            if self.i.PararCelda():
                print( "[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print( "[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "j" or num == 10:
            if self.j.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "k" or num == 11:
            if self.k.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "l" or num == 12:
            if self.l.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "m" or num == 13:
            if self.m.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "n" or num == 14:
            if self.n.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "o" or num == 15:
            if self.o.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)

        elif num == "p" or num == 16:
            if self.p.PararCelda():
                print("[" + str(datetime.datetime.now()) + "][DIND]- parando celda", file=log)
            else:
                print("[" + str(datetime.datetime.now()) + "][DIND]- no se pudo parar celda", file=log)
        else:
            print("[" + str(datetime.datetime.now()) + "][DIND] - parar celda - Atrib error", file=log)

    def xGetCondTiempoReal(self, num):
        if num == "a" or num == 1:
            corriente = self.a.microAmperes
            ciclos = self.a.barridoActual
            voltios = self.a.milivoltios
            ingresos = self.a.ingresos
            tiempoTot = self.a.segundos
            tiempoCAct = self.a.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "b" or num == 2:
            corriente = self.b.microAmperes
            ciclos = self.b.barridoActual
            voltios = self.b.milivoltios
            ingresos = self.b.ingresos
            tiempoTot = self.b.segundos
            tiempoCAct = self.b.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "c" or num == 3:
            corriente = self.c.microAmperes
            ciclos = self.c.barridoActual
            voltios = self.c.milivoltios
            ingresos = self.c.ingresos
            tiempoTot = self.c.segundos
            tiempoCAct = self.c.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "d" or num == 4:
            corriente = self.d.microAmperes
            ciclos = self.d.barridoActual
            voltios = self.d.milivoltios
            ingresos = self.d.ingresos
            tiempoTot = self.d.segundos
            tiempoCAct = self.d.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "e" or num == 5:
            corriente = self.e.microAmperes
            ciclos = self.e.barridoActual
            voltios = self.e.milivoltios
            ingresos = self.e.ingresos
            tiempoTot = self.e.segundos
            tiempoCAct = self.e.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "f" or num == 6:
            corriente = self.f.microAmperes
            ciclos = self.f.barridoActual
            voltios = self.f.milivoltios
            ingresos = self.f.ingresos
            tiempoTot = self.f.segundos
            tiempoCAct = self.f.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "g" or num == 7:
            corriente = self.g.microAmperes
            ciclos = self.g.barridoActual
            voltios = self.g.milivoltios
            ingresos = self.g.ingresos
            tiempoTot = self.g.segundos
            tiempoCAct = self.g.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "h" or num == 8:
            corriente = self.h.microAmperes
            ciclos = self.h.barridoActual
            voltios = self.h.milivoltios
            ingresos = self.h.ingresos
            tiempoTot = self.h.segundos
            tiempoCAct = self.h.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "i" or num == 9:
            corriente = self.i.microAmperes
            ciclos = self.i.barridoActual
            voltios = self.i.milivoltios
            ingresos = self.i.ingresos
            tiempoTot = self.i.segundos
            tiempoCAct = self.i.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "j" or num == 10:
            corriente = self.j.microAmperes
            ciclos = self.j.barridoActual
            voltios = self.j.milivoltios
            ingresos = self.j.ingresos
            tiempoTot = self.j.segundos
            tiempoCAct = self.j.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "k" or num == 11:
            corriente = self.k.microAmperes
            ciclos = self.k.barridoActual
            voltios = self.k.milivoltios
            ingresos = self.k.ingresos
            tiempoTot = self.k.segundos
            tiempoCAct = self.k.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "l" or num == 12:
            corriente = self.l.microAmperes
            ciclos = self.l.barridoActual
            voltios = self.l.milivoltios
            ingresos = self.l.ingresos
            tiempoTot = self.l.segundos
            tiempoCAct = self.l.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "m" or num == 13:
            corriente = self.m.microAmperes
            ciclos = self.m.barridoActual
            voltios = self.m.milivoltios
            ingresos = self.m.ingresos
            tiempoTot = self.m.segundos
            tiempoCAct = self.m.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "n" or num == 14:
            corriente = self.n.microAmperes
            ciclos = self.n.barridoActual
            voltios = self.n.milivoltios
            ingresos = self.n.ingresos
            tiempoTot = self.n.segundos
            tiempoCAct = self.n.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "o" or num == 15:
            corriente = self.o.microAmperes
            ciclos = self.o.barridoActual
            voltios = self.o.milivoltios
            ingresos = self.o.ingresos
            tiempoTot = self.o.segundos
            tiempoCAct = self.o.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct
        if num == "p" or num == 16:
            corriente = self.p.microAmperes
            ciclos = self.p.barridoActual
            voltios = self.p.milivoltios
            ingresos = self.p.ingresos
            tiempoTot = self.p.segundos
            tiempoCAct = self.p.tiempoCicloActual
            return corriente, ciclos, voltios, ingresos, tiempoTot, tiempoCAct

    def xGetCondGuardado(self, num):
        if num == "a" or num == 1:
            corriente = self.a.corrienteSetActual
            ciclos = self.a.barridosMax
            vli = self.a.voltajeLimInferior
            vls = self.a.voltajeLimSuperior
            tmax = self.a.tiempoMaxBarrido
            prom = self.a.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "b" or num == 2:
            corriente = self.b.corrienteSetActual
            ciclos = self.b.barridosMax
            vli = self.b.voltajeLimInferior
            vls = self.b.voltajeLimSuperior
            tmax = self.b.tiempoMaxBarrido
            prom = self.b.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "c" or num == 3:
            corriente = self.c.corrienteSetActual
            ciclos = self.c.barridosMax
            vli = self.c.voltajeLimInferior
            vls = self.c.voltajeLimSuperior
            tmax = self.c.tiempoMaxBarrido
            prom = self.c.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "d" or num == 4:
            corriente = self.d.corrienteSetActual
            ciclos = self.d.barridosMax
            vli = self.d.voltajeLimInferior
            vls = self.d.voltajeLimSuperior
            tmax = self.d.tiempoMaxBarrido
            prom = self.d.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "e" or num == 5:
            corriente = self.e.corrienteSetActual
            ciclos = self.e.barridosMax
            vli = self.e.voltajeLimInferior
            vls = self.e.voltajeLimSuperior
            tmax = self.e.tiempoMaxBarrido
            prom = self.e.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "f" or num == 6:
            corriente = self.f.corrienteSetActual
            ciclos = self.f.barridosMax
            vli = self.f.voltajeLimInferior
            vls = self.f.voltajeLimSuperior
            tmax = self.f.tiempoMaxBarrido
            prom = self.f.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "g" or num == 7:
            corriente = self.g.corrienteSetActual
            ciclos = self.g.barridosMax
            vli = self.g.voltajeLimInferior
            vls = self.g.voltajeLimSuperior
            tmax = self.g.tiempoMaxBarrido
            prom = self.g.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "h" or num == 8:
            corriente = self.h.corrienteSetActual
            ciclos = self.h.barridosMax
            vli = self.h.voltajeLimInferior
            vls = self.h.voltajeLimSuperior
            tmax = self.h.tiempoMaxBarrido
            prom = self.h.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "i" or num == 9:
            corriente = self.i.corrienteSetActual
            ciclos = self.i.barridosMax
            vli = self.i.voltajeLimInferior
            vls = self.i.voltajeLimSuperior
            tmax = self.i.tiempoMaxBarrido
            prom = self.i.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "j" or num == 10:
            corriente = self.j.corrienteSetActual
            ciclos = self.j.barridosMax
            vli = self.j.voltajeLimInferior
            vls = self.j.voltajeLimSuperior
            tmax = self.j.tiempoMaxBarrido
            prom = self.j.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "k" or num == 11:
            corriente = self.k.corrienteSetActual
            ciclos = self.k.barridosMax
            vli = self.k.voltajeLimInferior
            vls = self.k.voltajeLimSuperior
            tmax = self.k.tiempoMaxBarrido
            prom = self.k.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "l" or num == 12:
            corriente = self.l.corrienteSetActual
            ciclos = self.l.barridosMax
            vli = self.l.voltajeLimInferior
            vls = self.l.voltajeLimSuperior
            tmax = self.l.tiempoMaxBarrido
            prom = self.l.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "m" or num == 13:
            corriente = self.m.corrienteSetActual
            ciclos = self.m.barridosMax
            vli = self.m.voltajeLimInferior
            vls = self.m.voltajeLimSuperior
            tmax = self.m.tiempoMaxBarrido
            prom = self.m.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "n" or num == 14:
            corriente = self.n.corrienteSetActual
            ciclos = self.n.barridosMax
            vli = self.n.voltajeLimInferior
            vls = self.n.voltajeLimSuperior
            tmax = self.n.tiempoMaxBarrido
            prom = self.n.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "o" or num == 15:
            corriente = self.o.corrienteSetActual
            ciclos = self.o.barridosMax
            vli = self.o.voltajeLimInferior
            vls = self.o.voltajeLimSuperior
            tmax = self.o.tiempoMaxBarrido
            prom = self.o.promediado
            return corriente, ciclos, vli, vls, tmax, prom
        if num == "p" or num == 16:
            corriente = self.p.corrienteSetActual
            ciclos = self.p.barridosMax
            vli = self.p.voltajeLimInferior
            vls = self.p.voltajeLimSuperior
            tmax = self.p.tiempoMaxBarrido
            prom = self.p.promediado
            return corriente, ciclos, vli, vls, tmax, prom

    def xActualizoCampo(self, num, tension, corriente, tiempo):
        if num == "a" or num == 1:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num == "b" or num == 2:
            return self.b.ActualizoCampos(tiempo, tension, corriente)
        elif num == "c" or num == 3:
            return self.c.ActualizoCampos(tiempo, tension, corriente)
        elif num == "d" or num == 4:
            return self.d.ActualizoCampos(tiempo, tension, corriente)
        elif num == "e" or num == 5:
            return self.e.ActualizoCampos(tiempo, tension, corriente)
        elif num == "f" or num == 6:
            return self.f.ActualizoCampos(tiempo, tension, corriente)
        elif num == "g" or num == 7:
            return self.g.ActualizoCampos(tiempo, tension, corriente)
        elif num == "h" or num == 8:
            return self.h.ActualizoCampos(tiempo, tension, corriente)
        elif num == "i" or num == 9:
            return self.i.ActualizoCampos(tiempo, tension, corriente)
        elif num == "j" or num == 10:
            return self.j.ActualizoCampos(tiempo, tension, corriente)
        elif num == "k" or num == 11:
            return self.k.ActualizoCampos(tiempo, tension, corriente)
        elif num == "l" or num == 12:
            return self.l.ActualizoCampos(tiempo, tension, corriente)
        elif num == "m" or num == 13:
            return self.m.ActualizoCampos(tiempo, tension, corriente)
        elif num == "n" or num == 14:
            return self.n.ActualizoCampos(tiempo, tension, corriente)
        elif num == "o" or num == 15:
            return self.o.ActualizoCampos(tiempo, tension, corriente)
        elif num == "p" or num == 16:
            return self.p.ActualizoCampos(tiempo, tension, corriente)
        else:
            print("["+str(datetime.datetime.now())+"][DIND|xActCampo] - Atrib error", file=log)

    """
    def xGetBarrYTiempo(self, num):
        if num == "a" or 1:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "b" or 2:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "c" or 3:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "d" or 4:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "e" or 5:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "f" or 6:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "g" or 7:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "h" or 8:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "i" or 9:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "j" or 10:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "k" or 11:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "l" or 12:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "m" or 13:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "n" or 14:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "o" or 15:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num == "p" or 16:
            return self.a.barridoActual, self.a.tiempoCicloActual
        else:
            print( "["+str(datetime.datetime.now())+"][DIND|xGetBarryT- Atrib error", file=log)

    def xGetValTiempoReal(self, num):
        if num == "a" or 1:
            return self.a.barridoActual, self.a.milivoltios, self.a.microAmperes, self.a.tiempoCicloActual
        elif num == "b" or 2:
            return self.b.barridoActual, self.b.milivoltios, self.b.microAmperes, self.b.tiempoCicloActual
        elif num == "c" or 3:
            return self.c.barridoActual, self.c.milivoltios, self.c.microAmperes, self.c.tiempoCicloActual
        elif num == "d" or 4:
            return self.d.barridoActual, self.d.milivoltios, self.d.microAmperes, self.d.tiempoCicloActual
        elif num == "e" or 5:
            return self.e.barridoActual, self.e.milivoltios, self.e.microAmperes, self.e.tiempoCicloActual
        elif num == "f" or 6:
            return self.f.barridoActual, self.f.milivoltios, self.f.microAmperes, self.f.tiempoCicloActual
        elif num == "g" or 7:
            return self.g.barridoActual, self.g.milivoltios, self.g.microAmperes, self.g.tiempoCicloActual
        elif num == "h" or 8:
            return self.h.barridoActual, self.h.milivoltios, self.h.microAmperes, self.h.tiempoCicloActual
        elif num == "i" or 9:
            return self.i.barridoActual, self.i.milivoltios, self.i.microAmperes, self.i.tiempoCicloActual
        elif num == "j" or 10:
            return self.j.barridoActual, self.j.milivoltios, self.j.microAmperes, self.j.tiempoCicloActual
        elif num == "k" or 11:
            return self.k.barridoActual, self.k.milivoltios, self.k.microAmperes, self.k.tiempoCicloActual
        elif num == "l" or 12:
            return self.l.barridoActual, self.l.milivoltios, self.l.microAmperes, self.l.tiempoCicloActual
        elif num == "m" or 13:
            return self.m.barridoActual, self.m.milivoltios, self.m.microAmperes, self.m.tiempoCicloActual
        elif num == "n" or 14:
            return self.n.barridoActual, self.n.milivoltios, self.n.microAmperes, self.n.tiempoCicloActual
        elif num == "o" or 15:
            return self.o.barridoActual, self.o.milivoltios, self.o.microAmperes, self.o.tiempoCicloActual
        elif num == "p" or 16:
            return self.p.barridoActual, self.p.milivoltios, self.p.microAmperes, self.p.tiempoCicloActual
        else:
            print( "datos independientes - Atrib error", file=log)
    """

    """tengo que devolver"""
    #celda = char
    #corriente = por setearle
    def xGetPorSetear(self):
        celda = self.celdasAenviar[self.enColaPorEnviar()-1]
        corriente, a, b, c, d, e = self.xGetCondGuardado(celda)
        print("["+str(datetime.datetime.now())+"][DIND] xget por setear " + str(celda) + "  " + str(corriente), file=log)
        return celda, corriente

    def AllDisable(self):
        algunaActiva = (self.a.activa or self.b.activa or self.c.activa or self.d.activa or
            self.e.activa or self.f.activa or self.g.activa or self.h.activa or
            self.i.activa or self.j.activa or self.k.activa or self.l.activa or
            self.m.activa or self.n.activa or self.o.activa or self.o.activa)
        return algunaActiva
