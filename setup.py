import pathlib
from setuptools import setup,find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="pyz3multi",
    version="0.0.1",
    author="Thomas Prescott",
    author_email="tcprescott@gmail.com",
    description="A python module for interacting with the ALTTPR multiworld service.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tcprescott/pyz3multi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=['websockets'],
)