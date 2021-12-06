# skeleton.py
# Matt Riche 2021
# sr_suite_utilities module for editing and creating joints


import coord_math as cmath
from constants import GENERIC_KEYS, SR_MAPPING
import orientation as ori
import pymel.core as pm
import pymel.core.datatypes as dt
import fbx_utils as fbx
import constraints as cns

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
    DEPRECATED BY copy_skeleton()

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


def import_as_datablock():
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


def construct_from_datablock(datablock, prefix='data_'):
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
        rebuilt_joint = pm.joint(p=ws_euler, n=(prefix + joint_dict['name']))
        print("built {}".format(rebuilt_joint))
        rebuilt_joint.rotateOrder.set(joint_dict['rotate_order'])
        rebuilt_joint.jointOrient.set(j_orient)

    return


def translate_from_scene(data_block):
    '''
    A subprocess of skeleton-matching.
    orient all the contents created by the datablock to the "matches" found in scene.
    This is to be run after 'construct_from_datablock' as put the rebuilt joints in the scene.
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

    DEPRECATED
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


def hierarchy_from_datablock(datablock, prefix='data_'):
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
        print("Looking for {}".format(prefix + name))
        joint_node = pm.PyNode(prefix + name)

        if(joint_dict['parent'] != None):
            if(':' in joint_dict['parent']):
                parent_name = joint_dict['parent'].split(':')[-1]
            else:
                parent_name = joint_dict['parent']

            parent_name = prefix + parent_name

            print('Parenting {} to {}'.format(joint_node, parent_name))

            pm.parent(joint_node, parent_name)


def build_reoriented_skeleton(our_basejoint, datablock, standard, data_prefix='data_'):
    '''
    Given the base joint of our rig, make a copy of the bones to map on.
    Then using the client standard datablock and a temporarily rebuilt copy, we start to use our 
    mapping tech to intelligently make our first copy oriented the same as our second copy.

    usage:
    build_reoriented_skeleton([joint at top of our standard rig], datablock, standard)
    our_basejoint = A joint node found at the top of the hierarchy of our rig.
    datablock = the imported datablock built from  'import_as_datablock'
    standard
    '''

    new_base = copy_skeleton(base_joint=our_basejoint, prefix='skel_match')

    target_joints = (pm.listRelatives(new_base, ad=True, type='joint') + [new_base])

    # Prepare to collect some feedback stats.
    result = {'skipped':[], 'smart':[], 'dumb':[]}
    dumb_list = []

    for map in GENERIC_KEYS:
        print("mapping is {}".format(map))
        key = map[0]
        children = map[1]

        if((SR_MAPPING[key] == '') or (standard[key] == '')):
            print("Skipping {}...".format(map[0]))
            result['skipped'].append(map[0])
            continue

        print("Generic Key {}:".format(key))
        if(len(children) < 1):
            print("...no children.")
            target_child = None
            source_child = None
        elif(len(children) == 1):
            print("...one child: {}".format(children[0]))
            if(SR_MAPPING[children[0]] != ''):
                target_child = pm.PyNode(SR_MAPPING[children[0]])
            else:
                target_child = None
            if(standard[children[0]] != ''):
                source_child = pm.PyNode(data_prefix + standard[children[0]])
            else:
                source_child = None
        elif(len(children) > 1):
            print("...multiple children: {}".format(children))
            target_child = None
            source_child = None

        # The string "remap" is a hacky way of making sure we are operating on the copyied skel.
        local_joint = ("skel_match_" + SR_MAPPING[key])
        print("Local joint name is {}".format(local_joint))
        client_joint = standard[key]

        try:
            source_joint = pm.PyNode(data_prefix + client_joint)
        except:
            pm.error("Couldn't get a pynode of {}.  Is there two in the scene?".
                format(client_joint))

        try:
            target_joint = pm.PyNode(local_joint)
        except:
            pm.warning("couldn't get a pynode of  {}.  Is there two in the scene?".
                format(local_joint))
            continue
        print("Copying orientation from {} to {}".format(source_joint, target_joint))

        if(source_child != None):
            ori.smart_copy_orient(
                subject=source_joint, target=target_joint, s_child=source_child, 
                t_child=target_child
                )
        else:
            ori.dumb_copy_orient(subject=source_joint, target=target_joint)
            dumb_list.append(target_joint.name())


    print("Oriented {} joints using a \"dumb copy orient\", please double check these:\n{}".
        format(len(dumb_list), dumb_list))
    print("Done... \n")

    return


def copy_orient_from_example(datablock, standard):
    '''

    Possibly deprecated:
    Given a skeleton of our standard in scene, and a skeleton of the client standard freshly rebuilt
    start to copy the axis as intelligently as possible from the latter to the former.
    '''

    # Prepare to collect some feedback stats.
    result = {'skipped':[], 'smart':[], 'dumb':[]}
    dumb_list = []

    print (GENERIC_KEYS)

    for map in GENERIC_KEYS:
        print("Mapping is \"{}\"".format(map))
        key = map[0]
        children = map[1]

        if((SR_MAPPING[key] == '') or (standard[key] == '')):
            print("Skipping {}...".format(map[0]))
            result['skipped'].append(map[0])
            continue

        print("Generic Key {}:".format(key))
        if(len(children) < 1):
            print("...no children.")
            target_child = None
            source_child = None
        elif(len(children) == 1):
            print("...one child: {}".format(children[0]))
            if(SR_MAPPING[children[0]] != ''):
                target_child = pm.PyNode(SR_MAPPING[children[0]])
            else:
                target_child = None
            if(standard[children[0]] != ''):
                source_child = pm.PyNode(standard[children[0]])
            else:
                source_child = None
        elif(len(children) > 1):
            print("...multiple children: {}".format(children))
            target_child = None
            source_child = None

        local_joint = SR_MAPPING[key]
        client_joint = standard[key]

        try:
            source_joint = pm.PyNode(client_joint)
        except:
            pm.error("Couldn't get a pynode of {}.  Is there two in the scene?".
                format(client_joint))

        try:
            target_joint = pm.PyNode(local_joint)
        except:
            pm.error("couldn't get a pynode of  {}.  Is there two in the scene?".
                format(target_joint))
        print("Copying orientation from {} to {}".format(source_joint, target_joint))

        # Must store all constraints and removed them so that the orientation can happen.  
        cons_on_target = cns.identify_constraints(target_joint)
        stored_cons = []
        for constraint_node in cons_on_target:
            print("Attempting to store constraint node: {}".format(constraint_node))
            stored_cons.append(cns.StoredConstraint(constraint_node))

        if(source_child != None):
            ori.smart_copy_orient(
                subject=source_joint, target=target_joint, s_child=source_child, 
                t_child=target_child
                )
        else:
            ori.dumb_copy_orient(subject=source_joint, target=target_joint)
            dumb_list.append(target_joint.name())

        # Now rebuild all the constraints.
        for cons in stored_cons:
            print("Rebuilding {}".format(cons.name))
            cons.rebuild()

    print("Oriented {} joints using a \"dumb copy orient\", please double check these:\n{}".
        format(len(dumb_list), dumb_list))
    print("Done... \n")

        
def copy_skeleton(base_joint=None, prefix=None, base_name='duplicate'):
    '''
    Given a base_joint as a argument or selection, make a copy of that skeleton that is stripped of
    all constraints.
    
    usage:
    copy_skeleton(base_joint=[joint])
    base_joint - The joint at the top of a rigs hierarchy.
    '''

    # If no argument is given, fall back to viewport selection
    if(base_joint is None):
        base_joint = pm.ls(sl=True)[0]
        print("No args given, using viewport selection {}".format(base_joint))

    base_joint_old_name = base_joint.name(long=None)

    decendent_joints = pm.listRelatives(base_joint, ad=True, type='joint') + [base_joint]
    # Make a list of things that aren't joints (by negating the above list from the full list.)
    decendent_garbage = ([l for l in pm.listRelatives(base_joint, ad=True) if l not in 
        decendent_joints])
    duplicated_joints = pm.duplicate(decendent_joints, ic=False, un=False)

    # We find out which name is the new base, since the base will be the only name that is forced 
    # to be unique.
    duplicated_base = None
    for joint in duplicated_joints:
        # Weirdly, 'long=None' is a third option for this otherwise boolean flag.  Will return 
        # absolute name, no path. This is essential for the "is not unique" check I'm doing.
        if(len(pm.ls(joint.name(long=None))) > 1):
            # When len of the joint name (when long=None only) is > 1, that's proof it's not unique.
            continue
        else:
            # The unique one that was created during duplication is garunteed to be our base.
            duplicated_base = joint
            break

    # Let's assert this was found and crash if it wasn't.
    if(duplicated_base is None):
        pm.error("The duplicated base joint wasn't determined-- it never became unique after copy?")

    # Parent the base to world.
    pm.parent(duplicated_base, w=True)

    if(prefix is not None):
        for joint in duplicated_joints:
            # Give it a unique name:
            new_name = (prefix + '_' + joint.name(long=None))
            print("{} renamed to {}".format(joint.name(long=None), new_name))
            pm.rename(joint, new_name)
        duplicated_base.rename(prefix + '_' + base_joint_old_name)

    else:
        # Without a prefix, duplicate name must be fixed up.
        duplicated_base.rename("duplicate_{}".format(base_joint_old_name))

    # Clean up all constraints that might have gotten built due to the downstream copying.
    pm.delete(decendent_garbage)

    return duplicated_base

