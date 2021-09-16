# coord_math.py
# Matt Riche 2021
# some 3D math custom formulas to help sr_suite_utilities


import pymel.core as pm
import pymel.core.datatypes as dt
import maya.api.OpenMaya as om


def get_component_ID(component):
    '''
    Get selected component's ID/s using om2
    '''
    print ("Component is {}".format(component))
    id = component.getComponent(0)[1]
    id_list = om.MFnSingleIndexedComponent(id)
    id_element = id_list.getElements()

    print ("Component ID was {}".format(id_element))
    return id_element


def get_point_at_range(source_point, point):
    '''
    Not well documented what this was for...
    '''
    pass
    

def get_average_xform(nodes):
    '''
    Given a selection of components or trans nodes, find the average positon in world space.

    usage:
    get_average_xform(nodes)
    nodes - list of string node names or PyNodes.
    '''
    
    x_vals = []
    y_vals = []
    z_vals = []
    # Find the average transform of all nodes selected
    for node in nodes:

        # Transfer the PyNodes incoming to MObjects using viewport selection (Yes I hate it too):
        print ("Selecting {} and passing it to OM".format(node))
        pm.select(node)
        selection = om.MGlobal.getActiveSelectionList()
        print (selection)
        component_id = get_component_ID(selection)
        meshDagPath = selection.getDagPath(0)
        mFnMesh = om.MFnMesh(meshDagPath)
        new_point = mFnMesh.getPoint(component_id[0], om.MSpace.kWorld)

        print (new_point)
        x_vals.append(new_point[0])
        y_vals.append(new_point[1])
        z_vals.append(new_point[2])

    x_avg = sum(x_vals) / len(x_vals)
    y_avg = sum(y_vals) / len(y_vals)
    z_avg = sum(z_vals) / len(z_vals)

    return [x_avg, y_avg, z_avg]


def get_normal(point_a, point_b, point_c):
    '''
    Returns the vector of the normal for triangle specified by the given three points.

    usage:
    get_normal(point_a, point_b, point_c)
    point_a/b/c = a tuple with eulerian coordinates in it.
    '''

    # Turn coord lists into vectors so the math is easy:
    vec_a = dt.Vector(point_a)
    vec_b = dt.Vector(point_b)
    vec_c = dt.Vector(point_c)

    normal = (vec_c - vec_a) * (vec_b - vec_a)

    return normal


def get_vector(point_a, point_b):
    '''
    Given two Euler points in space, return the vector.

    usage:
    get_vector(point_a=[x,y,z], point_b=[x,y,z])
    Where x,y,z are Euler coords.
    '''

    # Grab numpy vectors for after
    vpoint_a = dt.Vector(point_a)
    vpoint_b = dt.Vector(point_b)
    vector = vpoint_a - vpoint_b

    return vector


def match_xform(target_node, subject_node, rotate=True):
    '''
    match_xform
    Matches the transform of one object to another.
    Performs the same as Maya's internal match without the weird matrix bugs.

    usage:
    match_xform(target_node=[string or PyNode], subject_node=[string or PyNode], rotate=[boolean])
    '''

    # Get details from the target_node.
    #targetRotOrder = pm.getAttr(target_node.rotateOrder)
    target_rot = pm.xform( target_node, q=True, ws=True, ro=True )
    target_trans = pm.xform( target_node, q=True, ws=True, t=True )
    #targetRotPivot = pm.xform( target_node, q=True, ws=True, rp=True )

    # I've been warned about the ws flags behaving deceptively.
    pm.xform( subject_node, ws=True, t=target_trans )

    if(rotate):
        pm.xform( subject_node, ws=True, ro=target_rot )
    
    return 


    

