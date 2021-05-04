"""
fkik.py
sr_suite_utilities
"""

import coord_math as m


import pymel.core as pm

# SSC default bone names
internal_def_fk_jnts = { 'shoulder':'armUprFK_drv', 'elbow':'armLwrFK_drv', 'wrist':'armWristFK_drv' }
internal_def_ik_jnts = { 'shoulder':'armUprIK_drv', 'elbow':'armLwrIK_drv', 'wrist':'armWristIK_drv' }

# SSC default controls names
internal_default_fk_ctrls = { 'shoulder':'armUprFK_Ctrl', 'elbow':'armLwrFK_Ctrl', 'wrist':'armWristFK_Ctrl' }
internal_default_ik_ctrls = { 'shoulder':'armUprIK_Ctrl', 'elbow':'ArmPV_Ctrl', 'wrist':'armWristIK_Ctrl' }
internal_side_tokens = { 'left':'L_', 'right':'R_' }


def fk_to_ik(side=None, ik_bones_dict = internal_def_ik_jnts, fk_ctrls_dict = internal_def_fk_jnts):
    """
    Match fk controls to ik, but executing match xforms of the controllers to the bones.  Generic
    and ready to receive rig info for any rig with a 'copied arm' set up for fk/ik.  Assuming that
    the rig is well build and controller xforms match these bone xforms, result will be accurate.
    
    ik_bones_dict - dictionary containing keys 'shoulder' and 'elbow', etc, listing the ik bones.
    fk_ctrls_dict - dictionary containing keys 'shoulder' and 'elbow' etc, listing fk controls.
    """

    if(side == None):      
        pm.error("Specify a side flag (Example fk_to_ik(side='l') )")
        return

    if(side.upper() in ['L', 'LEFT', 'L_', 'LFT', 'LT']):
        side_token = internal_side_tokens['left']
    elif(side.upper() in ['R', 'RIGHT', 'R_', 'RGT', 'RT']):
        side_token = internal_side_tokens['right']
    else:
        pm.error("Given side-flag string was weird.  Try 'r' or 'l'.")
        return

    # Append the side token to all strings.
    for bone in ik_bones_dict:
        ik_bones_dict[bone] = (side_token + ik_bones_dict[bone])
    print ("Side tokens added, joint references are:\n {}".format(ik_bones_dict))

    for ctrl in fk_ctrls_dict:
        fk_ctrls_dict[ctrl] = (side_token + fk_ctrls_dict[ctrl])
    print ("Side tokens added, ctrl targets are:\n {}".format(ik_bones_dict))

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

    print ("Done.")

    return

    
def ik_to_fk(side=None, fk_bones_dict = internal_def_fk_jnts, 
            ik_ctrls_dict=internal_default_ik_ctrls):
    """
    Move IK controls to match FK position.
    Ready to receive rig info for any rig with a 'copied arm' set up for fk/ik.  Assuming that the 
    rig is well build and controller xforms match these bone xforms, result will be accurate.
    
    usage:
    ik_to_fk(side=string, fk_bones_dict=dict, ik_controls_dict=dict)

    side - A string token to be appended to the front of the bone name.
    fk_bones_dict - dictionary containing keys 'shoulder' and 'elbow', etc, listing the fk bones.
    ik_ctrls_dict - dictionary containing keys 'shoulder' and 'elbow' etc, listing ik controls.
    """

    # Append the side flags
    if(side == None):      
        pm.error("Specify a side flag (Example fk_to_ik(side='l') )")
        return

    if(side.upper() in ['L', 'LEFT', 'L_', 'LFT', 'LT']):
        side_token = internal_side_tokens['left']
    elif(side.upper() in ['R', 'RIGHT', 'R_', 'RGT', 'RT']):
        side_token = internal_side_tokens['right']
    else:
        pm.error("Given side-flag string was weird.  Try 'r' or 'l'.")
        return

    # Append the side token to all strings.
    for bone in fk_bones_dict:
        fk_bones_dict[bone] = (side_token + fk_bones_dict[bone])
    print ("Side tokens added, joint references are:\n {}".format(fk_bones_dict))
    for ctrl in ik_ctrls_dict:
        ik_ctrls_dict[ctrl] = (side_token + ik_ctrls_dict[ctrl])
    print ("Side tokens added, ctrl targets are:\n {}".format(ik_ctrls_dict))

    # Step one, match ik shoulder 1:1
    shoulder_target = pm.PyNode(fk_bones_dict['shoulder'])
    shoulder_ctrl = pm.PyNode(ik_ctrls_dict['shoulder'])
    pm.matchTransform(shoulder_ctrl, shoulder_target, pos=True, piv=True)

    # Step two, match ik wrist 1:1
    wrist_target = pm.Pynode(fk_bones_dict['wrist'])
    wrist_ctrl = pm.PyNode(ik_ctrls_dict['wrist'])
    pm.matchTransform(wrist_ctrl, wrist_target, pos=True, piv=True)

    # Step three-- triangulate the plane on which the pole vector should go.
    normal = m.


    

