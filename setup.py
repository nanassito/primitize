from configparser import ConfigParser
from datetime import date

from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from setuptools import setup


with open("README.md", "r") as fd:
    long_description = fd.read()


def get_dependencies():
    pipfile = ConfigParser()
    assert pipfile.read("Pipfile"), "Could not read Pipfile"
    return list(pipfile["packages"])


def project_version_exists(project, version):
    project_url = f"https://pypi.org/project/{project}"
    try:
        return urlopen(f"{project_url}/{version}").status == 200
    except (HTTPError, URLError):
        return False


def get_next_version(project: str):
    today = date.today()
    version = f"{today:%Y}.{today:%m}.{today:%d}"
    minor = 0
    while project_version_exists(project, version):
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
    packages={
        "primitize": ["primitize"],
    },
    package_data={
        "primitize": ["py.typed"],
    },
    test_suite="unittests",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=get_dependencies(),
)
