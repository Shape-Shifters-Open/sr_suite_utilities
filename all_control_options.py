import pymel.core as pm
import maya.OpenMayaUI as omui
import pymel.core as pm
# Trust all the following to ship with Maya.
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from . import dict_lib

"""All the options to modify control shape and colour
Will add a size option"""

def swap_shape():
    """takes first selected shape and swaps the other shapes to match it"""

    #takes selection of controls for swap
    all_controls = pm.ls(selection = True)

    #establishes original control shape
    orig_ctrl = all_controls[0]
    all_controls.remove(orig_ctrl)

    new_control = pm.duplicate(orig_ctrl, rr = True)[0]
    new_shape = new_control.getShape()
    print("The shape node is {} and it's type {}".format(new_shape.name(), type(new_shape)))

    #swaps individual shapes
    for ctrl in all_controls:

        current_shape = ctrl.getShape()
        pm.parent(new_shape, ctrl, s=True, r=True)

        pm.delete(current_shape)
    pm.delete(new_control)



def pick_control(control_selected):
    """changes control shape to chosen shape"""

    #takes selection of controls to be changed
    cur_curve = pm.ls(selection=True)

    #checks if selection is appropriate
    for ctrl in cur_curve:
        if pm.nodeType(ctrl) != "transform":
            pm.error("please select a transform node")
            break


    #create swappable curve - this is a test - works with ring and plus

    new_curve = pm.curve(per=dict_lib.controls_dict[control_selected]['per'],
                         p=dict_lib.controls_dict[control_selected]['points'],
                         k=dict_lib.controls_dict[control_selected]['knots'],
                         d=dict_lib.controls_dict[control_selected]['degree'])
    new_curve_node = pm.PyNode(new_curve)
    #creates selection to send to swap curve function
    pm.select(new_curve, replace = True)
    pm.select(cur_curve, add = True)
    swap_shape()
    pm.delete(new_curve_node)



def set_colour():
    """provides selection window for colour"""

    #creates qolor window
    qcolor = QtWidgets.QColorDialog().getColor()

    #checks colour an sets up rgb for maya
    if qcolor.isValid():
        new = qcolor.getRgb()
        colors = [new[0] * 0.001, new[1] * 0.001, new[2] * 0.001]


    return colors

def pick_colour():
    """ sets the control colour based on selection"""

    #takes in control selection for colour change
    ctrl = pm.ls(selection=True)
    colors_list = set_colour()

    #assigns rgb values
    r_value = colors_list[0]
    g_value = colors_list[1]
    b_value = colors_list[2]

    #updates each control
    for each_ctrl in ctrl:
        pm.setAttr(each_ctrl + ".overrideEnabled", 1)
        pm.setAttr(each_ctrl + ".overrideRGBColors", 1)
        pm.setAttr(each_ctrl + ".overrideColorRGB", r_value, g_value, b_value)

def get_controls(axis):
    """gets controls either from selection or from the scene
    """
    #grabs selection if exists
    controls = pm.ls(selection = True)

    #if selection exists, calls function to mirror on it
    if len(controls)>0:
        mirror_controls(controls, axis)

    #if not, finds all controls in scene and mirrors those that aren't used               
    else:

        #iterates thrpugh all controls in scene and creates list of only transforms
        controls = [pm.listRelatives(i, parent=1, type='transform')[0] for i
        in pm.ls(type='nurbsCurve', objectsOnly=1, recursive=1, noIntermediate=1)]

        for current_control in controls:
            #removes from list if control has connections
            if pm.listConnections(current_control, c=True):
                controls.remove(current_control)
                
            else:
                pass
        #mirrors controls that are nto connected
        mirror_controls(controls, axis)
    
    return


def mirror_controls(controls, axis):
    """takes an arguement of controls and axis and mirrors
        params:
                controls: takes either the scene selection 
                          or all controls that are not connected
                axis: mirrors on given axis
    """
    #temp side axis dictionary
    axis_main = {0: "X",
                1: "Z",
                2:"Y"}
    axis_plane = {0: "Z",
                1: "Y",
                2:"X"}
    for control in controls:
        #for temporary naming
        name = str(control) 
        #creates duplicate that will be mirrored
        dup = pm.duplicate(control,renameChildren=True,rr=True,name=str(control) + "_duplicate")[0]
        #checks if a heirarchy exists
        current_parent = pm.listRelatives(dup, parent = True)
        #creates world space transform for mirroring
        parent_group = pm.group(em = True, n = name + "_GRP")
        #parents to world space transform for mirroring
        pm.parent(dup, parent_group)
        #rotates and scales 
        current_rot = pm.getAttr(parent_group + ".rotate" + axis_main[axis])
        pm.setAttr(parent_group + ".rotate" + axis_main[axis], current_rot + 180)
        pm.setAttr(parent_group + ".scale" + axis_plane[axis], -1)

        #checks if control is parented to world
        shape = pm.listRelatives(dup, shapes=True)
        node = pm.nodeType(shape)
        if node == "nurbsCurve":
            pm.parent(dup, w = True)

        #parents control to world   
        else:
            kids = pm.listRelatives(dup, allDescendents = True)
            print ("dup is ", dup)
            print ("kids are ", kids)
            for kid in kids:
                shape = pm.listRelatives(kid, shapes=True)
                node = pm.nodeType(shape)
                if node == "nurbsCurve":
                    ctrl = kid
                    pm.parent(ctrl, w = True)
            pm.delete(dup)
                   
        #deletes temporary wolrd space transform
        pm.delete(parent_group)
    
    return



