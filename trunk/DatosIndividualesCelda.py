from __future__ import print_function

import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'debug/Log.txt')
log = None #open(filename, "a+")

from collections import deque
import csv, datetime


class DatosCelda:
    class Modos:
        inactiva, ciclando, voc = range(3)

    encabezadoCSV = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ', ' TCicloActual[Seg] ', ' Ingresos[n] ']

    def __init__(self, nomb, activ=False,
                 prom=0.0, barr=0, barrM=0, vli=0,
                 vls=0, corr=0, tmb=0,
                 milivoltios=0, microAmperes=0, ingresos=0,
                 segundos=0):

        #print( "["+str(datetime.datetime.now())+"DCELD] initing " + str(nomb) + " id " + str(id(self)),file=log)
        # atributos de 1 sola vez
        self.nombre = nomb
        self.promediado = prom
        # activa puede sacarse a cambio de leer un modo distinto a cero
        self.activa = activ
        self.modo = self.Modos.inactiva

        # atributos para procesos de extremo
        self.porenviar = 0  # 0=nada por hacer, 1=enviar algo, 2, ack de envio
        self.barridosMax = barrM
        self.voltajeLimInferior = vli
        self.voltajeLimSuperior = vls
        self.tiempoMaxBarrido = tmb
        self.iniciaEnCarga = True
        self.corrienteSetActual = corr

        self.tiempoInicioCiclo = 0
        # atributos tiempo real
        self.tiempoCicloActual = 0
        self.PaPromediar = []
        self.ingresos = ingresos  # cantidad de tramas cargadas
        self.barridoActual = barr
        self.milivoltios = milivoltios
        self.microAmperes = microAmperes
        self.segundos = segundos
        # carga = true / descarga = false
        self.CargaDescarga = True

    """
       val=0: disponible para cambiar (solo Port)
       val=1: Tengo q enviar (ui a port)
       val=2: Ya envie Port a UI
    """
    def NecesitoEnviar(self, val):
        print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] " + str(val) + " celda: " + str(self.nombre), file=log)
        if val == 0:
            if self.porenviar == 0:
                # no puedo limpiar un flag ya limpio
                return False
            elif self.porenviar == 1:
                self.porenviar = 0
                return True
            elif self.porenviar == 2:
                # Puede limpiar su propia flag??
                self.porenviar = 0
                return True
            else:
                print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] 1 Necesito Enviar Error", file=log)
                return False
        elif val == 1:
            if self.porenviar == 0:
                self.porenviar = 1
                return True
            elif self.porenviar == 1:
                print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] 2 Necesito Enviar Error", file=log)
                return False
            elif self.porenviar == 2:
                self.porenviar = 1
                # puerto ya envio y levanto nuevamente
                return True
            else:
                print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] 2 2 Necesito Enviar Error", file=log)
                return False
        elif val == 2:
            if self.porenviar == 0:
                # si nadie me levanto el flag no puedo limpiar
                print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] 3 Necesito Enviar Error", file=log)
                return False
            elif self.porenviar == 1:
                self.porenviar = 2
                return True
            elif self.porenviar == 2:
                # ya hice ack
                return False
            else:
                print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] 3 3 Necesito Enviar Error", file=log)
                return False
        else:
            print("["+str(datetime.datetime.now())+"][DCELD][xEnvPS] 4 Necesito Enviar val error", file=log)
            return False

    def ActualizoCampos(self, tiempo, voltios, corriente):
        if self.ingresos == 1:
            """primer ingreso"""
            self.ingresos = 2
            print( "["+str(datetime.datetime.now())+"DCELD|"+str(self.nombre)+"] primer ingreso = "+str(self.ingresos),file=log)
            self.tiempoInicioCiclo = tiempo
            self.barridoActual = 1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.GuardaCsv()
            ############################################################Inicio Promediado
            return 0
        elif self.modo == self.Modos.ciclando:
            """Ciclando"""
            self.ingresos = self.ingresos + 1
            #print( "["+str(datetime.datetime.now())+"DCELD] ciclando - ingresos: "+str(self.ingresos),,file=log)
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.segundos = tiempo
            #tiempoFinAnteriorBarrido =  + ((self.barridoActual - 1) * self.tiempoMaxBarrido)
            self.tiempoCicloActual = tiempo - self.tiempoInicioCiclo
            #print( " tiempo ciclo("+str(self.barridoActual)+") actual: "+str(self.tiempoCicloActual)+" tiempo: "+str(tiempo),file=log)
            limite = self.SuperaLimite()
            if limite == 0:
                self.GuardaCsv()
                ############################################################append Promediado
                return 0
            elif limite == 2:
                #self.porenviar() mando I=0
                # ENVIO I = 0
                self.PararCelda()
                self.ResetValCiclado()
                self.CerrarCSV()
                return 2
            elif limite == 1:
                self.barridoActual = self.barridoActual + 1
                self.corrienteSetActual = - self.corrienteSetActual
                self.CargaDescarga = not self.CargaDescarga
                self.tiempoInicioCiclo = tiempo
                self.tiempoCicloActual = 0
                self.GuardaCsv()
                return 1
        elif self.modo == self.Modos.voc:
            print( "["+str(datetime.datetime.now())+"DCELD] VOC",file=log)
            self.ingresos = +1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.segundos = tiempo
            self.tiempoCicloActual = tiempo - self.tiempoInicioCiclo
            if self.SuperaLimite() != 2:
                ############################################################ENVIO
                self.GuardaCsv()
                ############################################################append Promediado
                return 0
            else:
                return 2

    def CondicionesDeGuardado(self, barridos, VLS, VLI, TMAX, Corr, Promedio, ComienzaEnCarga):
        BadArgument = 0
        self.ingresos = 1
        print("["+str(datetime.datetime.now())+"][DCELD] ingresos " + str(self.ingresos),file=log)
        if barridos > 0:
            self.barridosMax = barridos * 2  # por la mala definicion original
        else:
            print("["+str(datetime.datetime.now())+"][DCELD] Bad Arg: Barridos",file=log)
            BadArgument = 1
        self.CargaDescarga = ComienzaEnCarga
        if 0 <= Promedio >= 100:
            self.promediado = Promedio
        else:
            print("["+str(datetime.datetime.now())+"][DCELD] Bad Arg: Promedio",file=log)
            BadArgument = 1
        self.voltajeLimSuperior = VLS
        self.voltajeLimInferior = VLI
        self.tiempoMaxBarrido = TMAX
        if -999999 <= Corr <= 999999:
            self.corrienteSetActual = Corr
        else:
            print("["+str(datetime.datetime.now())+"][DCELD] Bad Arg: Corriente",file=log)
            BadArgument = 1
        print("["+str(datetime.datetime.now())+"][DCELD|" + str(self.nombre) + "][CONDGUARD] barridos=" + str(self.barridosMax)+", VLS=" + str(self.voltajeLimSuperior) + ", " \
              "VLI=" + str(self.voltajeLimInferior) + ", TMAX=" + str(self.tiempoMaxBarrido) + ", Corr=" + str(self.corrienteSetActual) + ", Promedio=" + str(self.promediado) + ", ComienzaEnCarga=" + str(self.iniciaEnCarga),file=log)
        if BadArgument != 0:
            print( "["+str(datetime.datetime.now())+"][DCELD] Some Bad Arg return False",file=log)
            return False
        else:
            return True

    def SuperaLimite(self):
        if (self.milivoltios >= self.voltajeLimSuperior) \
                or (self.milivoltios <= self.voltajeLimInferior) \
                or (self.tiempoCicloActual >= self.tiempoMaxBarrido):
            print("["+str(datetime.datetime.now())+"DCELD|supLim] supere algun extremo",file=log)
            if (self.barridoActual + 1)  > self.barridosMax:
                print("["+str(datetime.datetime.now())+"DCELD] termine ciclado",file=log)
                return 2
            else:
                print("["+str(datetime.datetime.now())+"DCELD] invertir corriente",file=log)
                return 1
        else:
            return 0

    def ResetValCiclado(self):
        self.tiempoInicioCiclo = 0
        self.tiempoCicloActual = 0
        self.barridosMax = 0
        self.voltajeLimInferior = 0
        self.voltajeLimSuperior = 0
        self.tiempoMaxBarrido = 0

    def IniciaVoc(self, prom, tmax):
        if self.modo != self.Modos.voc:
            self.modo = self.Modos.voc
            self.corrienteSetActual = 0
            self.barridosMax = 1
            self.voltajeLimInferior = -99999
            self.voltajeLimSuperior = 99999
            self.promediado = prom
            self.tiempoMaxBarrido = tmax
        else:
            print( "["+str(datetime.datetime.now())+"DCELD] esta en modo de barrido de Voltaje a circuito abierto",file=log)

    def Activada(self):
        return self.activa

    def CambiaModo(self, modo):
        if modo == self.Modos.inactiva:
            self.activa = False
            self.modo = self.Modos.inactiva
            return True
        elif modo == self.Modos.ciclando:
            self.activa = True
            self.modo = self.Modos.ciclando
            return True
        elif modo == self.Modos.voc:
            self.activa = True
            self.modo = self.Modos.voc
            return True
        else:
            return False

    def PararCelda(self):
        if self.modo != self.Modos.inactiva:
            self.CambiaModo(self.Modos.inactiva)
            self.activa = False
            self.CondicionesDeGuardado(0, 0, 0, 0, 0, 0.0, True)
            return True
        else:
            print( "["+str(datetime.datetime.now())+"DCELD] imposible detener una celda inactiva",file=log)
            return False

    def GuardaCsv(self):
        barrido = (self.barridoActual / 2) + (self.barridoActual % 2)
        columna = [barrido, self.milivoltios, self.microAmperes, self.segundos, self.tiempoCicloActual, self.ingresos]
        # [Barrido, Tension, Corriente, TiempoTotal, TiempoCiclo, Ingresos]
        fileName = 'Arch_Cn-' + str(self.nombre) + '.csv'
        try:
            open(fileName, 'r')
            with open(fileName, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna)
                f.close()
        except IOError:
            with open(fileName, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(self.encabezadoCSV)
                f_csv.writerow(columna)
                f.close()

    def CerrarCSV(self):
        columna = [' ----- ', ' ----- ', ' ----- ',' ----- ', ' ----- ', ' ----- ']
        Nombrefile = 'Arch_Cn-' + str(self.nombre) + '.csv'
        try:
            open(Nombrefile, 'r')
            with open(Nombrefile, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna)
                f.close()
        except IOError:
            with open(Nombrefile, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(self.encabezadoCSV)
                f_csv.writerow(columna)
                f.close()
