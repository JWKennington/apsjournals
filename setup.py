"""Setup file
"""


from setuptools import setup, find_packages
from apsjournals import __version__


setup(name='apsjournals',
      version=__version__,
      description='A pythonic interface for APS publications',
      url='http://github.com/JWKennington/apsjournals',
      author='Jim Kennington',
      author_email='jameswkennington@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
