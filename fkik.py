"""
fkik.py
sr_suite_utilities
"""

import pymel.core as pm


def fk_to_ik(ik_bones_dict = {}, fk_ctrls_dict = {}):
    """
    Match fk controls to ik, but executing match xforms of the controllers to the bones.  Generic
    and ready to receive rig info for any rig with a 'copied arm' set up for fk/ik.  Assuming that
    the rig is well build and controller xforms match these bone xforms, result will be accurate.
    
    ik_bones_dict - dictionary containing keys 'shoulder' and 'elbow', etc, listing the ik bones.
    fk_ctrls_dict - dictionary containing keys 'shoulder' and 'elbow' etc, listing fk controls.
    """

    if(ik_bones_dict == {}):
        # guess ik bones based on selection?
        pm.error("Automatic joint finding not implemented.")
        return

    if(fk_ctrls_dict == {}):
        # guess fk bones based on selection.
        pm.error("Automatic ctrl finding not implemented.")
        return

    # Iterate through the list of key names, perform the xform matching.
    targets_list = ['shoulder', 'elbow', 'wrist']
    for target_key in targets_list:
        print("Matching transforms of {} to {}...".format(
            fk_ctrls_dict[target_key], ik_bones_dict[target_key]
            ))
            # PyNode these up:
        target_node = pm.PyNode(fk_ctrls_dict[target_key])
        copy_node = pm.PyNode(ik_bones_dict[target_key])
        pm.matchTransform(target_node, copy_node, pos=True, piv=True)

    return

    



    