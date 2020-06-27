from setuptools import setup

setup(
    name='natural_time',
    version='1.2.0',
    licence='MIT',
    description='Tool for understanding dates and times',
    long_description=open('README.md').read(),
    url='https://github.com/DavidAmison/natural_time',
    keywords=['time', 'date', 'natural', 'interpret'],
    author='David Amison',
    author_email='david.amison20@gmail.com',
    packages=['natural_time'],
    install_requires=['python-dateutil', 'pathlib'],
)