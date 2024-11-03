from setuptools import setup, find_packages

setup(
   name='branalysis',
   version='1.0.10',
   description='Coleta e facilita a análise de votações nominais do Congresso Nacional',
   long_description=open('README.md').read(),
   long_description_content_type='text/markdown',
   author='Mateus Arns Kreuch',
   author_email='mateus.kreuch@grad.ufsc.br',
   url='https://github.com/mateuskreuch/branalysis',
   packages=find_packages(),
   classifiers=[
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent',
      'Topic :: Scientific/Engineering :: Information Analysis',
      'Topic :: Scientific/Engineering :: Visualization',
      'Topic :: Sociology',
      'Intended Audience :: Developers',
      'Intended Audience :: Science/Research',
      'Natural Language :: Portuguese (Brazilian)',
   ],
   install_requires=[
      "numpy",
      "peewee",
      "Requests",
   ],
   python_requires='>=3.9',
)
