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
        self.setMinimumHeight(200)

        # Remove help button flag on windows wm.
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        

    def create_widgets(self):
        
        # Prep tabs:
        self.tools_tab = QtWidgets.QTabWidget(self)
        self.tools_tab.setGeometry(QtCore.QRect(20, 20, 371, 361))
        self.tools_tab.setAutoFillBackground(False)

        # Make the skeleton tab
        self.skeleton_tab = QtWidgets.QWidget()
        # self.tools_tab.setTabText(self.tools_tab.indexOf(self.skeleton_tab), "Skeleton")
        self.tools_tab.addTab(self.skeleton_tab, "Skeleton")

        self.skin_tab = QtWidgets.QWidget()
        #self.tools_tab.setTabText(self.tools_tab.indexOf(self.skin_tab), "Skinning")
        self.tools_tab.addTab(self.skin_tab, "Skinning")


        self.tools_tab.setCurrentIndex(0)


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
