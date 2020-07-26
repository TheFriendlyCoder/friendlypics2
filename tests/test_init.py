from friendlypics2.version import __version__


def test_version():
    assert isinstance(__version__, str)
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all([i.isnumeric() for i in parts])
