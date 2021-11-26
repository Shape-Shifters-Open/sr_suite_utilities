import pymel.core as pm
import dict_lib

"""All the options to modify control shape and colour
Will add a size option"""

def swap_shape():
    """takes first selected shape and swaps the other shapes to match it"""
    print "testing shape swap"

    #takes selection of controls for swap
    all_controls = pm.ls(selection = True)

    #establishes original control shape
    orig_ctrl = all_controls[0]
    all_controls.remove(orig_ctrl)
    orig_shape = pm.listRelatives(orig_ctrl, shapes = True)[0]

    #swaps individual shapes
    for ctrl in all_controls:
        current_shape = pm.listRelatives(ctrl, shapes = True)[0]
        pm.connectAttr(str(orig_shape) + '.local', str(current_shape) + '.create', force = True)
        #pm.disconnectAttr(str(orig_shape) + '.local', str(current_shape) + '.create')



def pick_control(control_selected):
    """changes control shape to chosen shape"""
    print "testing control picker"

    #takes selection of controls to be changed
    cur_curve = pm.ls(selection=True)

    #create swappable curve - this is a test - works with ring and plus
    new_curve = pm.curve(per=dict_lib.controls_dict[control_selected]['per'],
                         p=dict_lib.controls_dict[control_selected]['points'],
                         k=dict_lib.controls_dict[control_selected]['knots'],
                         d=dict_lib.controls_dict[control_selected]['degree'])

    #creates selection to send to swap curve function
    pm.select(new_curve, replace = True)
    pm.select(cur_curve, add = True)
    swap_shape()
    #pm.delete(new_curve)


def pick_colour():
    """changes colour of chosen controls to selected colour"""

    #takes selection of controls for colour change
    ctrls = pm.ls(selection=True)
    print "testing colour"

    #gets selected colour and converts to rgb
    colour = QtWidgets.QColorDialog.getColor()
    rgb_value = colour.getRgb()

    #enables overrides, switches colour to rgb and changes colour
    for channel, color in zip(rgb, rgb_value):
        for each_ctrl in ctrls:
            cmds.setAttr(each_ctrl + ".overrideEnabled", 1)
            cmds.setAttr(each_ctrl + ".overrideRGBColors", 1)
            cmds.setAttr(each_ctrl + ".overrideColor%s" % channel, color)



