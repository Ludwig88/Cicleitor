#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    encabezadoCSV = [' Ingresos[n] ', ' FechaMuestra ', ' Tiempo[Seg] ', ' TCicloActual[Seg] ', ' Barrido[n] ',
                     ' Paso[0,OCP,+,-] ', ' Corriente[A] ', ' Tension[V]']

    def __init__(self, nomb, activ=False,
                 prom=0.0, barr=0, barrM=0, vli=0,
                 vls=0, corr=0, tmb=0,
                 milivoltios=0, microAmperes=0, ingresos=0,
                 segundos=0):

        #print( "["+str(datetime.datetime.now())+"][DCELD] initing " + str(nomb) + " id " + str(id(self)),file=log)
        # atributos de 1 sola vez
        self.nombre = nomb
        self.promediado = prom
        self.promediadoArray_I = []
        self.promediadoArray_V = []
        self.activa = activ
        self.modo = self.Modos.inactiva

        # atributos para procesos de extremo
        self.porenviar = 0                  # 0=nada por hacer, 1=enviar algo, 2, ack de envio
        self.barridosMax = barrM
        self.voltajeLimInferior = vli
        self.voltajeLimSuperior = vls
        self.tiempoMaxBarrido = tmb
        self.iniciaEnCarga = True
        self.corrienteSetActual = corr

        self.tiempoComienzo = 0
        self.tiempoInicioCiclo = 0
        # atributos tiempo real
        self.tiempoCicloActual = 0
        self.PaPromediar = []               # no en uso!
        self.ingresos = ingresos            # cantidad de tramas cargadas
        self.barridoActual = barr
        self.milivoltios = milivoltios
        self.microAmperes = microAmperes
        self.segundos = segundos            # tiempo total de proceso
        # carga = true / descarga = false
        self.CargaDescarga = True           # no en uso!

    """
       val=0: disponible para cambiar (solo Port)
       val=1: Tengo q enviar (ui a port)
       val=2: Ya envie Port a UI
    """
    def NecesitoEnviar(self, val):
        print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] " + str(val) + " celda: " + str(self.nombre), file=log)
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
                print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] 1 Necesito Enviar Error", file=log)
                return False
        elif val == 1:
            if self.porenviar == 0:
                self.porenviar = 1
                return True
            elif self.porenviar == 1:
                print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] 2 Necesito Enviar Error", file=log)
                return False
            elif self.porenviar == 2:
                self.porenviar = 1
                # puerto ya envio y levanto nuevamente
                return True
            else:
                print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] 2 2 Necesito Enviar Error", file=log)
                return False
        elif val == 2:
            if self.porenviar == 0:
                # si nadie me levanto el flag no puedo limpiar
                print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] 3 Necesito Enviar Error", file=log)
                return False
            elif self.porenviar == 1:
                self.porenviar = 2
                return True
            elif self.porenviar == 2:
                # ya hice ack
                return False
            else:
                print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] 3 3 Necesito Enviar Error", file=log)
                return False
        else:
            print("["+str(datetime.datetime.now())+"][DCELD][NecesitoEnviar] 4 Necesito Enviar val error", file=log)
            return False

    def ActualizoCampos(self, tiempo, voltios, corriente):
        if self.ingresos == 1:
            """primer ingreso"""
            self.ingresos = 2
            print( "["+str(datetime.datetime.now())+"][DCELD|"+str(self.nombre)+"] primer ingreso = "+str(self.ingresos),file=log)
            self.tiempoInicioCiclo = tiempo
            self.tiempoComienzo = tiempo
            self.barridoActual = 1
            self.microAmperes = corriente
            self.milivoltios = voltios
            #self.GuardaCsv()
            self.AppendPromediado(False)
            return 0
        elif self.modo == self.Modos.ciclando:
            """Ciclando"""
            self.ingresos = self.ingresos + 1
            #print( "["+str(datetime.datetime.now())+"][DCELD] ciclando - ingresos: "+str(self.ingresos),,file=log)
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.segundos = tiempo - self.tiempoComienzo
            #tiempoFinAnteriorBarrido =  + ((self.barridoActual - 1) * self.tiempoMaxBarrido)
            self.tiempoCicloActual = tiempo - self.tiempoInicioCiclo
            #print( " tiempo ciclo("+str(self.barridoActual)+") actual: "+str(self.tiempoCicloActual)+" tiempo: "+str(tiempo),file=log)
            limite = self.SuperaLimite()
            if limite == 0:
                #self.GuardaCsv()
                self.AppendPromediado()
                return 0
            elif limite == 2:
                self.AppendPromediado(False)
                self.PararCelda()
                self.ResetValCiclado()
                return 2
            elif limite == 1:
                self.barridoActual = self.barridoActual + 1
                self.corrienteSetActual = - self.corrienteSetActual
                self.CargaDescarga = not self.CargaDescarga
                self.tiempoInicioCiclo = tiempo
                self.tiempoCicloActual = 0
                #self.GuardaCsv()
                self.AppendPromediado()
                return 1
        elif self.modo == self.Modos.voc:
            self.ingresos = self.ingresos + 1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.segundos = tiempo - self.tiempoComienzo
            self.tiempoCicloActual = tiempo - self.tiempoInicioCiclo
            if self.SuperaLimite() == 0:
                #self.GuardaCsv()
                self.AppendPromediado()
                return 0
            else:
                self.AppendPromediado(False)
                self.PararCelda()
                self.ResetValCiclado()
                print("[" + str(datetime.datetime.now()) + "][DCELD] VOC finalizado", file=log)
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
        if Promedio != 0:
            MuestrasProm = int(100 / float(Promedio))
            print("[" + str(datetime.datetime.now()) + "][DCELD] Promedio: " + str(MuestrasProm), file=log)
            if MuestrasProm >= 1 or MuestrasProm >= 400:
                self.promediado = MuestrasProm
            else:
                print("["+str(datetime.datetime.now())+"][DCELD] Bad Arg: Promedio",file=log)
                BadArgument = 1
        else:
            print("[" + str(datetime.datetime.now()) + "][DCELD] Bad Arg: Promedio", file=log)
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
            print("["+str(datetime.datetime.now())+"][DCELD] Some Bad Arg return False",file=log)
            return False
        else:
            return True

    def SuperaLimite(self):
        if (self.milivoltios >= self.voltajeLimSuperior) \
                or (self.milivoltios <= self.voltajeLimInferior) \
                or (self.tiempoCicloActual >= self.tiempoMaxBarrido):
            print("["+str(datetime.datetime.now())+"][DCELD|supLim] supere algun extremo",file=log)
            if (self.barridoActual + 1)  > self.barridosMax:
                print("["+str(datetime.datetime.now())+"][DCELD] termine ciclado",file=log)
                return 2
            else:
                print("["+str(datetime.datetime.now())+"][DCELD] invertir corriente",file=log)
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
            print( "["+str(datetime.datetime.now())+"][DCELD] esta en modo de barrido de Voltaje a circuito abierto",file=log)

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
            self.AppendPromediado(False, True)
            self.CondicionesDeGuardado(0, 0, 0, 0, 0, 0.0, True)
            return True
        else:
            print("["+str(datetime.datetime.now())+"][DCELD] imposible detener una celda inactiva",file=log)
            return False

    def AppendPromediado(self, activo = True, cierre = False):
        if cierre != True:
            if activo != False:
                if self.promediadoArray_I.__len__() == (int(self.promediado) - 1):
                    self.promediadoArray_V.append(self.milivoltios,)
                    self.promediadoArray_I.append(self.microAmperes,)
                    mAmp = mVolt = 0
                    for element in self.promediadoArray_I:
                        mAmp = mAmp + element
                    for element in self.promediadoArray_V:
                        mVolt = mVolt + element
                    mAmp = float(mAmp / self.promediadoArray_I.__len__())
                    mVolt = float(mVolt / self.promediadoArray_V.__len__())
                    print("[" + str(datetime.datetime.now()) + "][DCELD] promediadoarray_I " + str(
                        self.promediadoArray_I) + "mAmp " + str(mAmp) + " - mVolt " + str(mVolt), file=log)
                    self.GuardaCsvProm(mAmp, mVolt)
                    self.promediadoArray_I = []
                    self.promediadoArray_V = []
                else:
                    self.promediadoArray_V.append(self.milivoltios,)
                    self.promediadoArray_I.append(self.microAmperes,)
            else:
                self.promediadoArray_V.append(self.milivoltios, )
                self.promediadoArray_I.append(self.microAmperes, )
                mAmp = mVolt = 0
                for element in self.promediadoArray_I:
                    mAmp = mAmp + element
                for element in self.promediadoArray_V:
                    mVolt = mVolt + element
                mAmp = float(mAmp / self.promediadoArray_I.__len__())
                mVolt = float(mVolt / self.promediadoArray_V.__len__())
                self.GuardaCsvProm(mAmp, mVolt)
                self.promediadoArray_I = []
                self.promediadoArray_V = []
        else:
            self.CerrarCsvProm()
            self.promediadoArray_I = []
            self.promediadoArray_V = []

    def CerrarCsvProm(self):
        print("[" + str(datetime.datetime.now()) + "][DCELD] Cierro CSV Prom", file=log)
        columna1 = [' ----- ', ' ----- ', ' ----- ' , ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ']
        columna2 = [' ', ' ', ' ',' Tiempo Maximo de Barrido: '+str(self.tiempoMaxBarrido), ' Máxima cantidad de barridos: ' +
                   str(self.barridosMax / 2), ' Potencial Limite Superior: ' + str(self.voltajeLimSuperior),
                   ' Potencial Limite Inferior: ' + str(self.voltajeLimInferior), ' Corriente de proceso: '
                   + str(self.corrienteSetActual) , ' Promediado de ' + str(int(self.promediado)) + ' muestras']
        columna3 = [' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ']

        fileName = 'Arch_CnProm-' + str(self.nombre) + '.csv'
        try:
            open(fileName, 'r')
            with open(fileName, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna1)
                f_csv.writerow(columna2)
                f_csv.writerow(columna3)
                f.close()
        except IOError:
            with open(fileName, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(self.encabezadoCSV)
                f_csv.writerow(columna1)
                f_csv.writerow(columna2)
                f_csv.writerow(columna3)
                f.close()

    def GuardaCsvProm(self, microAmp, milivolts):
            barrido = (self.barridoActual / 2) + (self.barridoActual % 2)

            if self.modo == self.Modos.inactiva:
                paso = 0
            elif self.modo == self.Modos.voc:
                paso = 1
            elif self.modo == self.Modos.ciclando:
                if self.corrienteSetActual >= 0:
                    paso = 2
                else:
                    paso = 3
            else:
                paso = 0

            columna = [self.ingresos, str(datetime.datetime.now()), self.segundos,
                       self.tiempoCicloActual, paso, barrido,
                       microAmp / 1000000.0, milivolts / 1000.0]
            """
            Ingreso -- Hora-Fecha del experimento -- Tiempo acumulado -- Tiempo de ese paso -- Barrido (número de ciclo)
            -- Paso (inactiva=0, OCP=1, carga=2 o descarga=3) -- Coriente(A) -- Voltaje(V)

            """
            fileName = 'Arch_CnProm-' + str(self.nombre) + '.csv'
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

    def GuardaCsv(self):
        barrido = (self.barridoActual / 2) + (self.barridoActual % 2)

        if self.modo == self.Modos.inactiva:
            paso = 0
        elif self.modo == self.Modos.voc:
            paso = 1
        elif self.modo == self.Modos.ciclando:
            if self.corrienteSetActual >= 0:
                paso = 2
            else:
                paso = 3
        else:
            paso = 0

        columna = [self.ingresos, str(datetime.datetime.now()), self.segundos,
                   self.tiempoCicloActual, paso, barrido,
                self.microAmperes / 1000000.0, self.milivoltios / 1000.0]
        """
        Ingreso -- Hora-Fecha del experimento -- Tiempo acumulado -- Tiempo de ese paso -- Barrido (número de ciclo)
        -- Paso (inactiva=0, OCP=1, carga=2 o descarga=3) -- Coriente(A) -- Voltaje(V)

        """
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
        columna1 = [' ----- ', ' ----- ', ' ----- ' , ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ']
        columna2 = [' ', ' ', ' ',' Tiempo Maximo de Barrido: '+str(self.tiempoMaxBarrido), ' Máxima cantidad de barridos: ' +
                   str(self.barridosMax / 2), ' Potencial Limite Superior: ' + str(self.voltajeLimSuperior),
                   ' Potencial Limite Inferior: ' + str(self.voltajeLimInferior), ' Corriente de proceso: '
                   + str(self.corrienteSetActual)]
        columna3 = [' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ', ' ----- ']

        Nombrefile = 'Arch_Cn-' + str(self.nombre) + '.csv'

        try:
            open(Nombrefile, 'r')
            with open(Nombrefile, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna1)
                f_csv.writerow(columna2)
                f_csv.writerow(columna3)
                f.close()
        except IOError:
            with open(Nombrefile, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(self.encabezadoCSV)
                f_csv.writerow(columna1)
                f_csv.writerow(columna2)
                f_csv.writerow(columna3)
                f.close()
