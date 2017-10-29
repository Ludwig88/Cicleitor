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
import csv
from PyQt4 import QtCore
from PyQt4.Qt import QMutex
from collections import deque
from DatosIndividualesCelda import DatosCelda
import ProcesoPuerto
import time


class DatosCompartidos(QtCore.QThread):

    class Modos:
        inactiva, ciclando, voc = range(3)
    PoolThread = []
    celdasAenviar = []

    def __init__(self, dequeSettings, dequePLOT, parent = None):
        print "[DCOMP] initing"
        self.b = DatosCelda("b") #2
        self.b.CambiaModo(self.Modos.inactiva)
        print " b esta " + str(self.b.Activada())
        self.c = DatosCelda("c") #3
        self.c.CambiaModo(self.Modos.inactiva)
        print " c esta " + str(self.c.Activada())
        self.d = DatosCelda("d") #4
        self.d.CambiaModo(self.Modos.inactiva)
        print " d esta " + str(self.d.Activada())
        self.e = DatosCelda("e") #5
        self.e.CambiaModo(self.Modos.inactiva)
        self.f = DatosCelda("f") #6
        self.f.CambiaModo(self.Modos.inactiva)
        self.g = DatosCelda("g") #7
        self.g.CambiaModo(self.Modos.inactiva)
        self.h = DatosCelda("h") #8
        self.h.CambiaModo(self.Modos.inactiva)
        self.a = DatosCelda("a")
        self.a.CambiaModo(self.Modos.inactiva)
        print " a esta " + str(self.a.Activada())
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

        """DEQUES de comunicacion"""
        self.dequeSettings = dequeSettings #desde UI
        self.dequePLOT = dequePLOT  #hacia UI??
        self.dequeOUT = deque(maxlen=16000) #seteos de celdas a puerto
        self.dequeIN = deque(maxlen=16000) #desde puerto crudo
        """"""
        #print "arranco thread de lectura desde DatosIndependientes"
        self.PoolThread.append(ProcesoPuerto.LECTURA(self.dequePLOT, self.dequeOUT, self.dequeIN))
        #self.PoolThread[len(self.PoolThread) - 1].start()

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        self.PoolThread[len(self.PoolThread) - 1].start()
        while (True):
            time.sleep(0.001)
            if int(len(self.dequeSettings))>= 1:
                try:
                    self.mutex.lock()
                    [mensaje, Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga] = self.dequeSettings.pop()
                    self.mutex.unlock()
                except IndexError:
                    mensaje = None
                if mensaje is "SETC" or mensaje is "SETV":
                    print "[DIND] recibo set" + str([Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga])
                    if self.xIsActive(Celda):
                        print "[DIND|"+str(Celda)+"]activada"
                    else:
                        if mensaje is "SETC":
                            self.xSetActive(Celda,self.Modos.ciclando)
                        elif mensaje is "SETV":
                            self.xSetActive(Celda,self.Modos.ciclando)
                        self.xCondicionesDeGuardado(Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga)
            if int(len(self.dequeIN)) >= 1:
                try:
                    self.mutex.lock()
                    [mensaje, celda, Tension, Corriente, Tiempo] = self.dequeIN.pop()
                    self.mutex.unlock()
                except IndexError:
                    mensaje = None
                    #print "[DIND] error extrayendo datos"
                if mensaje == "RAW":
                    if self.xIsActive(celda):
                        print "."
                        self.xActualizoCampo(celda, Tension, Corriente, Tiempo )
                # verifico que pueda setear, en cuanto, o si debo guardar datos para futuro seteo

    def xIsActive(self, num):
        print "[DIND|xIsActive] num: "+str(num)
        if num is "a" or 1:
            return self.a.Activada()
        elif num is "b" or 2:
            return self.b.Activada()
        elif num is "c" or 3:
            return self.c.Activada()
        elif num is "d" or 4:
            return self.d.Activada()
        elif num is "e" or 5:
            return self.e.Activada()
        elif num is "f" or 6:
            return self.f.Activada()
        elif num is "g" or 7:
            return self.g.Activada()
        elif num is "h" or 8:
            return self.h.Activada()
        elif num is "i" or 9:
            return self.i.Activada()
        elif num is "j" or 10:
            return self.j.Activada()
        elif num is "k" or 11:
            return self.k.Activada()
        elif num is "l" or 12:
            return self.l.Activada()
        elif num is "m" or 13:
            return self.m.Activada()
        elif num is "n" or 14:
            return self.n.Activada()
        elif num is "o" or 15:
            return self.o.Activada()
        elif num is "p" or 16:
            return self.p.Activada()
        else:
            print "datos independientes - Atrib error"
            return False

    def xSetActive(self, num, modo):
        if num is "a" or 1:
            self.a.CambiaModo(modo)
            return True
        elif num is "b" or 2:
            self.b.CambiaModo(modo)
            return True
        elif num is "c" or 3:
            self.c.CambiaModo(modo)
            return True
        elif num is "d" or 4:
            self.d.CambiaModo(modo)
            return True
        elif num is "e" or 5:
            self.e.CambiaModo(modo)
            return True
        elif num is "f" or 6:
            self.f.CambiaModo(modo)
            return True
        elif num is "g" or 7:
            self.g.CambiaModo(modo)
            return True
        elif num is "h" or 8:
            self.h.CambiaModo(modo)
            return True
        elif num is "i" or 9:
            self.i.CambiaModo(modo)
            return True
        elif num is "j" or 10:
            self.j.CambiaModo(modo)
            return True
        elif num is "k" or 11:
            self.k.CambiaModo(modo)
            return True
        elif num is "l" or 12:
            self.l.CambiaModo(modo)
            return True
        elif num is "m" or 13:
            self.m.CambiaModo(modo)
            return True
        elif num is "n" or 14:
            self.n.CambiaModo(modo)
            return True
        elif num is "o" or 15:
            self.o.CambiaModo(modo)
            return True
        elif num is "p" or 16:
            self.p.CambiaModo(modo)
            return True
        else:
            print "[DIND] datos independientes - Atrib error"
            return False

    def xCondicionesDeGuardado(self, num, ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga):
        if num is "a" or 1:
            return self.a.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "b" or 2:
            return self.b.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "c" or 3:
            return self.c.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "d" or 4:
            return self.d.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "e" or 5:
            return self.e.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "f" or 6:
            return self.f.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "g" or 7:
            return self.g.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "h" or 8:
            return self.h.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "i" or 9:
            return self.i.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "j" or 10:
            return self.j.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "k" or 11:
            return self.k.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "l" or 12:
            return self.l.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "m" or 13:
            return self.m.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "n" or 14:
            return self.n.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "o" or 15:
            return self.o.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        elif num is "p" or 16:
            return self.p.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)
        else:
            print "error"
            return False

    def enColaPorEnviar(self):
        return self.celdasAenviar.__len__()

    def xEnviarPS(self, num, val):
        print "[DIND][xEnvPS] longitud de cola de envio es " + str(self.enColaPorEnviar())
        print "[DIND][xEnvPS] num y val " + str(num) + "  " + str(val)

        if num is "a" or 1:
            if (self.a.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    print "[DIND][xEnvPS] popeo"
                    self.celdasAenviar.pop(0)
                print "[DIND][xEnvPS] por enviar corriente"
                return True
            else:
                print "[DIND][xEnvPS] no se pudo enviar corriente"
                return False

        elif num is "b" or 2:
            if (self.b.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                print "DInd - por enviar corriente"
                return True
            else:
                print "DInd - no se pudo enviar corriente"
                return False

        elif num is "c" or 3:
            if (self.c.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                print "DInd - por enviar corriente"
                return True
            else:
                print "DInd - no se pudo enviar corriente"
                return False

        elif num is "d" or 4:
            if (self.d.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "e" or 5:
            if (self.e.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "f" or 6:
            if (self.f.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "g" or 7:
            if (self.g.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "h" or 8:
            if (self.h.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "i" or 9:
            if (self.i.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "j" or 10:
            if (self.j.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "k" or 11:
            if (self.k.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "l" or 12:
            if (self.l.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "m" or 13:
            if (self.m.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "n" or 14:
            if (self.n.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "o" or 15:
            if (self.o.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num is "p" or 16:
            if (self.p.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False
        else:
            print "datos independientes- EnviarPS - Atrib error"

    def PrimerInicio(self):
        print "NO arranco el thread del puerto"
        # self.PoolThread[len(self.PoolThread)-1].start()
        # time.sleep(0.5)

    # def xIniciaCiclado(self, num, ciclos, VLIMS, VLIMI, T_Max, Corr, Promedio, CoD):
    #     if self.xIsActive(num):
    #         print "[DIND][CICLADO] no puedo setear celda activa"
    #     else:
    #         self.xSetActive(num, self.Modos.ciclando)
    #         if (self.xCondicionesDeGuardado(num, ciclos, VLIMS, VLIMI, T_Max, Corr, Promedio, CoD)) is True:
    #             print "[DIND][CICLADO] actualizadas condiciones de guardado"
    #         else:
    #             print "[DIND][CICLADO] no pudo actualizar condiciones de guardado"

    # def xIniciaVoc(self, num, Promedio, T_Max):
    #     if self.xIsActive(num):
    #         print "[DIND|VOC] no puedo setear celda activa"
    #     else:
    #         self.xSetActive(num, self.Modos.voc)
    #         if (self.xCondicionesDeGuardado(num, 1, 9999, -9999, T_Max, 0, Promedio, True)) is True:
    #             print "[DIND|VOC] actualizadas condiciones de guardado"
    #         else:
    #             print "[DIND|VOC] no pudo actualizar condiciones de guardado"

    def xPararCelda(self, num):
        if num is "a" or 1:
            if (self.a.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "b" or 2:
            if (self.b.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "c" or 3:
            if (self.c.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "d" or 4:
            if (self.d.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "e" or 5:
            if (self.e.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "f" or 6:
            if (self.f.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "g" or 7:
            if (self.g.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "h" or 8:
            if (self.h.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "i" or 9:
            if (self.i.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "j" or 10:
            if (self.j.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "k" or 11:
            if (self.k.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "l" or 12:
            if (self.l.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "m" or 13:
            if (self.m.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "n" or 14:
            if (self.n.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "o" or 15:
            if (self.o.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num is "p" or 16:
            if (self.p.PararCelda()) is True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"
        else:
            print "datos independientes - parar celda - Atrib error"

    """FALTA multiplicar"""
    def xGetCondGuardado(self, num):
        if num is "a" or 1:
            corriente = self.a.corrienteSetActual
            ciclos = self.a.barridosMax
            vli = self.a.voltajeLimInferior
            vls = self.a.voltajeLimSuperior
            tmax = self.a.tiempoMaxBarrido
            prom = self.a.promediado
        return corriente, ciclos, vli, vls, tmax, prom

    def xActualizoCampo(self, num, tension, corriente, tiempo):
        if num is "a" or 1:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "b" or 2:
            return self.b.ActualizoCampos(tiempo, tension, corriente)
        elif num is "c" or 3:
            return self.c.ActualizoCampos(tiempo, tension, corriente)
        elif num is "d" or 4:
            return self.d.ActualizoCampos(tiempo, tension, corriente)
        elif num is "e" or 5:
            return self.e.ActualizoCampos(tiempo, tension, corriente)
        elif num is "f" or 6:
            return self.f.ActualizoCampos(tiempo, tension, corriente)
        elif num is "g" or 7:
            return self.g.ActualizoCampos(tiempo, tension, corriente)
        elif num is "h" or 8:
            return self.h.ActualizoCampos(tiempo, tension, corriente)
        elif num is "i" or 9:
            return self.i.ActualizoCampos(tiempo, tension, corriente)
        elif num is "j" or 10:
            return self.j.ActualizoCampos(tiempo, tension, corriente)
        elif num is "k" or 11:
            return self.k.ActualizoCampos(tiempo, tension, corriente)
        elif num is "l" or 12:
            return self.l.ActualizoCampos(tiempo, tension, corriente)
        elif num is "m" or 13:
            return self.m.ActualizoCampos(tiempo, tension, corriente)
        elif num is "n" or 14:
            return self.n.ActualizoCampos(tiempo, tension, corriente)
        elif num is "o" or 15:
            return self.o.ActualizoCampos(tiempo, tension, corriente)
        elif num is "p" or 16:
            return self.p.ActualizoCampos(tiempo, tension, corriente)
        else:
            print "datos independientes - Atrib error"

    def xGetBarrYTiempo(self, num):
        if num is "a" or 1:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "b" or 2:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "c" or 3:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "d" or 4:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "e" or 5:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "f" or 6:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "g" or 7:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "h" or 8:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "i" or 9:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "j" or 10:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "k" or 11:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "l" or 12:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "m" or 13:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "n" or 14:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "o" or 15:
            return self.a.barridoActual, self.a.tiempoCicloActual
        elif num is "p" or 16:
            return self.a.barridoActual, self.a.tiempoCicloActual
        else:
            print "datos independientes - Atrib error"

    def xGetValTiempoReal(self, num):
        if num is "a" or 1:
            return self.a.barridoActual, self.a.milivoltios, self.a.microAmperes, self.a.tiempoCicloActual
        elif num is "b" or 2:
            return self.b.barridoActual, self.b.milivoltios, self.b.microAmperes, self.b.tiempoCicloActual
        elif num is "c" or 3:
            return self.c.barridoActual, self.c.milivoltios, self.c.microAmperes, self.c.tiempoCicloActual
        elif num is "d" or 4:
            return self.d.barridoActual, self.d.milivoltios, self.d.microAmperes, self.d.tiempoCicloActual
        elif num is "e" or 5:
            return self.e.barridoActual, self.e.milivoltios, self.e.microAmperes, self.e.tiempoCicloActual
        elif num is "f" or 6:
            return self.f.barridoActual, self.f.milivoltios, self.f.microAmperes, self.f.tiempoCicloActual
        elif num is "g" or 7:
            return self.g.barridoActual, self.g.milivoltios, self.g.microAmperes, self.g.tiempoCicloActual
        elif num is "h" or 8:
            return self.h.barridoActual, self.h.milivoltios, self.h.microAmperes, self.h.tiempoCicloActual
        elif num is "i" or 9:
            return self.i.barridoActual, self.i.milivoltios, self.i.microAmperes, self.i.tiempoCicloActual
        elif num is "j" or 10:
            return self.j.barridoActual, self.j.milivoltios, self.j.microAmperes, self.j.tiempoCicloActual
        elif num is "k" or 11:
            return self.k.barridoActual, self.k.milivoltios, self.k.microAmperes, self.k.tiempoCicloActual
        elif num is "l" or 12:
            return self.l.barridoActual, self.l.milivoltios, self.l.microAmperes, self.l.tiempoCicloActual
        elif num is "m" or 13:
            return self.m.barridoActual, self.m.milivoltios, self.m.microAmperes, self.m.tiempoCicloActual
        elif num is "n" or 14:
            return self.n.barridoActual, self.n.milivoltios, self.n.microAmperes, self.n.tiempoCicloActual
        elif num is "o" or 15:
            return self.o.barridoActual, self.o.milivoltios, self.o.microAmperes, self.o.tiempoCicloActual
        elif num is "p" or 16:
            return self.p.barridoActual, self.p.milivoltios, self.p.microAmperes, self.p.tiempoCicloActual
        else:
            print "datos independientes - Atrib error"

    """tengo que devolver"""
    #celda = char
    #corriente = por setearle
    def xGetPorSetear(self, num):
        celda = self.celdasAenviar[self.enColaPorEnviar()-1]
        corriente, a, b, c, d, e = self.xGetCondGuardado(num)
        print "xget por setear " + str(celda) + "  " + str(corriente)
        return celda, corriente

    def AllDisable(self):
        algunaActiva = (self.a.activa or self.b.activa or self.c.activa or self.d.activa or
            self.e.activa or self.f.activa or self.g.activa or self.h.activa or
            self.i.activa or self.j.activa or self.k.activa or self.l.activa or
            self.m.activa or self.n.activa or self.o.activa or self.o.activa)
        return algunaActiva
