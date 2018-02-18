"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import platform
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup

here = path.abspath(path.dirname(__file__))

reqs = [
    'numpy>=1.14.0',
    'prometheus_client>=0.1.1',
    'flask>=0.12.2',
    'pyserial>=3.4',
    'paho-mqtt>=1.3.1',
    'requests>=2.18.4',
    'imutils>=0.4.5',
]

# Rasberry Pis (ARM devices) and Jetsons don't support opencv-python install through pip
if not platform.uname()[4].startswith('arm') and not platform.uname()[4].startswith('aarch64'):
    reqs.append('opencv-python>=3.4.0.12')

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='arc852-robotics',
    version='1.0.25',
    description='ARC852 Robotic Code',
    url='https://github.com/athenian-robotics/arc852-robotics',
    author='The Athenian School',
    author_email='pambrose@mac.com',

    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='robotics',  # Optional

    packages=['arc852', ],

    install_requires=reqs,
)
