'''
debugging.py

Debugging tools for other parts of the suite.
'''

import pymel.core as pm
import pymel.core.datatypes as dt
import colour as cl

def make_vector_nurbs(vector, start_point=None):
    '''
    Create a one-degree nurbs curve that shows the vector given.
    '''

    if(start_point != None):
        vector_line = pm.curve(d=1, p=[start_point, vector])
    else:
        vector_line = pm.curve(d=1, p=[(0,0,0), vector])

    return vector_line


def make_matrix_nurbs(matrix, name="debug_matrix"):
    '''
    Show what a matrix 'should look like' with one-degree debug curves.
    '''

    trans = dt.Vector(matrix[3][:3])

    x_vec = dt.Vector(matrix[0][:3])
    y_vec = dt.Vector(matrix[1][:3])
    z_vec = dt.Vector(matrix[2][:3])

    print(trans)

    x_nurbs = make_vector_nurbs(x_vec + trans, start_point=trans)
    y_nurbs = make_vector_nurbs(y_vec + trans, start_point=trans)
    z_nurbs = make_vector_nurbs(z_vec + trans, start_point=trans)

    cl.change_colour(x_nurbs, colour='pink')
    cl.change_colour(y_nurbs, colour='paleGreen')
    cl.change_colour(z_nurbs, colour='paleBlue')

    pm.group(x_nurbs, y_nurbs, z_nurbs, n=name)

    return



