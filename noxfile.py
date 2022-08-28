import nox
from nox_poetry import session
import tempfile

locations = "src", "noxfile.py"

# this is from hypermodern python. Not sure if this will be usefule.
def install_with_constraints(session, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)

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

@nox.session(python="3.9")
def docs(session) -> None:
    """Build the documentation."""
    install_with_constraints(session, "sphinx", "sphinx-rtd-theme", ".")
    session.run("sphinx-build", "docs", "docs/build")
