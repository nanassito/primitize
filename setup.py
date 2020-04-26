from setuptools import setup
from configparser import ConfigParser


with open("README.md", "r") as fd:
    long_description = fd.read()


pipfile = ConfigParser()
assert pipfile.read("Pipfile"), "Could not read Pipfile"



setup(
    name="primitize",
    version="1.0",
    author="Dorian Jaminais",
    author_email="primitize@jaminais.fr",
    description="Primitize is a library that facilitates converting dataclass instances into primitive objects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nanassito/primitize",
    packages=["primitize"],
    test_suite="unittests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=list(pipfile["packages"]),
)
