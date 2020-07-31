"""GUI dialog defining behavior of main application window"""
import logging

from qtpy.QtWidgets import QMainWindow
from qtpy.QtCore import Slot
from qtpy.QtGui import QKeySequence

from friendlypics2.misc.gui_helpers import load_ui
from friendlypics2.misc.app_helpers import is_mac_app_bundle
from friendlypics2.dialogs.about_dlg import AboutDialog


class MainWindow(QMainWindow):
    """Main window interface"""
    def __init__(self):
        super().__init__()
        self._log = logging.getLogger(__name__)
        self.setWindowTitle("Friendly Pics")
        self.statusBar().showMessage('Ready')
        self._load_ui()

    def _load_ui(self):
        """Internal helper method that configures the UI for the main window"""
        load_ui("main_window.ui", self)

        self.file_open_menu.triggered.connect(self.file_open_click)
        self.file_open_menu.setShortcut(QKeySequence.Open)
        self.help_about_menu.triggered.connect(self.help_about_click)

        # Hack: for testing on MacOS we convert menu bar to non native
        #       works around the bug where native menu bar on Mac is read only on app launch
        #       problem is non existent when running app from a .app package
        #       (ie: as generated by pyinstaller)
        if not is_mac_app_bundle():
            self.menuBar().setNativeMenuBar(False)

    @Slot()
    def file_open_click(self):
        """callback for file-open menu"""
        self._log.debug("Opening...")

    @Slot()
    def help_about_click(self):
        """callback for the help-about menu"""
        dlg = AboutDialog(self)
        dlg.exec_()

    def closeEvent(self, _event):  # pylint: disable=invalid-name
        """event handler called when the application is about to close"""
        # TODO: check for unsaved work
        self._log.debug("Shutting down")
        # if True:
        #     event.accept()
        # else:
        #     event.ignore()


if __name__ == "__main__":  # pragma: no cover
    pass