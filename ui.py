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
import skeleton
import skinning
import handles
import connections


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
        self.jfc_btn = QtWidgets.QPushButton(self.skeleton_tab)
        self.jfc_btn.setText("Joint from Components")

        # Skinning Tab:
        self.skin_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.skin_tab, "Skinning")
        
        self.copy_sw_btn = QtWidgets.QPushButton(self.skin_tab)
        self.copy_sw_btn.setText("Copy SkinWeights")

        self.find_rs_btn = QtWidgets.QPushButton(self.skin_tab)
        self.find_rs_btn.setText("Find Related Cluster")

        self.select_bj_btn = QtWidgets.QPushButton(self.skin_tab)
        self.select_bj_btn.setText("Select Bound Joints")

        self.harden_btn = QtWidgets.QPushButton(self.skin_tab)
        self.harden_btn.setText("Harden Skin")

        self.save_skin_btn = QtWidgets.QPushButton(self.skin_tab)
        self.save_skin_btn.setText("Save Skin to JSON")

        # Heirachy Tab (Some of this is from "controllers.py")
        self.hierarchy_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.hierarchy_tab, "Hierarchy")

        self.h_create_offset_btn = QtWidgets.QPushButton(self.hierarchy_tab)
        self.h_create_offset_btn.setText("Create Offset")

        # Connections tab
        self.connections_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.connections_tab, "Connections")

        self.h_connect_xforms_btn = QtWidgets.QPushButton(self.connections_tab)
        self.h_connect_xforms_btn.setText("Connect Xform")

        # FKIK Ttab
        self.fkik_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.fkik_tab, "FK/IK")


        self.tools_tab.setCurrentIndex(0)


    def create_layouts(self):

        # Create the skeleton tab layout:
        skeleton_tab_layout = QtWidgets.QFormLayout(self.skeleton_tab)
        skeleton_tab_layout.addRow(self.jfc_btn)

        # Create the skinning tab layout:
        skin_tab_layout = QtWidgets.QFormLayout(self.skin_tab)
        skin_tab_layout.addRow(self.harden_btn)
        skin_tab_layout.addRow(self.save_skin_btn)
        skin_tab_layout.addRow(self.copy_sw_btn)
        skin_tab_layout.addRow(self.find_rs_btn)
        skin_tab_layout.addRow(self.select_bj_btn)

        # Create the Hierarchy tab layout:
        hier_tab_layout = QtWidgets.QFormLayout(self.skin_tab)
        hier_tab_layout.addRow(self.h_create_offset_btn)

        # Create Connections Tab layout:
        connections_tab_layout = QtWidgets.QFormLayout(self.connections_tab)
        connections_tab_layout.addRow(self.h_connect_xforms_btn)


    def create_connections(self):
        self.jfc_btn.clicked.connect(self.ui_joint_from_component)
        self.harden_btn.clicked.connect(self.ui_harden_skin)
        self.copy_sw_btn.clicked.connect(self.ui_copy_skinweights)
        self.find_rs_btn.clicked.connect(self.ui_find_related_cluster)
        self.select_bj_btn.clicked.connect(self.ui_find_related_joints)
        self.h_create_offset_btn.clicked.connect(self.ui_create_offset)
        self.h_connect_xforms_btn.clicked.connect(self.ui_connect_xform)


    # UI commands:

    def ui_joint_from_component(self):
        print ("UI call for skeleton.joint_from_components()")
        skeleton.joint_from_components()

    def ui_harden_skin(self):
        print ("UI call for skinning.harden()")
        skinning.harden()

    def ui_copy_skinweights(self):
        print ("UI call for skinning.copy_skinweights()")
        skinning.copy_skinweights()

    def ui_find_related_cluster(self):
        print ("UI call for skinning.find_related_skinCluster()")
        skinning.find_related_skinCluster()

    def ui_find_related_joints(self):
        print ("UI call for skinning.select_bound_joints()")
        skinning.select_bound_joints()

    def ui_create_offset(self):
        print ("UI call for handles.create_offset()")
        handles.create_offset()

    def ui_connect_xform(self):
        print ("UI call for connections.connect_xforms()")
        connections.connect_xforms()

    
def run():
    try:
        srsu_main_dialog.close()
        srsu_main_dialog.deleteLater()
    except:
        pass

    srsu_main_dialog = MainDialog()
    srsu_main_dialog.show()
