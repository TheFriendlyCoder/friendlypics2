"""Class for manipulating the Pinterest pin-dump dialog"""
import logging
from qtpy.QtWidgets import QDialog
from qtpy.QtCore import Slot, SLOT, SIGNAL
from friendlypics2.misc.gui_helpers import load_ui


class PinDumpDialog(QDialog):
    """Dialog for managing the caching of Pinterest pin data"""
    def __init__(self):
        super().__init__()
        self._log = logging.getLogger(__name__)
        self._load_ui()

    def _load_ui(self):
        """Internal helper method that sets up the UI for this dialog"""

        load_ui("pinterest_dump.ui", self)

        self.connect(self.button_box, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(self.button_box, SIGNAL("rejected()"), self, SLOT("reject()"))
        self.refresh_board_button.clicked.connect(self._refresh_board)

    @Slot()
    def _refresh_board(self):
        """Helper method that reloads the list of Pinterest boards and displays the list in a combo box on the UI"""
        self._log("Refreshing...")


if __name__ == "__main__":  # pragma: no cover
    pass
