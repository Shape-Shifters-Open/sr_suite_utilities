# skeleton.py
# Matt Riche 2021
# sr_suite_utilities module for editing and creating joints

import pymel.core as pm
import coord_math as cmath

def joint_from_components(name="_JNT"):
    '''
    joint_from_components()
    Given a selection of one or more components, create a joint in the average location.
    
    usage:
    joint_from_components([name=string])
    name - (optional) string name of the joint to be created.  Defaults to "_JNT" to remind you 
    to name it.
    '''

    # Use coord_math module to get average position.
    selection = pm.ls(sl=True, fl=True)
    print ("selection is {}".format(selection))
    position = cmath.get_average_xform(selection)
    pm.select(clear=True)
    
    joint = pm.joint(p=(position[0], position[1], position[2]), n=name)

    return joint


def duplicate_skeleton(prefix="ripped_", joints_list=[]):
    '''
    duplicate_skeleton(prefix)
    Rebuilds a skeleton exactly like the hiearchy attached to base_joint.  This helps the "Rip Skin"
    feature work.

    usage:
    duplicate_skeleton(prefix=[string], base_joint=[PyNode Joint])

    return value:
    List of newly duplicated root joints.
    '''

    # First we have to take the full joints list, and chase it to the top-most joint.
    root_joints = []
    for joint in joints_list:
        # Check each joint for a lack of parents that are also joints, then collect them in roots.
        parents = pm.listRelatives(joint, ap=True)
        has_joint_parent = False
        for parent in parents:
            if(parent.type() == 'joint'):
                has_joint_parent = True
        
        if(has_joint_parent == False):
            print ("Appending {} to the list of root joints to duplicate.".format(joint))
            root_joints.append(joint)

    # Duplicate the discovered roots, and make them a child of world.
    new_roots = []
    for joint in root_joints:
        # Keep the name of the old joint
        name = (prefix + joint.name())
        print ("New name should be {}".format(name))
        new_root = pm.duplicate(joint, un=True)[0]
        pm.parent(new_root, w=True)
        new_root.rename(name)
        print ("New name is {}".format(new_root.name()))
        new_roots.append(new_root)

    return new_roots

