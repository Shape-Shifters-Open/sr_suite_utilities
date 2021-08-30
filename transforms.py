# transforms.py
# Matt Riche 2021
# Module for transform related tasks in sr_suite_utilities

import pymel.core as pm
import pymel.core.datatypes as dt


def aim_at(node, target=None, vec=None, pole_vec=(0,-1,0), axis=1, pole=2):
    '''
    Aim's a node's axis at another point in space and a "pole axis" down a normalized vector.

    node - PyNode of the transform to be aimed
    target - PyNode of object to be aimed at (if vec == None)
    vec - dt.Vector of direction to aim in (if target == None)
    pole_vec - A dt.Vector that aims toward the "pole" of this aim constraint.
    axis - the axis along which to aim down. (enumated x,y,z where x=0)
    pole - the "pole" axis, which will aim at the vec (enumerated x,y,z where x=0)
    '''

    # Format this input into a dt.Vector:
    pole_vec = dt.Vector(pole_vec)

    # Sort what we are aiming at:
    # If we got a target, use it.
    if(target != None):
        target_pos = dt.Vector(pm.xform(target, q=True, ws=True, t=True))
        node_pos = dt.Vector(pm.xform(node, q=True, ws=True, t=True))
        target_vec = target_pos - node_pos
        target_vec.normalize()

        if(vec != None):
            pm.warning("Both vec and node are populated.  Node will take precidence.")

    # If we got a vec, use that instead.
    elif(vec != None):
        target_vec = vec.normal()

    else:
        pm.error("Either a vector or a target is required.")
        return

    # Step two, "unconstrained" vec; cross product of normalized vector and normalized pole vector 
    # is found and stored.
    u_vec = target_vec.cross(pole_vec)

    # Step three, we "clean" the pole vector by getting the cross product of the aim and the 
    # "unconstrained" axis vector.
    clean_pole = target_vec.cross(u_vec)

    # Step four, apply the values of each vector to the correct place in the matrix.
    aimed_matrix = dt.Matrix()






