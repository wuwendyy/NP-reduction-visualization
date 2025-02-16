from setuptools import setup, find_packages

setup(
    name="element",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pygame",
        "networkx",
        "matplotlib",
        "numpy",
    ],
)
