import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="conrad_relaycard",
    version="0.2",
    description="Library and commandline tool to control Conrad relay cards.",
    long_description=read("README.rst"),
    author="Stephan Jaekel",
    author_email="steph@rdev.info",
    url="https://github.com/stephrdev/conrad-relaycard/",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["pyserial"],
    entry_points={
        "console_scripts": ["conrad-relaycard=conrad_relaycard.cli:main"],
    },
    python_requires=">=3.7",
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
