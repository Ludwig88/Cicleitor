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
            if int(len(self.dequeSettings)) >= 1:
                try:
                    self.mutex.lock()
                    [mensaje, Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga] = self.dequeSettings.pop()
                    self.mutex.unlock()
                except IndexError:
                    mensaje = Celda = Corriente = None
                if mensaje == "SETC" or mensaje == "SETV":
                    print "[DIND] recibo set" + str([Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga])
                    if self.xIsActive(Celda):
                        print "[DIND|"+str(Celda)+"]activada"
                    else:
                        if mensaje == "SETC":
                            self.xEnviarPS(Celda, 1)
                            self.xSetActive(Celda, self.Modos.ciclando)
                        elif mensaje == "SETV":
                            self.xEnviarPS(Celda, 1)
                            self.xSetActive(Celda, self.Modos.voc)
                        self.xCondicionesDeGuardado(Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga)
            if int(len(self.dequeIN)) >= 1:
                try:
                    self.mutex.lock()
                    [mensaje, Celda, Tension, Corriente, Tiempo] = self.dequeIN.pop()
                    self.mutex.unlock()
                except IndexError:
                    mensaje = Celda = Tension = Corriente = Tiempo = None
                    print "[DIND] error extrayendo datos"
                if mensaje == "RAW":
                    if self.xIsActive(Celda):
                        cambio = self.xActualizoCampo(Celda, Tension, Corriente, Tiempo)
                        print "[DIND] Cambio= "+str(cambio)
                        if cambio == 1 or cambio == 2:
                            Corriente, ciclos, vli, vls, tmax, prom = self.xGetCondGuardado(Celda)
                            self.mutex.lock()
                            self.dequeOUT.append(["SETI", Celda, Corriente])
                            self.mutex.unlock()
                        if self.enColaPorEnviar() != 0:
                            Celda, Corriente = self.xGetPorSetear()
                            self.mutex.lock()
                            self.dequeOUT.append(["SETI", Celda, Corriente])
                            self.mutex.unlock()
                if mensaje == "OK!":
                    self.xEnviarPS(Celda, 2)
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
            print "[DIND|xIsActive]- Atrib error"
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
        elif num == "e" or num ==  5:
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
            print "[DIND|xSetActive]- Atrib error"
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
            print "[DIND|xCondGuard] Attr Error"
            return False

    def enColaPorEnviar(self):
        return self.celdasAenviar.__len__()

    def xEnviarPS(self, num, val):
        print "[DIND][xEnvPS] longitud de cola de envio es " + str(self.enColaPorEnviar())
        print "[DIND][xEnvPS] num y val " + str(num) + "  " + str(val)

        if num == "a" or num ==1:
            if (self.a.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    print "[DIND][xEnvPS] popeo"
                    self.celdasAenviar.pop(0)
                print "[DIND][xEnvPS] por enviar corriente"
                return True
            else:
                print "[DIND][xEnvPS] no se pudo enviar corriente"
                return False

        elif num == "b" or num == 2:
            if (self.b.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                print "DInd - por enviar corriente"
                return True
            else:
                print "DInd - no se pudo enviar corriente"
                return False

        elif num == "c" or num == 3:
            if (self.c.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                print "DInd - por enviar corriente"
                return True
            else:
                print "DInd - no se pudo enviar corriente"
                return False

        elif num == "d" or num == 4:
            if (self.d.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "e" or num == 5:
            if (self.e.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "f" or num == 6:
            if (self.f.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "g" or num == 7:
            if (self.g.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "h" or num == 8:
            if (self.h.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "i" or num == 9:
            if (self.i.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "j" or num == 10:
            if (self.j.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "k" or num == 11:
            if (self.k.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "l" or num == 12:
            if (self.l.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "m" or num == 13:
            if (self.m.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "n" or num == 14:
            if (self.n.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "o" or num == 15:
            if (self.o.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False

        elif num == "p" or num == 16:
            if (self.p.NecesitoEnviar(val)) == True:
                if val == 1:
                    self.celdasAenviar.extend(str(num))
                elif val == 2:
                    self.celdasAenviar.pop(0)
                    print "DInd - por enviar corriente"
                    return True
                else:
                    print "DInd - no se pudo enviar corriente"
                    return False
        else:
            print "datos independientes- EnviarPS - Atrib error"

    def xPararCelda(self, num):
        if num == "a" or 1:
            if (self.a.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "b" or 2:
            if (self.b.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "c" or 3:
            if (self.c.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "d" or 4:
            if (self.d.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "e" or 5:
            if (self.e.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "f" or 6:
            if (self.f.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "g" or 7:
            if (self.g.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "h" or 8:
            if (self.h.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "i" or 9:
            if (self.i.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "j" or 10:
            if (self.j.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "k" or 11:
            if (self.k.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "l" or 12:
            if (self.l.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "m" or 13:
            if (self.m.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "n" or 14:
            if (self.n.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "o" or 15:
            if (self.o.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"

        elif num == "p" or 16:
            if (self.p.PararCelda()) == True:
                print "DInd - parando celda"
            else:
                print "DInd - no se pudo parar celda"
        else:
            print "datos independientes - parar celda - Atrib error"

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
            print "[DIND|xActCampo] - Atrib error"

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
            print "[DIND|xGetBarryT- Atrib error"

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
            print "datos independientes - Atrib error"
    """

    """tengo que devolver"""
    #celda = char
    #corriente = por setearle
    def xGetPorSetear(self):
        celda = self.celdasAenviar[self.enColaPorEnviar()-1]
        corriente, a, b, c, d, e = self.xGetCondGuardado(celda)
        print "[DIND] xget por setear " + str(celda) + "  " + str(corriente)
        return celda, corriente

    def AllDisable(self):
        algunaActiva = (self.a.activa or self.b.activa or self.c.activa or self.d.activa or
            self.e.activa or self.f.activa or self.g.activa or self.h.activa or
            self.i.activa or self.j.activa or self.k.activa or self.l.activa or
            self.m.activa or self.n.activa or self.o.activa or self.o.activa)
        return algunaActiva
