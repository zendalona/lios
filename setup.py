from distutils.core import setup
from glob import glob
setup(name='lios',
      version='2.0',
      description='Python Distribution Utilities',
      author='Nalin.x.Linux',
      author_email='Nalin.x.Linux@gmail.com',
      url='https://github.com/Nalin-x-Linux/',
      license = 'GPL-3',
      packages=['lios','lios/ocr','lios/scanner','lios/ui/','lios/ui/gtk'],
      data_files=[('share/lios/',['share/lios/readme.text','share/lios/lios.png']),('share/applications/',['share/applications/Lios.desktop']),('share/man/man1/',['share/man/man1/lios.1.gz']),('share/doc/lios/',['share/doc/lios/copyright']),('share/pixmaps/',['share/pixmaps/lios.xpm']),('bin',['bin/lios'])]
      )
# sudo python3 setup.py install --install-data=/usr
