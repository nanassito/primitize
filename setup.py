from configparser import ConfigParser
from datetime import date

import requests
from setuptools import setup
from urllib_ext.parse import urlparse


with open("README.md", "r") as fd:
    long_description = fd.read()


def get_dependencies():
    pipfile = ConfigParser()
    assert pipfile.read("Pipfile"), "Could not read Pipfile"
    return list(pipfile["packages"])


def get_next_version(project: str):
    project_url = urlparse("https://pypi.org/project") / project
    today = date.today()
    version = f"{today:%Y}.{today:%m}.{today:%d}"
    minor = 0
    while requests.get(str(project_url / version)).status_code == 200:
        minor += 1
        version = f"{today:%Y}.{today:%m}.{today:%d}.{minor}"
    return version


setup(
    name="primitize",
    version=get_next_version("primitize"),
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
    install_requires=get_dependencies(),
)
