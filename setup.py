import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system.
sys.path.pop(0)
from setuptools import setup

setup(name='micropython-rfsocket',
      version='0.1',
      description='rfsocket module for MicroPython ',
      long_description="This is a module implemented specifically for MicroPython.",
      url='https://github.com/wuub/micropython-rfsocket',
      author='Wojciech Bederski',
      author_email='github@wuub.net',
      license='MIT',
      py_modules=['rfsocket'])
