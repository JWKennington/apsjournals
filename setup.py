"""Setup file
"""


import setuptools
import apsjournals


setuptools.setup(name='apsjournals',
                 version=apsjournals.__version__,
                 description='A pythonic interface for APS publications',
                 url='http://github.com/JWKennington/apsjournals',
                 author='James W. Kennington',
                 author_email='jameswkennington@gmail.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 zip_safe=False)
