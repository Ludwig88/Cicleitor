from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("Ciclador",  ["Ciclador.py"]),
    Extension("DatosIndependientes",  ["DatosIndependientes.py"]),
    Extension("DatosIndividualesCelda",  ["DatosIndividualesCelda.py"]),
    Extension("PLOTEOTR",  ["PLOTEOTR.py"]),
    Extension("ProcesoPuerto", ["ProcesoPuerto.py"]),
    Extension("ProcesoPuerto", ["ProcesoPuerto.py"])
    ]

setup(
    name = 'Ciclador',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
    )