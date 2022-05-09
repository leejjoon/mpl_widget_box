import nox

locations = "src", "noxfile.py"


@nox.session(python="3.10")
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)
