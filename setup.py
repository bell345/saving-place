#!/usr/bin/env python3

from setuptools import setup, find_packages

from savingplace.version import APP_NAME, APP_VERSION

def read(filename):
    with open(filename) as fp:
        return fp.read()

setup(
    name=APP_NAME,
    version=APP_VERSION,
    packages=find_packages(),
    author="Thomas Bell",
    author_email="tom.aus@outlook.com",
    url="https://github.com/bell345/saving-place",
    description="Recording reddit's /r/place experiment, one pixel at a time.",
    long_description=read("README.rst"),
    install_requires=[
        "beautifulsoup4>=4.5.3",
        "websockets>=3.3",
        "requests>=2.13"
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: No Input/Output (Daemon)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    keywords="reddit place script logging websocket",
    entry_points={
        'console_scripts': [
            'saving-place=savingplace:main'
        ]
    }
)
