# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="tws3",
    version="0.1.0",
    description="Tws3 Nscm Assignment",
    long_description=readme,
    author="Théo Pomies",
    author_email="theo.pomies@outlook.com",
    url="https://github.com/theopomies/tws-assignment-3",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
