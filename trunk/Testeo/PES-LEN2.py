import serial
import time
import csv
import string

encabezadoCSV = ['TEST']

def SeteoPuerto():
    global ser
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = '/dev/ttyUSB0' #
    ser.bytesize = 8
    ser.stopbits = 1
    ser.timeout = 0.1
    ser.parity = 'N'
    #print "el puerto se configura " + str(ser)
    ser.open()
    return ser

def RecibirPS():
  s = ser.readline()
  s = s[:len(s)-1]
  return s

def GuardaCsv(entrada):
    fileName = 'Archivo_Test_LEN2.csv'
    try:
        open(fileName, 'r')
        with open(fileName, 'a') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(entrada)
            f.close()
    except IOError:
        with open(fileName, 'w+') as f:
            f_csv = csv.writer(f)
            f_csv.writerow(encabezadoCSV)
            f_csv.writerow(entrada)
            f.close()

def NumDeCelda(celda):
 for i in range(len(string.ascii_letters)):
    if celda == string.ascii_letters[i]:
        return i
        break

def EnviarPS_I(ua, Descarga, celda):
    # I=0 con uA=0 en cualquier descarga
    # 2 unidades = 1uA 2048 =0A
    # global ser
    # print ser
    print 'ua: ' + str(ua) + ' ' + str(type(ua)) + 'Descarga: ' + str(Descarga) + ' ' + str(
        type(Descarga)) + 'Celda: ' + str(celda) + ' ' + str(type(celda))
    MatConv = [['h', 2], ['f', 2], ['d', 2], ['b', 2], ['h', 1], ['f', 1], ['d', 1], ['b', 1], ['e', 2], ['g', 2],
               ['a', 2], ['c', 2], ['e', 1], ['g', 1], ['a', 1], ['c', 1]]
    # cada renglon es el orden en asccii, dentro la primer columna es el caracter dentro del dac cuyo numero es la otra
    if Descarga:
        num = int(2048 - (ua * 2))
    else:
        num = int((ua * 2) + 2048)
    #print 'numero a enviar__: ' + str(num)
    if num >= 0 and num <= 4095:
        mil = num / 1000
        cien = (num - mil * 1000) / 100
        die = (num - mil * 1000 - cien * 100) / 10
        un = (num - mil * 1000 - cien * 100 - die * 10)
        ser.write('i')
        ser.write(str(mil))  # 1
        ser.write(str(cien))  # 2
        ser.write(str(die))  # 3
        ser.write(str(un))  # 4
        ser.write(str(MatConv[NumDeCelda(str(celda))][0]))
        ser.write(str(MatConv[NumDeCelda(str(celda))][1]))
        ser.write('f')
        ser.flushInput()
    else:
        print 'numero incorrecto'

if __name__=="__main__":
 global ser
 ser = SeteoPuerto()
 count = 0
 EnviarPS_I(0,True,'b')
 while count < 10000:
     time.sleep(0.00001)
     count = count + 1
     recepcion = RecibirPS() + '#' + str(time.time() - 1500000000)
     separado = recepcion.split('#', 4)
     #print "recepcion:: "+str(separado)
     print ".",
     GuardaCsv(separado)
 print
 print "PROCESO FINALIZADO"