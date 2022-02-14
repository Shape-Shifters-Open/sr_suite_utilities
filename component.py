# component.py
# Created: Monday, 14th February 2022 8:35:18 am
# Matthew Riche
# Last Modified: Monday, 14th February 2022 8:35:27 am
# Modified By: Matthew Riche

import pymel.core as pm
import pymel.core.datatypes as dt

from . import progbar as prg

def list_vertex_deltas(new_geo, original_geo):
    '''
    Will take two pieces of geo and compare their positional offsets.
    The vertex order of the geo should match, or else it'll fail to zip the two lists of zips.
    '''

    ws_positions = []

    # Maya will return pm.general.MeshVertex unless casted as a list.
    print(list(new_geo.vtx))
    vert_zip = zip(list(new_geo.vtx), list(original_geo.vtx))

    prg.start_progbar(max_value = len(list(new_geo.vtx)), message="Calculating Vertex Deltas...")
    print("Calculating {} vert deltas...".format(len(list(new_geo.vtx))))
    for verts in vert_zip:
        new_vert_pos = dt.Vector(pm.xform(verts[0], q=True, t=True, ws=True))
        orig_vert_pos = dt.Vector(pm.xform(verts[1], q=True, t=True, ws=True))
        ws_positions.append(new_vert_pos - orig_vert_pos)
        prg.update_progbar()

    prg.end_progbar()

    return ws_positions