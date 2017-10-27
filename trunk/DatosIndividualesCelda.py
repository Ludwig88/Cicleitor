from collections import deque
import csv


class DatosCelda:
    class Modos:
        inactiva, ciclando, voc = range(3)

    encabezadoCSV = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ']

    def __init__(self, nomb, activ=False,
                 prom=0.0, barr=0, barrM=0, vli=0,
                 vls=0, corr=0, tmb=0,
                 milivoltios=0, microAmperes=0, ingresos=0,
                 segundos=0):

        print "[DCELD] initing " + str(nomb) + " id " + str(id(self))
        # atributos de 1 sola vez
        self.nombre = nomb
        self.promediado = prom
        # activa puede sacarse a cambio de leer un modo distinto a cero
        self.activa = activ
        self.modo = self.Modos.inactiva

        # atributos para procesos de extremo
        self.porenviar = 0  # 0=nada por hacer, 1=enviar algo, 2, ack de envio
        self.tiempoInicioCiclo = 0
        self.tiempoCicloActual = 0
        self.barridosMax = barrM
        self.voltajeLimInferior = vli
        self.voltajeLimSuperior = vls
        self.tiempoMaxBarrido = tmb
        self.iniciaEnCarga = True

        self.corrienteSetNueva = 0  ####

        # atributos tiempo real
        self.PaPromediar = []
        self.ingresos = ingresos  # cantidad de tramas cargadas
        self.barridoActual = barr
        self.corrienteSetActual = corr
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
        if val is 0:
            if self.porenviar is 0:
                # no puedo limpiar un flag ya limpio
                return False
            elif self.porenviar is 1:
                self.porenviar = 0
                return True
            elif self.porenviar is 2:
                # Puede limpiar su propia flag??
                self.porenviar = 0
                return True
            else:
                print "[DCELD][xEnvPS] 1 Necesito Enviar Error"
                return False
        elif val is 1:
            if self.porenviar is 0:
                self.porenviar = 1
                return True
            elif self.porenviar is 1:
                print "[DCELD][xEnvPS] 2 Necesito Enviar Error"
                return False
            elif self.porenviar is 2:
                self.porenviar = 1
                # puerto ya envio y levanto nuevamente
                return True
            else:
                print "[DCELD][xEnvPS] 2 2 Necesito Enviar Error"
                return False
        elif val is 2:
            if self.porenviar is 0:
                # si nadie me levanto el flag no puedo limpiar
                print "[DCELD][xEnvPS] 3 Necesito Enviar Error"
                return False
            elif self.porenviar is 1:
                self.porenviar = 2
                return True
            elif self.porenviar is 2:
                # ya hice ack
                return False
            else:
                print "[DCELD][xEnvPS] 3 3 Necesito Enviar Error"
                return False
        else:
            print "[DCELD][xEnvPS] 4 Necesito Enviar val error"
            return False

    def ActualizoCampos(self, tiempo, voltios, corriente):
        if self.ingresos is 1:
            """primer ingreso"""
            print "[DCELD] primer ingreso " + str(self.ingresos)
            self.ingresos = self.ingresos + 1
            print "[DCELD] sumo ingreso " + str(self.ingresos)
            self.tiempoInicioCiclo = tiempo
            self.ingresos = self.barridoActual = 1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.GuardaCsv()
            ############################################################Inicio Promediado
            return True
        elif self.modo is self.Modos.ciclando:
            """Ciclando"""
            print "[DCELD] ciclando"
            self.ingresos = +1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.segundos = tiempo
            tiempoFinAnteriorBarrido = self.tiempoInicioCiclo + ((self.barridoActual - 1) * self.tiempoMaxBarrido)
            self.tiempoCicloActual = tiempo - tiempoFinAnteriorBarrido
            if self.SuperaLimite() is not 2:
                ############################################################ENVIO
                self.GuardaCsv()
                ############################################################append Promediado
                return True
            else:
                return False
        elif self.modo is self.Modos.voc:
            print "[DCELD] VOC"
            self.ingresos = +1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.segundos = tiempo
            self.tiempoCicloActual = tiempo - self.tiempoInicioCiclo
            if self.SuperaLimite() is not 2:
                ############################################################ENVIO
                self.GuardaCsv()
                ############################################################append Promediado
                return True
            else:
                return False

    def CondicionesDeGuardado(self, barridos, VLS, VLI, TMAX, Corr, Promedio, ComienzaEnCarga):
        BadArgument = 0
        self.ingresos = 1
        if barridos > 0:
            self.barridosMax = barridos * 2  # por la mala definicion original
        else:
            BadArgument = 1
        self.CargaDescarga = ComienzaEnCarga
        if 0 < Promedio > 100:
            self.promediado = Promedio
        else:
            BadArgument = 1
        self.voltajeLimSuperior = VLS
        self.voltajeLimInferior = VLI
        self.tiempoMaxBarrido = TMAX
        if -999999 < Corr > 999999:
            self.corrienteSetActual = Corr
        else:
            BadArgument = 1
        print "[CELD|" + str(self.nombre) + "][CONDGUARD] barridos=" + str(barridos) + ", VLS=" + str(VLS) + ", " \
                                                                                                             "VLI=" + str(
            VLI) + ", TMAX=" + str(TMAX) + ", Corr=" + str(Corr) + ", " \
                                                                   "Promedio=" + str(
            Promedio) + ", ComienzaEnCarga=" + str(ComienzaEnCarga) + ""
        if BadArgument is not 0:
            return False
        else:
            return True

    def SuperaLimite(self):
        if self.milivoltios >= self.voltajeLimSuperior \
                or self.milivoltios <= self.voltajeLimInferior \
                or self.tiempoCicloActual > (self.tiempoInicioCiclo + self.tiempoMaxBarrido):
            print "[DCELD] supere algun extremo"
            if self.barridoActual > self.barridosMax:
                print "[DCELD] termine ciclado"
                self.CerrarCSV()
                self.ResetValCiclado()
                self.porenviar = 0
                return 2
            else:
                print "[DCELD] invierto corriente"
                self.barridoActual = + 1
                self.CargaDescarga = not self.CargaDescarga
                self.porenviar = -1
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
        if self.modo is not self.Modos.voc:
            self.modo = self.Modos.voc
            self.corrienteSetActual = 0
            self.barridosMax = 1
            self.voltajeLimInferior = -99999
            self.voltajeLimSuperior = 99999
            self.promediado = prom
            self.tiempoMaxBarrido = tmax
        else:
            print "[DCELD] esta en modo de barrido de Voltaje a circuito abierto"

    def Activada(self):
        print "[DCELD|" + str(self.nombre) + "] list " + str(self.activa) + " id self " + str(id(self))
        return self.activa

    def CambiaModo(self, modo):
        print "[DCELD|"+str(self.nombre)+"] activ? " + str(self.activa)
        if modo is self.Modos.inactiva:
            self.activa = False
            self.modo = self.Modos.inactiva
            return True
        elif modo is self.Modos.ciclando:
            self.activa = True
            self.modo = self.Modos.ciclando
            return True
        elif modo is self.Modos.voc:
            self.activa = True
            self.modo = self.Modos.voc
            return True
        else:
            return False

    def PararCelda(self):
        if self.modo is not self.Modos.inactiva:
            self.CambiaModo(self.Modos.inactiva)
            self.CerrarCSV()
            self.CondicionesDeGuardado(0, 0, 0, 0, 0, 0.0, True)
            return True
        else:
            print "[DCELD] imposible detener una celda inactiva"
            return False

    def GuardaCsv(self):
        columna = [self.barridoActual, self.milivoltios, self.segundos]
        # [Barrido, Tension, Corriente, Tiempo]
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
        columna = [' ----- ', ' ----- ', ' ----- ', ' ----- ']
        filename = 'Arch_Cn-' + str(self.nombre) + '.csv'
        try:
            open(filename, 'r')
            with open(filename, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna)
                f.close()
        except IOError:
            with open(filename, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(self.encabezadoCSV)
                f_csv.writerow(columna)
                f.close()
