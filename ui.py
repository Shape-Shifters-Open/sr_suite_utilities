# ui.py
# Matt Riche 2021
# Shaper Rigs in-suite UI.

from pymel.core.datatypes import Vector
import maya.OpenMayaUI as omui
import pymel.core as pm
import sys
# Trust all the following to ship with Maya.
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import gc


# From related modules:


import skeleton
import globals
import skinning
import handles
import connections
import dict_lib
import all_control_options
import orientation
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):

    #storing current instance in a variable
    instance = None

    def __init__(self, parent=maya_main_window(), **kwargs):

        #calling function to check for current instance and delete it
        self.delete_instance()
        self.__class__.instance = self

        super(MainDialog, self).__init__(parent, **kwargs)
        self.setWindowTitle("Shaper Rigs Suite Utilities v0.1.07")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        

        # Remove help button flag on windows wm.
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        return

    def delete_instance(self):
        """looks for currente existing instance and deletes it"""
        if self.__class__.instance is not None:
            try:
                self.__class__.instance.close()
                self.__class__.instance.deleteLater()
            except Exception as e:
                pass
        
        return


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

        #      adding dumb copy orient
        self.dumb_copy_orient_btn = QtWidgets.QPushButton(self.skeleton_tab)
        self.dumb_copy_orient_btn.setText("dumb copy orient")

        #      adding smart copy orient
        self.smart_copy_orient_btn = QtWidgets.QPushButton(self.skeleton_tab)
        self.smart_copy_orient_btn.setText("smart copy orient")

        # Skinning Tab:
        self.skin_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.skin_tab, "skinning")

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

        #     add driver attribute prompt  and textbox
        self.h_input_driver_txtbox = QtWidgets.QLabel(self.connections_tab)
        self.h_input_driver_txtbox.setText("Input Driver Attribute")
        self.get_driver = QtWidgets.QLineEdit(self.connections_tab)
        self.get_driver.move(150, 36)
        self.get_driver.resize(200, 20)

        #     add driven attribute prompt and textbox
        self.h_input_driven_txtbox = QtWidgets.QLabel(self.connections_tab)
        self.h_input_driven_txtbox.setText("Input Driven Attributes")
        self.get_driven = QtWidgets.QLineEdit(self.connections_tab)
        self.get_driven.move(150, 57)
        self.get_driven.resize(210, 20)

        #    attribute connector button
        self.h_batch_connector_btn = QtWidgets.QPushButton(self.connections_tab)
        self.h_batch_connector_btn.setText("Connect Attributes")

        # Controls tab
        self.controls_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.controls_tab, "Controls")
        self.h_swap_control_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_swap_control_btn.setText("Swap Shape")
        # self.h_swap_control_btn.resize(370, 20)

        self.shape_options = QtWidgets.QComboBox(self.controls_tab)
        self.shape_options.move(10, 81)
        self.shape_options.resize(200, 30)
        self.shape_options.setStyleSheet("border: 3px solid blue; border-right-width: 0px;")
        all_options = dict_lib.controls()
        for key in all_options:
            self.shape_options.addItem(key)

        self.h_control_selection_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_control_selection_btn.setText("Set Control Shape")
        self.control_selection = self.shape_options.currentText()
        self.h_control_selection_btn.move(200, 81)
        self.h_control_selection_btn.resize(150, 30)
        self.h_control_selection_btn.setStyleSheet("border: 3px solid blue;border-left-width: 0px;")

        #     add colour options
        self.h_color_options_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_color_options_btn.setText("Colour Options")

        # FKIK Ttab
        self.fkik_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.fkik_tab, "FK/IK")

        self.tools_tab.setCurrentIndex(0)

        # Transforms tab
        self.transforms_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.transforms_tab, "Transforms")
        self.h_aim_at_btn = QtWidgets.QPushButton(self.transforms_tab)
        self.h_aim_at_btn.setText("Aim At")
        self.h_aim_at_btn.move(0, 36)
        self.h_aim_at_btn.resize(40, 20)

        #     adding pole vector label
        self.h_input_pv_label = QtWidgets.QLabel(self.transforms_tab)
        self.h_input_pv_label.setText("Up Vector:")
        self.h_input_pv_label.move(45, 36)
        self.h_input_pv_label.resize(80, 20)

        #     adding float input dialog
        self.h_input_pv_x = QtWidgets.QLineEdit(self.transforms_tab)
        self.h_input_pv_x.move(100, 36)
        self.h_input_pv_x.resize(30, 20)
        self.h_input_pv_x.setText("0.0")
        self.h_input_pv_y = QtWidgets.QLineEdit(self.transforms_tab)
        self.input_y = self.h_input_pv_y.text()
        self.h_input_pv_y.move(130, 36)
        self.h_input_pv_y.resize(30, 20)
        self.h_input_pv_y.setText("1.0")
        self.h_input_pv_z = QtWidgets.QLineEdit(self.transforms_tab)
        self.input_z = self.h_input_pv_z.text()
        self.h_input_pv_z.move(160, 36)
        self.h_input_pv_z.resize(30, 20)
        self.h_input_pv_z.setText("0.0")

        #     adding vector combobox label
        self.h_vector_label = QtWidgets.QLabel(self.transforms_tab)
        self.h_vector_label.setText("Aimed Axis:")
        self.h_vector_label.move(190, 36)
        self.h_vector_label.resize(80, 20)

        #     adding vector combobox
        self.vector_enum = QtWidgets.QComboBox(self.transforms_tab)
        self.vector_enum.move(250, 36)
        self.vector_enum.resize(33, 20)
        self.vector_enum.addItem('x')
        self.vector_enum.addItem('y')
        self.vector_enum.addItem('z')

        #     adding up vector label
        self.h_up_vector_label = QtWidgets.QLabel(self.transforms_tab)
        self.h_up_vector_label.setText("Up Axis:")
        self.h_up_vector_label.move(285, 36)
        self.h_up_vector_label.resize(80, 20)

        #     adding up vector combobox
        self.up_vector_enum = QtWidgets.QComboBox(self.transforms_tab)
        self.up_vector_enum.move(325, 36)
        self.up_vector_enum.resize(33, 20)
        self.up_vector_enum.addItem('x')
        self.up_vector_enum.addItem('y')
        self.up_vector_enum.addItem('z')
        self.up_vector_enum.setCurrentIndex(1)

        return


    def create_layouts(self):
        # Create the skeleton tab layout:
        skeleton_tab_layout = QtWidgets.QFormLayout(self.skeleton_tab)
        skeleton_tab_layout.addRow(self.jfc_btn)
        skeleton_tab_layout.addRow(self.dumb_copy_orient_btn)
        skeleton_tab_layout.addRow(self.smart_copy_orient_btn)

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
        connections_tab_layout.addRow(self.h_input_driver_txtbox)
        connections_tab_layout.addRow(self.h_input_driven_txtbox)
        connections_tab_layout.addRow(self.h_batch_connector_btn)

        # Create Controls Tab layout:
        controls_tab_layout = QtWidgets.QFormLayout(self.controls_tab)
        controls_tab_layout.addRow(self.h_color_options_btn)
        controls_tab_layout.addRow(self.h_swap_control_btn)

        # Create Transforms Tab layout:
        transforms_tab_layout = QtWidgets.QFormLayout(self.transforms_tab)

        return


    def create_connections(self):
        self.jfc_btn.clicked.connect(self.ui_joint_from_component)
        self.harden_btn.clicked.connect(self.ui_harden_skin)
        self.copy_sw_btn.clicked.connect(self.ui_copy_skinweights)
        self.find_rs_btn.clicked.connect(self.ui_find_related_cluster)
        self.select_bj_btn.clicked.connect(self.ui_find_related_joints)
        self.h_create_offset_btn.clicked.connect(self.ui_create_offset)
        self.h_connect_xforms_btn.clicked.connect(self.ui_connect_xform)
        self.get_driver.text()
        self.get_driven.text()
        self.h_batch_connector_btn.clicked.connect(self.ui_batch_connect)
        self.h_swap_control_btn.clicked.connect(self.ui_swap_controls)
        self.shape_options.currentText()
        self.h_control_selection_btn.clicked.connect(self.ui_control_options)
        self.h_color_options_btn.clicked.connect(self.ui_colour_options)
        self.h_aim_at_btn.clicked.connect(self.ui_aim_at)
        self.dumb_copy_orient_btn.clicked.connect(self.ui_dumb_copy_orient)
        self.smart_copy_orient_btn.clicked.connect(self.ui_smart_copy_orient)

        return


    # UI commands:

    def ui_joint_from_component(self):
        print ("UI call for skeleton.joint_from_components()")
        skeleton.joint_from_components()

        return


    def ui_harden_skin(self):
        print ("UI call for skinning.harden()")
        skinning.harden()

        return


    def ui_copy_skinweights(self):
        print ("UI call for skinning.copy_skinweights()")
        skinning.copy_skinweights()

        return


    def ui_find_related_cluster(self):
        print ("UI call for skinning.find_related_skinCluster()")
        skinning.find_related_skinCluster()

        return


    def ui_find_related_joints(self):
        print ("UI call for skinning.select_bound_joints()")
        skinning.select_bound_joints()

        return


    def ui_create_offset(self):
        print ("UI call for handles.create_offset()")
        handles.create_offset()

        return


    def ui_connect_xform(self):
        print ("UI call for connections.connect_xforms()")
        connections.connect_xforms()

        return


    def ui_batch_connect(self):
        print ("UI call for connections.batch_connect()")
        # uses input attributes for parameters
        connections.batch_connect(str(self.get_driver.text()), str(self.get_driven.text()))

        return


    def ui_swap_controls(self):
        print ("UI call for swapping control shape")
        all_control_options.swap_shape()

        return


    def ui_control_options(self):
        print ("UI call for picking control")
        all_control_options.pick_control(self.shape_options.currentText())

        return


    def ui_colour_options(self):
        print ("UI call for picking colour")
        all_control_options.pick_colour()

        return


    def ui_aim_at(self):
        print ("UI call for aim at button")

        # takes selection as node and target
        nodes = pm.ls(selection=True)

        if(len(nodes) != 2):
            pm.warning("Please select one target and one subject (transform nodes)")
            return
            
        node = nodes[1]
        target = nodes[0]

        # takes values entered
        pv_x = float(self.h_input_pv_x.text())
        pv_y = float(self.h_input_pv_y.text())
        pv_z = float(self.h_input_pv_z.text())

        if(self.vector_enum.currentText() == self.up_vector_enum.currentText()):
            pm.warning("Aimed vector and up vector can't be the same thing!")
            return

        orientation.aim_at(node, target, up_vector=(pv_x, pv_y, pv_z),
                           aim_axis=self.vector_enum.currentIndex(), 
                           up_axis=self.up_vector_enum.currentIndex())

        return


    def ui_dumb_copy_orient(self):
        orientation.dumb_copy_orient()

        return


    def ui_smart_copy_orient(self):
        orientation.smart_copy_orient()
 
        return


def run():
    """displays windows"""

    srsu_main_dialog = MainDialog()

    #shows window
    srsu_main_dialog.show(dockable=True, floating=True)

    return

  