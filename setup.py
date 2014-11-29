from distutils.core import setup
import io
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with io.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Tabipy',
    version='0.1',
    description='Construct tables for rich display in IPython.',
    long_description=long_description,
    url='https://github.com/takluyver/tabipy',

    # Author details
    author='Thomas Kluyver, Christian Alis',
    author_email='thomas@kluyver.me.uk, ianalis@gmail.com',

    # Choose your license
    license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='table ipython notebook latex',

    py_modules=['tabipy'],
)
