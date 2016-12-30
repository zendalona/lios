from distutils.core import setup
from glob import glob
setup(name='lios',
      version='2.5',
      description='Easy-OCR solution and Tesseract trainer for GNU/Linux',
      author='Nalin.x.Linux',
      author_email='nalin.x.Linux@gmail.com',
      url='https://gitlab.com/Nalin-x-Linux/lios-3',
      license = 'GPL-3',
      packages=['lios','lios/ocr','lios/scanner','lios/ui/','lios/ui/gtk'],
      data_files=[('share/lios/',['share/lios/readme.text','share/lios/text_cleaner_list.text','share/lios/lios.png']),
      ('share/applications/',['share/applications/Lios.desktop','share/applications/Tesseract-Trainer.desktop']),
      ('share/man/man1/',['share/man/man1/lios.1.gz','share/man/man1/train-tesseract.1.gz']),
      ('share/doc/lios/',['share/doc/lios/copyright']),('share/pixmaps/',['share/pixmaps/lios.xpm']),
      ('bin',['bin/lios','bin/train-tesseract'])]
      )
# sudo python3 setup.py install --install-data=/usr
