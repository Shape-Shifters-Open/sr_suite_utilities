# deform.py
# Created: Monday, 14th February 2022 8:32:59 am
# Matthew Riche
# Last Modified: Monday, 14th February 2022 8:33:05 am
# Modified By: Matthew Riche

'''
Operations related to deformations
'''

from . import component as cmp
from . import progbar as prg

import pymel.core as pm

def deltas_to_tweak(new_geo, old_geo, tweak):
    '''
    Applies a list of vertex deltas, generated by component.list_vertex_deltas() to the inside
    of a tweak node.
    '''

    deltas = cmp.list_vertex_deltas(new_geo, old_geo)

    prg.start_progbar(max_value=len(deltas), message="Baking Deltas to Tweak node...")

    for delta in deltas:
        tweak_vert = tweak.plist[0].controlPoints[deltas.index(delta)]
        tweak_vert.xValue.set(delta[0])
        tweak_vert.yValue.set(delta[1])
        tweak_vert.zValue.set(delta[2])
        prg.update_progbar()

    prg.end_progbar()

    print("Vertex deltas from {} are now baked to {}.".format(new_geo.name(), tweak))

    return
