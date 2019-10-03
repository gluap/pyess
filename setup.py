# coding=utf-8
from setuptools import setup

from pyduofern import __version__ as version

setup(name='pyess',
      version=version,
      description='Library for communicating with LG ESS photovoltaics systems',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',

      ],

      url='https://github.com/gluap/pyess',
      author='Paul Görgen',
      author_email='pypi@pgoergen.de',
      license='MIT',

      packages=['pyess'],

      install_requires=[
          'zeroconf', 'requests'
      ],

      zip_safe=False,
      include_package_data=False,

      tests_require=[
          'tox', 'pytest'
      ],

      entry_points={'console_scripts': ['esscli=pyess.cli:main']},
      long_description=open('README.rst', 'r').read()
      )