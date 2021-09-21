'''
orientation.py

module for altering the orientation of bones based on mapping swaps.
'''

import pymel.core as pm
import pymel.core.datatypes as dt

def swap_axis(subject, swap_map, orient_joint=False):
    '''
    Given the target axis that represents the new way it should be oriented, shuffled the contents 
    of the matrix
    '''

    # If the node is a joint, begin the process by moving joint orientation to eular rotations
    if(orient_joint):
        subject.rotate.set(subject.jointOrient.get())
        subject.jointOrient.set(0,0,0)

    s_matrix = subject.getMatrix()  
    s_translate = dt.Vector(s_matrix.translate)

    fresh_matrix = dt.Matrix()

    s_x_vec = dt.Vector(s_matrix[0][:3])
    s_y_vec = dt.Vector(s_matrix[1][:3])
    s_z_vec = dt.Vector(s_matrix[2][:3])

    # Vector replacements case by case.
    if(swap_map[0] == 'x'):
        t_x_vec = s_x_vec
    elif(swap_map[0] == '-x'):
        t_x_vec = -s_x_vec
    elif(swap_map[0] == 'y'):
        t_x_vec = s_y_vec
    elif(swap_map[0] == '-y'):
        t_x_vec = -s_y_vec
    elif(swap_map[0] == 'z'):
        t_x_vec = s_z_vec
    elif(swap_map[0] == '-z'):
        t_x_vec = -s_z_vec
    else:
        pm.error("Bad X input string for new-axis mapping")

    if(swap_map[1] == 'x'):
        t_y_vec = s_x_vec
    elif(swap_map[1] == '-x'):
        t_y_vec = -s_x_vec
    elif(swap_map[1] == 'y'):
        t_y_vec = s_y_vec
    elif(swap_map[1] == '-y'):
        t_y_vec = -s_y_vec
    elif(swap_map[1] == 'z'):
        t_y_vec = s_z_vec
    elif(swap_map[1] == '-z'):
        t_y_vec = -s_z_vec
    else:
        pm.error("Bad Y input string for new-axis mapping")

    # We used to use the third axis, but I think to avoid weird bad scales, we will get the cross
    # product instead.
    t_z_vec = t_x_vec.cross(t_y_vec)
    t_x_vec.normalize()
    t_y_vec.normalize()
    t_z_vec.normalize()

    # Reconstruct the matrix values:
    m0 = list(t_x_vec.get())
    m1 = list(t_y_vec.get())
    m2 = list(t_z_vec.get())

    m3 = list(s_translate.get())
    m3.append(1.0)

    # Reconstruct the forth column:
    for row in [m0, m1, m2]:
        row.append(0.0)

    # Reconstruct the translate
    fresh_matrix = dt.Matrix(m0, m1, m2, m3)

    # Apply the newly constructed matrix
    subject.setMatrix(fresh_matrix)

    # If node is a joint, we need to apply this to the jo values.
    if(orient_joint):
        subject.jointOrient.set(subject.rotate.get())
        subject.rotate.set(0, 0, 0)

    return


def find_down_axis(joint_node, child_name=None):
    '''
    Given a joint node, find the vector between itself and it's child, and compare all axis in the 
    matrix to that.

    vector - If True, return value is a dt.Vector of the "down skeleton" axis.
    '''

    if(child_name == None):
        child_list = (
            [child for child in pm.listRelatives(joint_node, c=True) 
            if(child.type() in ['transform', 'joint'])]
            )

        print("DEBUG: Aiming at {}".format(child_list[0]))
        # This process can't ever pick a "favored" child joint if there's more than one-- I've 
        # chosen to complete crash this process
        if(len(child_list) > 1):
            pm.error("find_down_axis() won't work on multi-child joints.  {} has {} child joints."
            .format(joint_node.name(), len(child_list)))
            return

        elif(len(child_list) < 1):
            return None
        else:
            child = child_list[0]
    else:
        child = pm.PyNode(child_name)

    # Find the vector between the joint and the child.
    print("Getting the vector aimed down at the child...")
    joint_ws = dt.Vector(pm.xform(joint_node, q=True, ws=True, t=True))
    child_ws = dt.Vector(pm.xform(child, q=True, ws=True, t=True))
    down_vec = child_ws - joint_ws
    down_vec.normalize()

    print("WE have the downvec, it's {}".format(down_vec))

    # Now that we have the vector pointing to the next joint, which find which part of the matrix
    # has the closest angle to it
    joint_matrix = joint_node.getMatrix()
    print("We got the matrix, it's {}".format(joint_matrix))
    # Take apart the matrix into vectors for each axis
    x_axis = joint_matrix[0][:3]
    y_axis = joint_matrix[1][:3]
    z_axis = joint_matrix[2][:3]

    # Collect a list of angles betwee existing axis and our "down vector".  The smallest angle will 
    # be from the intended "down axis"
    angle_list = []
    for axis_vec in [x_axis, y_axis, z_axis]:
        print("comparing:\n{}\n{}".format(down_vec, axis_vec))
        if(down_vec.get() != axis_vec.get()):
            print("Not equal enough")
            angle_list.append(down_vec.angle(axis_vec))
            print("Appended anyways")
        else:
            print("They were equal")
            angle_list.append(0.0)

    print("We got the angle list...")
    # Get an int 0,1,2 for x,y,z
    smallest_angle = min(angle_list)
    axis_index = angle_list.index(smallest_angle)

    # Prep readable strings instead of the sint:
    axis_strings = ['x', 'y', 'z']

    return (axis_strings[axis_index], down_vec)


def closest_axis(target_joint, source_joint, exclude_axis=None):
    '''
    Find which two axis between two joints have similarly parallel alignment between bones, 
    in order to use this relationship to determine the alignment later.

    usage:
    closest_axis(target_joint, source_joint, exclude_axis=(string))
    - target_joint: (pynode) of the joint we are snapping to.
    - source_joint: pynode of the joint we are aligning by.
    - excluse_axis: Char value of the previously determined "down axis" that doesn't need checking.

    returns:
    (tuple) (closest matching source axis, closest matching target axis, closest target's vector)
    '''

    target_matrix = target_joint.getMatrix()
    source_matrix = source_joint.getMatrix()

    target_angles = []

    source_x_axis = dt.Vector(source_matrix[0][:3])
    source_y_axis = dt.Vector(source_matrix[1][:3])
    source_z_axis = dt.Vector(source_matrix[2][:3])

    target_x_axis = dt.Vector(target_matrix[0][:3])
    target_y_axis = dt.Vector(target_matrix[1][:3])
    target_z_axis = dt.Vector(target_matrix[2][:3])

    source_vectors = [
        source_x_axis, source_y_axis, source_z_axis, -source_x_axis, -source_y_axis, -source_z_axis
    ]
    target_vectors = [
        target_x_axis, target_y_axis, target_z_axis]

    axis = ['x', 'y', 'z', '-x', '-y', '-z']

    # Get the "exclude_axis" flag's demands sorted-- a 'None' gets skipped later.
    if(exclude_axis != None):
        if(exclude_axis in axis):
            source_vectors[axis.index(exclude_axis)] = None
        else:
            pm.error("Bad string given to 'exlude_axis' flag.  Must be ['x','y','z','-x','-y','-z']")

    smallest_angle = 360.1
    for s_vector in source_vectors:
        # Check if this axis has been excluded and continue in that case
        if s_vector is None:
            continue
        for t_vector in target_vectors:
            if(s_vector.angle(t_vector) < smallest_angle):
                smallest_angle = s_vector.angle(t_vector)
                t_match_axis = axis[target_vectors.index(t_vector)]
                s_match_axis = axis[source_vectors.index(s_vector)]
                t_match_vec = s_vector

    return (s_match_axis, t_match_axis, t_match_vec)


def aim_at(node, target=None, vec=None, pole_vec=(0,1,0), axis=0, pole=1):
    '''
    Aim's a node's axis at another point in space and a "pole axis" down a normalized vector.
    Operates in place on the given node-- returns nothing.

    node - PyNode of the transform to be aimed
    target - PyNode of object to be aimed at (if vec == None)
    vec - dt.Vector of direction to aim in (if target == None)
    pole_vec - A dt.Vector that aims toward the "pole" of this aim constraint.
    axis - the axis along which to aim down. (enumated x,y,z where x=0)
    pole - the "pole" axis, which will aim at the vec (enumerated x,y,z where x=0)
    '''

    # Check for bad args:
    if(pole == axis):
        pm.error("sr_biped error: Chosen pole and aim axis can't be identical.")

    # Format some vectors into the dt.Vector type
    pole_vec = dt.Vector(pole_vec)
    node_pos = dt.Vector(pm.xform(node, q=True, ws=True, t=True))

    # Sort what we are aiming at:
    # If we got a target, use it.
    if(target != None):
        target_pos = dt.Vector(pm.xform(target, q=True, ws=True, t=True))
        target_vec = target_pos - node_pos
        target_vec.normalize()

        if(vec != None):
            pm.warning("Both vec and node are populated.  Node will take precidence.")

    # If we got a vec, use that instead.
    elif(vec != None):
        target_vec = dt.Vector(vec).normal()

    else:
        pm.error("sr_biped error: Either a vector or a target is required.")
        return

    if(target_vec == pole_vec):
        pm.error("sr_biped error: Target vector and pole vector are identical-- result will be "
            "unsafe.")

    print(target_vec)

    # Step two, "unconstrained" vec; cross product of normalized vector and normalized pole vector 
    # is found and stored.
    last_vec = target_vec.cross(pole_vec)
    last_vec.normalize()

    # Step three, we "clean" the pole vector by getting the cross product of the aim and the 
    # "unconstrained" axis vector.
    clean_pole = target_vec.cross(last_vec)
    clean_pole.normalize()

    # Before we proceed, we shuffle based on the incoming arguments.  Chosen axis to aim...
    x_axis_vec = y_axis_vec = z_axis_vec = None
    remaining_vectors = { 'x':True, 'y':True, 'z':True }

    if(axis == 0):
        x_axis_vec = target_vec
        remaining_vectors.pop('x')
    elif(axis == 1):
        y_axis_vec = target_vec
        remaining_vectors.pop('y')
    elif(axis == 2):
        z_axis_vec = target_vec
        remaining_vectors.pop('z')

    # And unconstrained.
    if(pole == 0):
        x_axis_vec = clean_pole
        remaining_vectors.pop('x') 
        # Note it should be impossible to pop the same twice at this point due to the early check.

    elif(pole == 1):
        y_axis_vec = clean_pole
        remaining_vectors.pop('y')
    elif(pole == 2):
        z_axis_vec = clean_pole
        remaining_vectors.pop('z')

    # Decide which axis gets the "last_vec" applied based on what remains in the dict
    if (remaining_vectors.keys()[0] == 'x'):
        x_axis_vec = last_vec
    elif (remaining_vectors.keys()[0] == 'y'):
        y_axis_vec = last_vec
    elif (remaining_vectors.keys()[0] == 'z'):
        z_axis_vec = last_vec
    else:
        pm.error('No good axis keys remaining in the "remaining_vectors" dict.')

    for last_axis in ['x_axis_vec', 'y_axis_vec', 'z_axis_vec']:
        if(eval(last_axis + ' == None') == True):
            exec('{} = last_vec'.format(last_axis))
            break

    # Turn the axis vectors into lists to slot into the Matrix:
    m0 = list(x_axis_vec)
    m1 = list(y_axis_vec)
    m2 = list(z_axis_vec)

    # Recompose transform data here so it lands in a list to put inside the matrix correctly.
    m3 = list(node_pos.get())

    # Fabricate the rightmost columns constant state.
    m0.append(0.0)
    m1.append(0.0)
    m2.append(0.0)
    m3.append(1.0)

    # Step four, apply the values of each vector to the correct place in the matrix.
    aimed_matrix = dt.Matrix(m0, m1, m2, m3)

    node.setMatrix(aimed_matrix)

    print(aimed_matrix.formated())

    return


def trans_align(orient, orient_like, source_child=None):
    '''
    Given a transform node that is oriented a certain way, and a comparitive transform node that is
    not oriented alike, take the "major axis orientation" and apply it to the first node without 
    changing the finer details of it's orientation-- essentially, keep the orientation but swap 
    the chosen axis used in the orientation.

    This is a long process-- see find_down_axis and closest_axis.  The process essentially
    identifies the "down axis" as something to aim at, and the closest_axis decides on the 
    pole axis, and a matrix-edit orients it using those two axis with old vectors given new matrix
    positions.

    orient - transform node to orient
    orient_like - transform node to emulator the axis-orientation of
    source_child - optional string to identify the orient_like node in the case that where it should
        aim is not presently it's child (corner case that comes from skeleton match.)   
    '''

    pm.select(clear=True)

    print("Axis aligning {} to {}".format(orient, orient_like))

    # Find the down vector of orient
    target_down_vec = find_down_axis(orient)[1]
    if(target_down_vec in ['ROOT', 'MULTI_CHILD']):
        print("Can't orient {}, as it's {}".format(orient_like, target_down_vec))
        return
 
    # Find the down axis of the source
    if(source_child == None):
        source_down_axis = find_down_axis(orient_like)[0]
    else:
        source_down_axis = find_down_axis(orient_like, source_child)
    
    print(
        "'down joint' vector on our skeleton is {}, replacing with theirs; {}".format(
            target_down_vec, source_down_axis
            )
        )

    print("Working out a pole vector by choosing near-match axis...")
    # Find "next best" axis to use as a pole
    source_match_axis, target_match_vec = closest_axis(
        orient, orient_like, exclude_axis=source_down_axis[0]
        )

    # Turn axis strings into ints:
    axis = ['x', 'y', 'z']
    print("SOURCED DOWN AXIS IS {}".format(source_down_axis[0]))
    aim_axis = axis.index(source_down_axis[0])

    if('-' in source_down_axis[0]):
        print("This down axis is reversed.  Altering the axis string to treat it as normal now.")
        source_down_axis[0].replace('-', '')

    if('-' in source_match_axis):
        print("This pole axis is reversed.  Altering the axis string to treat it as normal now.")
        print(source_match_axis)
        source_match_axis = source_match_axis.replace('-', '')
        print(source_match_axis)

    pole_axis = axis.index(source_match_axis)

    # Now at this point, we have a vector to aim at and a pole, and we know which to make which.
    try:
        aim_at(
            orient, vec=target_down_vec, pole_vec=target_match_vec, axis=aim_axis, pole=pole_axis
            )
    except:
        print("WARNING COULDN'T AIM--- IS IT BECAUSE OF THE NEGATIVE NOT BEING EXCLUDED?")

    return


def swap_rot_for_jo(joint_node):
    '''
    Swaps rotation of transform for the jointOrient values.

    joint_node - PyNode of a joint in scene.
    '''

    jo = joint_node.jointOrient.get()
    ro = joint_node.rotate.get()

    joint_node.jointOrient.set(ro)
    joint_node.rotate.set(jo)

    return

