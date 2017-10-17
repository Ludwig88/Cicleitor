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
from collections import deque
#import ProcesoPuerto


class DatosCelda:

    class Modos:
        inactiva, ciclando, voc = range(3)

    encabezadoCSV = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ']

    def __init__(self, nomb, act=False,
                 prom=0.0, barr=0, barrM=0, vli=0,
                 vls=0, corr=0, tmb=0,
                 milivoltios=0, microAmperes=0,
                 segundos=0):

        #atributos de 1 sola vez
        self.nombre = nomb
        self.promediado = prom
        #activa puede sacarse a cambio de leer un modo distinto a cero
        self.activa = act
        self.modo = self.Modos.inactiva

        #atributos para procesos de extremo
        self.porenviar = 0 #0=nada por hacer, 1=enviar algo, 2, ack de envio
        self.tiempoInicioCiclo = 0
        self.tiempoCicloActual = 0
        self.barridosMax = barrM
        self.voltajeLimInferior = vli
        self.voltajeLimSuperior = vls
        self.tiempoMaxBarrido = tmb
        self.iniciaEnCarga = True

        self.corrienteSetNueva = 0 ####

        #atributos tiempo real
        self.PaPromediar = []
        self.ingresos = 0 #cantidad de tramas cargadas
        self.barridoActual = barr
        self.corrienteSetActual = corr
        self.milivoltios = milivoltios
        self.microAmperes = microAmperes
        self.segundos = segundos
        #carga = true / descarga = false
        self.CargaDescarga = True

    def GuardoTInicioCiclo(self, tiempo):
        self.tiempoInicioCiclo = tiempo

    """
       val=0: disponible para cambiar (solo Port)
       val=1: Tengo q enviar (ui a port)
       val=2: Ya envie Port a UI
    """
    def NecesitoEnviar(self, val):
        if val is 0:
            if self.porenviar is 0:
                #no puedo limpiar un flag ya limpio
                return False
            elif self.porenviar is 1:
                self.porenviar = 0
                return True
            elif self.porenviar is 2:
                #Puede limpiar su propia flag??
                self.porenviar = 0
                return True
            else:
                print "1Necesito Enviar Error"
                return False
        elif val is 1:
            if self.porenviar is 0:
                self.porenviar = 1
                return True
            elif self.porenviar is 1:
                print "2Necesito Enviar Error"
                return False
            elif self.porenviar is 2:
                self.porenviar = 1
                #puerto ya envio y levanto nuevamente
                return True
            else:
                print "22Necesito Enviar Error"
                return False
        elif val is 2:
            if self.porenviar is 0:
                #si nadie me levanto el flag no puedo limpiar
                print "3Necesito Enviar Error"
                return False
            elif self.porenviar is 1:
                self.porenviar = 2
                return True
            elif self.porenviar is 2:
                #ya hice ack
                return False
            else:
                print "33Necesito Enviar Error"
                return False
        else:
            print "4Necesito Enviar val error"
            return False

    def SeteoSentidoInicioCiclado(self, sentido):
        #no hace falta???
        self.iniciaEnCarga = sentido

    def ActualizoCampos(self, tiempo, voltios, corriente):
        if self.modo is self.Modos.inactiva:
            print "actualizo campos"
            """primer ingreso"""
            self.modo = self.Modos.ciclando
            self.tiempoInicioCiclo = tiempo
            self.ingresos = self.barridoActual = 1
            self.microAmperes = corriente
            self.milivoltios = voltios
            self.GuardaCsv()
            return True
            ############################################################Inicio Promediado
        #no va a ser necesario!
        # elif voltios == corriente == '%':
        #     print 'finalizo ciclado por forzado'
        #     self.ResetValCiclado()
        #     self.CerrarCSV()
        #     return False



        # if BARRIDO % 2 == 0:
        #     Descarga = True
        # else:
        #     Descarga = False



        elif self.modo is self.Modos.ciclando:
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
        if barridos >= 0:
            self.barridosMax = barridos * 2  # por la mala definicion original
            # hacer filtro de valores correctos
            self.CargaDescarga = ComienzaEnCarga
            self.promediado = Promedio
            self.voltajeLimSuperior = VLS
            self.voltajeLimInferior = VLI
            self.tiempoMaxBarrido = TMAX
            self.corrienteSetActual = Corr
            print "-COndGuard- barridos="+str(barridos)+", VLS="+str(VLS)+", " \
                  "VLI="+str(VLI)+", TMAX="+str(TMAX)+", Corr="+str(Corr)+", " \
                  "Promedio="+str(Promedio)+", ComienzaEnCarga="+str(ComienzaEnCarga)+""
            return True
        else:
            #especificar que dio mal para informarlo
            return False

    def PrimerIngreso(self):
        if self.ingresos is None:
            return True
        else:
            return False

    def SuperaLimite(self):
        if self.milivoltios >= self.voltajeLimSuperior \
           or self.milivoltios <= self.voltajeLimInferior \
           or self.tiempoCicloActual > (self.tiempoInicioCiclo + self.tiempoMaxBarrido):
            print "supere algun extremo"
            if self.barridoActual > self.barridosMax:
                print "termine ciclado"
                self.CerrarCSV()
                self.ResetValCiclado()
                self.porenviar = 0
                return 2
            else:
                print "invierto corriente"
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

    def Ciclar(self):
        if self.modo is not self.Modos.inactiva:
            print 'Datos Independientes - imposible setear celda no libre'
        else:
            if self.PrimerIngreso():
                self.GuardoTInicioCiclo()
            self.GuardaCsv()

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
            print "esta en modo de barrido de Voltaje a circuito abierto"

    def PararCelda(self):
        if self.modo is not self.Modos.inactiva:
            self.modo = self.Modos.inactiva
            self.activa = False
            self.CerrarCSV()
            self.CondicionesDeGuardado(0, 0, 0, 0, 0, 0.0, True)
            # ActualizoMatriz(Celda,0,0,0,1,0)
            # barridos 0 y corriente 0 y tiempoMax mayor a cero pero minimo
            #PorSetear = Celda  # para finalizar hago barridos de seteo como 0 (el resto me da lo mismo?)
            # luego la lectura me reinicia cond de seteo y pa barrer
            # eso me hace cerrar el archivo
            # y en proceso me actuliza cond de guardado a ['cel',False, 0]
            return True
        else:
            print "imposible detener una celda inactiva"
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

    def ValoresPaTest(self):
        self.promediado = 100
        self.corrienteSetActual = 1000
        self.barridosMax = 10
        self.voltajeLimSuperior = 999999
        self.voltajeLimInferior = -999999
        self.tiempoMaxBarrido = 12


class DatosCompartidos:

    PoolThread = []
    celdasAenviar = []
    filaPloteo = deque(maxlen=16000)

    def __init__(self):
        self.a = DatosCelda("a") #1
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

        # # inicio lectura
        #print "arranco thread de lectura desde DatosIndependientes"
        #self.PoolThread.append(ProcesoPuerto.LECTURA(self.filaPloteo))

    def xIsActive(self, num):
        if num is "a" or 1:
            return self.a.activa
        elif num is "b" or 2:
            return self.b.activa
        elif num is "c" or 3:
            return self.c.activa
        elif num is "d" or 4:
            return self.d.activa
        elif num is "e" or 5:
            return self.e.activa
        elif num is "f" or 6:
            return self.f.activa
        elif num is "g" or 7:
            return self.g.activa
        elif num is "h" or 8:
            return self.h.activa
        elif num is "i" or 9:
            return self.i.activa
        elif num is "j" or 10:
            return self.j.activa
        elif num is "k" or 11:
            return self.k.activa
        elif num is "l" or 12:
            return self.l.activa
        elif num is "m" or 13:
            return self.m.activa
        elif num is "n" or 14:
            return self.n.activa
        elif num is "o" or 15:
            return self.o.activa
        elif num is "p" or 16:
            return self.p.activa
        else:
            print "datos independientes - Atrib error"

    def xCondicionesDeGuardado(self, num, ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga):
        if num is "a" or 1:
            if (self.a.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "b" or 2:
            if (self.b.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "c" or 3:
            if (self.c.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "d" or 4:
            if (self.d.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "e" or 5:
            if (self.e.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "f" or 6:
            if (self.f.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "g" or 7:
            if (self.g.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "h" or 8:
            if (self.h.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "i" or 9:
            if (self.i.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "j" or 10:
            if (self.j.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "k" or 11:
            if (self.k.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "l" or 12:
            if (self.l.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "m" or 13:
            if (self.m.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "n" or 14:
            if (self.n.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "o" or 15:
            if (self.o.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        elif num is "p" or 16:
            if (self.p.CondicionesDeGuardado(ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaoDescarga)) is True:
                return True
            else:
                return False
        else:
            print "error"
            return False

    def enColaPorEnviar(self):
        return self.celdasAenviar.__len__()

    def xEnviarPS(self, num, val):
        print "longitud de cola de envio es " + str(self.enColaPorEnviar())
        print "num y val " + str(num) + "  " + str(val)
        if num is "a" or 1:
            if (self.a.NecesitoEnviar(val)) is True:
                if val is 1:
                    self.celdasAenviar.extend(str(num))
                elif val is 2:
                    print "popeo"
                    self.celdasAenviar.pop(0)
                print "DInd - x por enviar -- por enviar corriente"
                return True
            else:
                print "DInd - x por enviar - no se pudo enviar corriente"
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

    def xIniciaVoc(self, num, Promedio, T_Max):
        if (self.xCondicionesDeGuardado(num, 1, 9999, -9999, T_Max, 0, Promedio, True)) is True:
            print "DInd - actualizadas condiciones de guardado"
        else:
            print "DInd - no pudo actualizar condiciones de guardado"

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
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "c" or 3:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "d" or 4:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "e" or 5:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "f" or 6:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "g" or 7:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "h" or 8:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "i" or 9:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "j" or 10:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "k" or 11:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "l" or 12:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "m" or 13:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "n" or 14:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "o" or 15:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
        elif num is "p" or 16:
            return self.a.ActualizoCampos(tiempo, tension, corriente)
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
        if num is "a" or 1:
            celda = self.celdasAenviar[self.enColaPorEnviar()-1]
            corriente, a, b, c, d, e = self.xGetCondGuardado(num)
            print "xget por setear " + str(celda) + "  " + str(corriente)
            return celda, corriente
            """
            elif num is "b" or 2:
                return self.b.activa
            elif num is "c" or 3:
                return self.c.activa
            elif num is "d" or 4:
                return self.d.activa
            elif num is "e" or 5:
                return self.e.activa
            elif num is "f" or 6:
                return self.f.activa
            elif num is "g" or 7:
                return self.g.activa
            elif num is "h" or 8:
                return self.h.activa
            elif num is "i" or 9:
                return self.i.activa
            elif num is "j" or 10:
                return self.j.activa
            elif num is "k" or 11:
                return self.k.activa
            elif num is "l" or 12:
                return self.l.activa
            elif num is "m" or 13:
                return self.m.activa
            elif num is "n" or 14:
                return self.n.activa
            elif num is "o" or 15:
                return self.o.activa
            elif num is "p" or 16:
                return self.p.activa
            """
        else:
            print "datos independientes - Atrib error"
            return None, None


    def AllDisable(self):
        algunaActiva = (self.a.activa or self.b.activa or self.c.activa or self.d.activa or
            self.e.activa or self.f.activa or self.g.activa or self.h.activa or
            self.i.activa or self.j.activa or self.k.activa or self.l.activa or
            self.m.activa or self.n.activa or self.o.activa or self.o.activa)
        return algunaActiva
