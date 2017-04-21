from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='natural_time',
    version='0.1.9',
    description='Tool for understanding dates and times',
    long_description=long_description,
    url='https://github.com/DavidAmison/natural_time',
    author='David Amison',
    author_email='david.amison20@gmail.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['python-dateutil', 'pathlib', 'textblob'],
)