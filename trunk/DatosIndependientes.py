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
        self.porenviar = False
        self.tiempoInicioCiclo = 0
        self.tiempoCicloActual = 0
        self.barridosMax = barrM
        self.voltajeLimInferior = vli
        self.voltajeLimSuperior = vls
        self.tiempoMaxBarrido = tmb
        self.iniciaEnCarga = True

        self.corrienteSetNueva = 0 ####

        #atributos tiempo real
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

    def NecesitoEnviar(self, corr):
        if self.porenviar is not True:
            self.porenviar = True
            self.corrienteSetActual = corr
        else:
            print "Datos Independientes - ya pedi enviar previamente"

    def SeteoSentidoInicioCiclado(self, sentido):
        self.iniciaEnCarga = sentido

    def ActualizoCampos(self, tiempo, voltios, corriente):
        self.ingresos+=1
        self.milivoltios = voltios
        self.microAmperes = corriente
        self.segundos = tiempo
        self.GuardaCsv()

    def CondicionesDeGuardado(self, barridos, VLS, VLI, TMAX, Corr, Promedio):
        print "condiciones de guardado"
        self.promediado = Promedio
        self.barridosMax = barridos * 2 #por la mala definicion original
        self.voltajeLimSuperior = VLS
        self.voltajeLimInferior = VLI
        self.tiempoMaxBarrido = TMAX
        self.corrienteSetActual = Corr

    def PrimerIngreso(self):
        if self.ingresos is None:
            return True
        else:
            return False

    def SuperaLimite(self):
        if self.milivoltios >= self.voltajeLimSuperior or self.milivoltios <= self.voltajeLimInferior or self.segundos > (self.tiempoInicioCiclo + self.tiempoMaxBarrido):
            print "supere algun extremo"
            if self.barridoActual >= self.barridosMax:
                print "termine ciclado"
                self.CerrarCSV()
                self.ResetValCiclado()
            else:
                print "invierto corriente"
                self.CargaDescarga = not self.CargaDescarga
            return True
        else:
            return False

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
            #limpiar las variables de seteo, cerrar archivo
            #enviar corriente cero
            # adicionar mandar i=0 para cuando para celda usar por setear en 0
            self.CerrarCSV()
            # self.ActualizoCondGuardado(Celda,False,0.0)
            # ActualizoMatriz(Celda,0,0,0,1,0)
            # barridos 0 y corriente 0 y tiempoMax mayor a cero pero minimo
            #PorSetear = Celda  # para finalizar hago barridos de seteo como 0 (el resto me da lo mismo?)
            # luego la lectura me reinicia cond de seteo y pa barrer
            # eso me hace cerrar el archivo
            # y en proceso me actuliza cond de guardado a ['cel',False, 0]

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
    # fila = deque(maxlen=16000)
    # self.threadPool.append(ProcesoPuerto.LECTURA(fila, self.filaPloteo, Datos))
    # self.connect(self.threadPool[len(self.threadPool)-1],
    #              self.threadPool[len(self.threadPool)-1].signal,
    #              self.ActualValores)

    def xIsSeted(self, num):
        if num is "a" or 1:
            print 'slfdlfksdlfksd'
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
            print "error"

    def xEnviarPS(self, cel, corr):
        getattr('self.'+str(cel),'NecesitoEnviar')(corr)

    def PrimerInicio(self):
        print "arranco el thread del puerto"
        # self.threadPool[len(self.threadPool)-1].start()
        # time.sleep(0.5)
        # # inicio procesamiento
        # self.threadPool.append(PROCESO(fila))
        # self.threadPool[len(self.threadPool)-1].start()