# coord_math.py
# Matt Riche 2021
# some 3D math custom formulas to help sr_suite_utilities


import pymel.core as pm
import numpy as np


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
        node_xform = pm.xform(node, q=True, t=True, a=True)
        print (node_xform)
        x_vals.append(node_xform[0])
        y_vals.append(node_xform[1])
        z_vals.append(node_xform[2])

    average_pos = [np.average(x_vals), np.average(y_vals), np.average(z_vals)]

    print

    return average_pos


def get_normal(point_a, point_b, point_c):
    '''
    Returns the vector of the normal for triangle specified by the given three points.

    usage:
    get_normal(point_a, point_b, point_c)
    point_a/b/c = a tuple with eulerian coordinates in it.
    '''

    # Turn coord lists into vectors so the math is easy:
    vec_a = np.array(point_a)
    vec_b = np.array(point_b)
    vec_c = np.array(point_c)

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
    vpoint_a = np.array(point_a)
    vpoint_b = np.array(point_b)
    vector = vpoint_a - vpoint_b

    return vector


def get_unit_vector(vector):
    '''
    given two points, normalize the line into a unit vector.
    The points are non-numpy lists.

    usage:
    get_unit_vector(point_a=[lists], point_b=[lists])
    '''
    point_a = vector[0]
    point_b = vector[1]
    # Calculate magnitude
    magnitude = np.sqrt(point_a[0]**2 + point_a[1]**2 + point_a[2]**2)

    # Normalize into unit vector.
    normalized_mag = vector / magnitude

    return normalized_mag
    

def match_xform(target_node, subject_node, rotate=True):
    '''
    match_xform
    Matches the transform of one object to another.
    Performs the same as Maya's internal match without the weird matrix bugs.

    usage:
    match_xform(target_node=[string or PyNode], subject_node=[string or PyNode], rotate=[boolean])
    '''

	# Get details from the target_node.
	targetRotOrder = pm.getAttr(target_node.rotateOrder)
	targetRot = pm.xform( target_node, q=True, ws=True, ro=True )
	targetTrans = pm.xform( target_node, q=True, ws=True, t=True )
	targetRotPivot = pm.xform( target_node, q=True, ws=True, rp=True )

	# I've been warned about the ws flags behaving deceptively.
	pm.xform( subject_node, ws=True, t=targetTrans )

	if(rotate):
		pm.xform( subject_node, ws=True, ro=targetRot )

    return
