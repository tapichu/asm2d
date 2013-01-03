from os.path import dirname, join
from setuptools import setup

def fread(fname):
    return open(join(dirname(__file__), fname)).read()

setup(name = 'asm2d',
      version = '0.1.8',
      description = 'An assembler for the 68112D microprocessor',
      long_description = fread('README.rst'),
      url = 'https://github.com/tapichu/asm2d',
      author = 'Eduardo Lopez Biagi',
      author_email = 'eduardo.biagi@gmail.com',
      license = 'BSD',
      packages = ['asm2d'],
      install_requires = ['ply', 'bitstring'],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Assemblers',
      ],
      keywords = 'asm2d 6811 68HC11 68112d assembler',
      entry_points = {
          'console_scripts': ['asm2d=asm2d.assembler:main'],
      },
      zip_safe = False)
