"""Helper functions to perform various application level operations"""
import sys
from pathlib import Path


def is_mac_app_bundle():
    """bool: Checks to see if the application is running under a MacOS app bundle"""
    # when running in an app bundle, the relative path to the application will look something like this
    #       ./fpics2.app/Contents/MacOS/fpics2
    cur_path = Path(sys.executable).parent
    if cur_path.name != "MacOS":
        return False
    if cur_path.parent.name != "Contents":
        return False
    if cur_path.parent.parent.name != "fpics2.app":
        return False
    return True


def is_pyinstaller_bundle():
    """bool: Checks to see if the application is running under a pyinstaller bundle"""
    # TIP: when running in a frozen environment, you can retrieve the path
    # to the temporary folder pyinstaller creates when running the app using the
    # following meta-variable:
    #       sys._MEIPASS
    return hasattr(sys, 'frozen')


if __name__ == "__main__":  # pragma: no cover
    pass
