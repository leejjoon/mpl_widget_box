import nox
from nox_poetry import session

locations = "src", "noxfile.py"


@nox.session(python="3.9")
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session(python=["3.9"])
def lint(session):
    args = session.posargs or locations
    session.install("flake8")
    session.run("flake8", *args)


@session(python=["3.7", "3.8", "3.9", "3.10"])
def tests(session):
    session.install("pytest", ".")
    session.run("pytest")
