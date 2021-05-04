"""
math.py
Some of the custom math utilities that the other tools lean on.
"""

import pymel.core as pm
import numpy as np


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
    # Calculate magnitude
    magnitude = np.sqrt(point_a[0]**2 + point_a[1]**2 + point_a[2]**2)

    # Normalize into unit vector.
    normalized_mag = vector / magnitude

    return normalized_mag
    

