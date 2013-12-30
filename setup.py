from distutils.core import setup
from glob import glob
setup(name='lios',
      version='2.0',
      description='Python Distribution Utilities',
      author='Nalin.x.Linux',
      author_email='Nalin.x.Linux@gmail.com',
      url='https://github.com/Nalin-x-Linux/',
      license = 'GPL-3',
      packages=['lios'],
      data_files=[('share/lios',glob('share/lios/ui/*')),('share/lios/Data/',['share/lios/Data/Readme']),('share/applications/',['share/applications/Lios.desktop']),('bin',['bin/lios'])]
      )
