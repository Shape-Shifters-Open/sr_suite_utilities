'''
colour.py

Module for doing whatever recolour related task.
Spelled the Canadian way in stark defiance.
'''

import pymel.core as pm


colour_dict = { 'grey':0, 'black':1, 'darkGrey':2, 'lightGrey':3, 'darkRed':4, 'navy':5, 'blue':6, 
                'darkGreen':7, 'darkPurple':8, 'purple':9, 'brown':10, 'darkBrown':11, 
                'darkOrange':12, 'red':13, 'brightGreen':14, 'paleBlue':15, 'white':16, 'yellow':17, 
                'cyan':18, 'selectGreen':19, 'pink':20, 'paleOrange':21, 'paleYellow':22, 
                'paleGreen':23, 'orange':24, 'darkYellow':25, 'uglyGreen':26, 'blueGreen':27, 
                'darkCyan':28, 'darkBlue':29, 'palePurple':30, 'violet':31 }


def change_colour(node, colour='red', shape=True ):
    '''
    changes the colour override on the given node.

    usage:
    change_colour(PyNode, colour=(string), shape=(bool))
    colour - Must be a string key for the colour_dict in this module.
    shape - If true, the override will go on the shape instead of the 
    '''

    node.overrideEnabled.set(True)
    node.overrideColor.set(colour_dict[colour])
    if(shape):
        node.getShape().overrideEnabled.set(True)
        node.getShape().overrideColor.set(colour_dict[colour])   
        print ("Changed the colour override of {} to {}.").format(node, colour)
