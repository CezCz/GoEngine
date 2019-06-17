from distutils.core import setup
from Cython.Build import cythonize

setup(name='go',
      ext_modules=cythonize("go.pyx"))