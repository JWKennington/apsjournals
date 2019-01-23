"""Setup file
"""


import setuptools
import apsjournals


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(name='apsjournals',
                 version=apsjournals.__version__,
                 description='A pythonic interface for APS publications',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url='http://github.com/JWKennington/apsjournals',
                 author='James W. Kennington',
                 author_email='jameswkennington@gmail.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 zip_safe=False)
