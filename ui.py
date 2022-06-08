# ui.py
# Matt Riche 2021
# Shaper Rigs in-suite UI.

from pickletools import long4
from pymel.core.datatypes import Vector
import maya.OpenMayaUI as omui
import pymel.core as pm
import sys
# Trust all the following to ship with Maya.
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import gc
import sys

# From related modules:

from . import globals
from . import skeleton
from . import skinning
from . import handles
from . import connections
from . import dict_lib
from . import all_control_options
from . import orientation
from . import deform
from . import vehicle
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):

    def __init__(self, parent=maya_main_window()):
        super(MainDialog, self).__init__(parent)
        self.setWindowTitle("Shaper Rigs Suite Utilities v{}".format(globals.srsu_version))
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

        # Remove help button flag on windows wm.
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        return


    def create_widgets(self):
        # Prep tabs:
        self.tools_tab = QtWidgets.QTabWidget(self)
        self.tools_tab.setGeometry(QtCore.QRect(20, 20, 371, 600))
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

        # Rip Skin Tab Groupbox
        self.rip_box = QtWidgets.QGroupBox("Rip Skin Tool", self.skin_tab)
        self.rip_box.move(10, 175)
        self.rip_box.resize(360, 240)
        

        self.h_source_txtbox = QtWidgets.QLabel(self.skin_tab)
        self.h_source_txtbox.setText("Input Source Mesh")
        self.get_source_mesh = QtWidgets.QLineEdit(self.skin_tab)
        self.h_target_txtbox = QtWidgets.QLabel(self.skin_tab)
        self.h_target_txtbox.setText("Input Target Mesh")
        self.get_target_mesh = QtWidgets.QLineEdit(self.skin_tab)


        self.match_by_options_label = QtWidgets.QLabel(self.skin_tab)
        self.match_by_options_label.setText("Match by")
        self.match_by_options = QtWidgets.QComboBox(self.skin_tab)

        all_options = ["Closest Point", "UVs"]
        for option in all_options:
            self.match_by_options.addItem(option)
        
        self.influence_options_label = QtWidgets.QLabel(self.skin_tab)
        self.influence_options_label.setText("Influence Option")
        self.influence_options = QtWidgets.QComboBox(self.skin_tab)

        all_options = ["Closest Joint", "Namespace"]
        for option in all_options:
            self.influence_options.addItem(option)


        self.rip_skin_btn = QtWidgets.QPushButton(self.skin_tab)
        self.rip_skin_btn.setText("Rip Skin")


        self.vbox = QtWidgets.QVBoxLayout()
        self.rip_box.setLayout(self.vbox)
        self.vbox.addWidget(self.h_source_txtbox)
        self.vbox.addWidget(self.get_source_mesh)
        self.rip_box.layout().addLayout(self.vbox)
        self.vbox.addWidget(self.h_target_txtbox)
        self.vbox.addWidget(self.get_target_mesh)
        self.rip_box.layout().addLayout(self.vbox)     
        self.vbox.addWidget(self.match_by_options_label)
        self.vbox.addWidget(self.match_by_options)
        self.rip_box.layout().addLayout(self.vbox)
        self.vbox.addWidget(self.influence_options_label)
        self.vbox.addWidget(self.influence_options)
        self.rip_box.layout().addLayout(self.vbox)
        self.vbox.addWidget(self.rip_skin_btn)


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

        # add colour options
        self.h_color_options_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_color_options_btn.setText("Colour Options")

        #self.tools_tab.setCurrentIndex(0)

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

        # Deform Tab tab
        self.deform_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.deform_tab, "Deform")

        self.new_geo_txtbox = QtWidgets.QLabel(self.deform_tab)
        self.new_geo_txtbox.setText("Input New Geo")
        self.new_geo_txtbox.move(10, 21)
        self.get_new_geo = QtWidgets.QLineEdit(self.deform_tab)
        self.get_new_geo.move(150, 21)
        self.get_new_geo.resize(210, 20)

        self.new_geo_txtbox = QtWidgets.QLabel(self.deform_tab)
        self.new_geo_txtbox.setText("Input Old Geo")
        self.new_geo_txtbox.move(10, 42)
        self.get_old_geo = QtWidgets.QLineEdit(self.deform_tab)
        self.get_old_geo.move(150, 42)
        self.get_old_geo.resize(210, 20)

        self.tweak_node = QtWidgets.QLabel(self.deform_tab)
        self.tweak_node.setText("Input Tweak Node")
        self.tweak_node.move(10, 63)
        self.get_tweak_node = QtWidgets.QLineEdit(self.deform_tab)
        self.get_tweak_node.move(150, 63)
        self.get_tweak_node.resize(210, 20)

        self.h_deform_btn = QtWidgets.QPushButton(self.deform_tab)
        self.h_deform_btn.setText("Bake Deltas")
        self.h_deform_btn.move(10, 84)
        self.h_deform_btn.resize(360, 20)

        # Vehicle tab
        self.vehicle_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.vehicle_tab, "Vehicles")

        #     adding wheel rotate axis label
        self.h_wheel_rot_label = QtWidgets.QLabel(self.vehicle_tab)
        self.h_wheel_rot_label.setText("Wheel Rotate")
        self.h_wheel_rot_label.move(10, 36)
        self.h_wheel_rot_label.resize(80, 20)

        #     adding wheel rotate axis combobox
        self.h_wheel_rot = QtWidgets.QComboBox(self.vehicle_tab)
        self.h_wheel_rot.move(81, 36)
        self.h_wheel_rot.resize(33, 20)
        self.h_wheel_rot.addItem('X')
        self.h_wheel_rot.addItem('Y')
        self.h_wheel_rot.addItem('Z')

        #     adding wheel up axis label
        self.h_wheel_up_label = QtWidgets.QLabel(self.vehicle_tab)
        self.h_wheel_up_label.setText("Wheel UP")
        self.h_wheel_up_label.move(120, 36)
        self.h_wheel_up_label.resize(80, 20)

        #     adding wheel up axis combobox
        self.h_wheel_up = QtWidgets.QComboBox(self.vehicle_tab)
        self.h_wheel_up.move(180, 36)
        self.h_wheel_up.resize(33, 20)
        self.h_wheel_up.addItem('X')
        self.h_wheel_up.addItem('Y')
        self.h_wheel_up.addItem('Z')
        self.h_wheel_up.setCurrentIndex(1)

        self.h_build_wheel_btn = QtWidgets.QPushButton(self.vehicle_tab)
        self.h_build_wheel_btn.setText("Build Auto Wheel")
        self.h_build_wheel_btn.move(10, 60)
        self.h_build_wheel_btn.resize(360, 20)


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
        self.rip_skin_btn.clicked.connect(self.ui_rip_skin_btn)
        self.h_build_wheel_btn.clicked.connect(self.ui_build_wheel)
        


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

    def ui_bake_deltas(self):
        if not self.get_new_geo.text():
            geo = pm.ls(selection = True)
            new_geo = geo[0]
            old_geo = geo[1]
        else:
            new_geo = self.get_new_geo.text()
            old_geo = self.get_old_geo.text()
            
        deform.deltas_to_tweak(new_geo, old_geo, self.get_tweak_node.text())

    def ui_rip_skin_attrs(self):
        if not self.get_source_mesh.text():
            source_mesh = pm.ls(selection = True)[0]
        else:
            source_mesh = self.get_source_mesh.text()
        
        if not self.get_target_mesh.text():
            target_mesh = pm.ls(selection = True)[1]
        else:
            target_mesh = self.get_target_mesh.text()
        
        return(source_mesh, target_mesh)


    def ui_rip_skin_btn(self):
        skinning.rip_skin(self.ui_rip_skin_attrs()[0], self.ui_rip_skin_attrs()[1], 
                        self.match_by_options.currentIndex(), self.influence_options.currentIndex())


    def ui_build_wheel(self):
        all_wheels = pm.ls(selection = True)
        for wheel in all_wheels:
            vehicle.wheel_builder(wheel_ctrl = wheel, wheel_up = self.h_wheel_up.currentText(), 
                                  wheel_rot = self.h_wheel_rot.currentText())
        

def run():
    """displays windows"""

    for obj in gc.get_objects():
        #checks all objects in scene and verifies whether an instance of the window exists

        if isinstance(obj, MainDialog):
            print ("checking for instances")
            obj.close()


    srsu_main_dialog = MainDialog()

    #shows window
    srsu_main_dialog.show(dockable=True, floating=True)

    return