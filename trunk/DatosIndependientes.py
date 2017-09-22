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
        self.tiempoInicioCiclo = 0
        self.tiempoCiclo = 0
        self.barridoMax = barrM
        self.voltajeLimInferior = vli
        self.voltajeLimSuperior = vls
        self.tiempoMaxBarrido = tmb
        self.iniciaEnCarga = True

        #atributos tiempo real
        self.barridoActual = barr
        self.corriente = corr
        self.milivoltios = milivoltios
        self.microAmperes = microAmperes
        self.segundos = segundos
        #carga = true / descarga = false
        self.CargaDescarga = True

    def isCeldaLibre(self):
        return self.activa

    def GuardoTInicioCiclo(self, tiempo):
        self.tiempoInicioCiclo = tiempo

    def SeteoSentidoInicioCiclado(self, sentido):
        self.iniciaEnCarga = sentido

    def ActualizoCampos(self, tiempo, voltios, corriente):
        self.milivoltios = voltios
        self.microAmperes = corriente
        self.segundos = tiempo

    def SuperaLimite(self):
        if self.milivoltios >= self.voltajeLimSuperior or self.milivoltios <= self.voltajeLimInferior or self.segundos > (self.tiempoInicioCiclo + self.tiempoMaxBarrido):
            print "supere algun extremo"
            if self.barridoActual >= self.barridoMax:
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
        self.tiempoCiclo = 0
        self.barridoMax = 0
        self.voltajeLimInferior = 0
        self.voltajeLimSuperior = 0
        self.tiempoMaxBarrido = 0

    def iniciaCiclado(self):
        if self.modo is not self.Modos.inactiva:
            print 'imposible setear celda no libre'
        else:
            print "inicia ciclado"

    def IniciaVoc(self):
        if self.modo is not self.Modos.voc:
            self.modo = self.Modos.voc
            self.ciclo
            self.voltajeLimInferior = -99999
            self.voltajeLimSuperior = 99999
        else:
            print "está en modo de barrido de Voltaje a circuito abierto"

    def PararCelda(self):
        if self.modo is not self.Modos.inactiva:
            self.modo = self.Modos.inactiva

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
        self.corriente = 1000
        self.barridoMax = 10
        self.voltajeLimSuperior = 999999
        self.voltajeLimInferior = -999999
        self.tiempoMaxBarrido = 12