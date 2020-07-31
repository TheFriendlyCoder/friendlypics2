"""Logic for the application about box"""
import logging
from qtpy.QtWidgets import QDialog, QLabel
from friendlypics2.version import __version__
from friendlypics2.misc.gui_helpers import load_ui
from friendlypics2.misc.app_helpers import is_mac_app_bundle, is_pyinstaller_bundle


class AboutDialog(QDialog):
    """Logic for managing about box"""
    def __init__(self, parent):
        super().__init__(parent)
        self._log = logging.getLogger(__name__)
        self.setWindowTitle("About...")
        self.setModal(True)
        self._load_ui()

    def _load_ui(self):
        """Internal helper method that configures the UI for the main window"""
        load_ui("about_dlg.ui", self)
        self.title_label = self.findChild(QLabel, "title_label")
        self.title_label.setText("Friendly Pics 2 v" + __version__)

        self.runtime_env_label = self.findChild(QLabel, "runtime_env_label")
        if is_mac_app_bundle():
            self.runtime_env_label.setText("Running as MacOS app bundle")
        elif is_pyinstaller_bundle():
            self.runtime_env_label.setText("Running as a pyinstaller binary")
        else:
            self.runtime_env_label.setText("Running under conventional Python environment")

        # Center the about box on the parent window
        parent_geom = self.parent().geometry()
        self.move(parent_geom.center() - self.rect().center())
