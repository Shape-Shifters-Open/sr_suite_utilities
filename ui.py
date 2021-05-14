# ui.py
# Matt Riche 2021
# Shaper Rigs in-suite UI.


import maya.OpenMayaUI as omui
import pymel.core as pm
# Trust all the following to ship with Maya.
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
# From related modules:
import globals

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class MainDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(MainDialog, self).__init__(parent)
        self.setWindowTitle("Shaper Rigs Suite Utilities v{}".format(globals.srsu_version))
        self.setMinimumWidth(400)

        # Remove help button flag on windows wm.
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()


    def create_widgets(self):

        # Widgets for standard tokens
        pass


    def create_layouts(self):
        pass


    def create_connections(self):
        pass


def run():
    try:
        srsu_main_dialog.close()
        srsu_main_dialog.deleteLater()
    except:
        pass

    srsu_main_dialog = MainDialog()
    srsu_main_dialog.show()
