# handles.py
# Matt Riche 2021
# Shaper Rigs suite utilities relating to the setup of handles and controls.

import pymel.core as pm

offset_string = "_Offset"

def create_offset(suffix=offset_string):
    '''
    Creates an offset group above the selection.
    
    Return value: List of new offset nodes (PyNodes)

    Usage:
    create_offset(suffix=[string]) # With selection

    suffix - string that defaults to a constant, usually "_Offset"
    '''

    selection = pm.ls(sl=True)

    offsets_list = []

    for node in selection:
        # Create empty xform node.
        group = pm.group(empty=True, n=(node.name() + suffix))
        offsets_list.append(group)
        # Move group node to same world-space xform as the selection
        pm.matchTransform(group, node)

        # Arrange desired hierarachy (Node beneath new transform, new transform beneath old parent.)
        parent = pm.listRelatives(node, parent=True)
        pm.parent(node, group, a=True)
        if(parent != None):
            pm.parent(group, parent[0], a=True)

    return offsets_list