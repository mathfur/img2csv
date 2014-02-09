#from distutils.core import setup
from setuptools import setup

setup(
  name = 'img2csv',
  packages = ['img2csv'],
  version = '0.0.0',
  description = 'input image, output csv',
  author='mathfur',
  install_requires=open('requirements.txt').read().splitlines(),
  entry_points="""
  [console_scripts]
  img2csv = img2csv.runner:run_img2csv
  """
)
