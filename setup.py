import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="relaycard",
    version="0.1",
    description="Library and commandline tool to control Conrad relay cards.",
    long_description=read("README.md"),
    author="Stephan Jaekel",
    author_email="steph@rdev.info",
    url="https://github.com/stephrdev/relaycard/",
    packages=find_packages(),
    scripts=[
        "bin/relaycard-cli",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False,
)
