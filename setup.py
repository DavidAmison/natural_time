from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='natural_time',
    version='1.1.8',
    description='Tool for understanding dates and times',
    long_description=long_description,
    url='https://github.com/DavidAmison/natural_time',
    author='David Amison',
    author_email='david.amison20@gmail.com',
    packages=['natural_time'],
    install_requires=['python-dateutil', 'pathlib', 'textblob'],
)