# skeleton.py
# Matt Riche 2021
# sr_suite_utilities module for editing and creating joints


import coord_math as cmath
from constants import GENERIC_KEYS
import orientation as ori
import pymel.core as pm
import pymel.core.datatypes as dt
import fbx_utils as fbx

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


def duplicate_skeleton(prefix="duplicated_", joints_list=[]):
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


def import_and_match():
    '''
    Runs the import and performs the matching process
    '''

    # Get path of imported skeleton and create datablock.
    fbx_path = pm.filepath = pm.fileDialog2(ff="*.fbx", fm=1, dialogStyle=2, cap="Import FBX")[0]
    data_block = fbx.import_skeleton(fbx_path)

    # Take the data block and use it to rebuild a skeleton
    construct_from_datablock(data_block)
    # Match in scene
    pm.error("We haven't implementing the matching scheme builder yet.")
    #translate_from_scene(data_block, cns.CLIENT_MAPPING, cns.SR_MAPPING)

    # Aim each joint per best-vectors:
    orient_from_datablock(data_block)

    # Restore hierarchy
    hierarchy_from_datablock(data_block)

    print("Skeleton matched.")



def construct_from_datablock(datablock):
    '''
    A subprocess of skeleton-matching.
    Constructs all the nodes in scene by reading the datablock given from fbx_utils.import_skeleton
    '''

    print('Building imported skeleton in scene...')

    # Iterate through data block and create in-scene-nodes based on the content.
    for joint_dict in datablock[0]:

        ws_euler = dt.Vector(joint_dict['world_space_pos'])
        j_orient = dt.Vector(joint_dict['jointOrient'])
        pm.select(cl=True)
        rebuilt_joint = pm.joint(p=ws_euler, n=(joint_dict['name']))
        rebuilt_joint.rotateOrder.set(joint_dict['rotate_order'])
        rebuilt_joint.jointOrient.set(j_orient)


def translate_from_scene(data_block, import_map, export_map):
    '''
    A subprocess of skeleton-matching.
    orient all the contents created by the datablock to the "matches" found in scene.
    This is to be run after 'construct_from_datablock as put the rebuilt joints in the scene.
    '''

    print('Matching imported skeleton...')
    for bone in GENERIC_KEYS:
        print("matching {}".format(bone))

        # Skip anything unlisted on either side.
        if(export_map[bone] == '' or import_map[bone] == ''):
            continue

        orient_to = pm.PyNode(export_map[bone])
        oriented = pm.PyNode(import_map[bone])

        # Add a new key to the datablock for access later now that this relationship is established
        for joint_dict in data_block[0]:
            if(joint_dict['name'] == import_map[bone]):
                joint_dict['match'] = export_map[bone]
                print("Added {} to data block for  {}".format(export_map[bone], joint_dict['name']))
                
        pm.matchTransform(oriented, orient_to, pos=True, rot=False)

    print ("Transform matching complete...")


def orient_from_datablock(datablock):
    '''
    A subprocess of skeleton-matching.
    orient joints based on an imported datablock
    For "Skeleton Match" purposes
    '''

    for joint_dict in datablock[0]:
         # Clean up namespaces in the datablock
        if(':' in joint_dict['name']):
            name = joint_dict['name'].split(':')[-1]
        else:
            name = joint_dict['name']

        if(joint_dict['children'] == None):
            print("{} has no children and thus we can't derive an orient.".format(name))
            continue
        child = joint_dict['children'][0]
        if(len(joint_dict['children']) > 1):
            print("{} has too many children to derive an orient.".format(name))
            continue
        elif(len(joint_dict['children']) < 1):
            print("{} has no children and thus we can't derive an orient.".format(name))
            continue

        orient = pm.PyNode(joint_dict['match'])
        orient_to = pm.PyNode(joint_dict['name'])

        ori.trans_align(orient, orient_to, source_child=child)
        print(
            "Took axis from {} and orientation from {} and aimed at {}".format(
                orient_to, orient, child
                )
            )


def hierarchy_from_datablock(datablock):
    '''
    Reconstruct hierarchy from what is defined in the datablock, maintaining new worldspace
    orientation.
    '''

    pm.select(clear=True)

    for joint_dict in datablock[0]:
        # Clean up namespaces in the datablock
        if(':' in joint_dict['name']):
            name = joint_dict['name'].split(':')[-1]
        else:
            name = joint_dict['name']
        joint_node = pm.PyNode(name)

        if(joint_dict['parent'] != None):
            if(':' in joint_dict['parent']):
                parent_name = joint_dict['parent'].split(':')[-1]
            else:
                parent_name = joint_dict['parent']

            print('Parenting {} to {}'.format(joint_node, parent_name))

            pm.parent(joint_node, parent_name)
