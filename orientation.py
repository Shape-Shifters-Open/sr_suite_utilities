'''
orientation.py

module for altering the orientation of bones based on mapping swaps.
'''

import pymel.core as pm
import pymel.core.datatypes as dt


def smart_copy_orient(subject=None, target=None, s_child=None, t_child=None, reparent=True):
    '''
    'smartly' copies the orientation from one joint to another, preserving the actual orientation by
    degrees, but fully re-aligning the axial orientation.

    Usage:
    smart_copy_orient(subject=(PyNode), target=(PyNode))
    subject - the joint upon which to paste the orientation
    target - the joint from which to copy the orientation from    
    '''
    ui_mode = False
    if(subject == None or target == None):
        ui_mode = True
        selection = pm.ls(sl=True)
        if(len(selection) != 2):
            pm.error("Must select exactly two joints for this operation.")
        else:
            subject = selection[0]
            target = selection[1]

    # The angle-discovering and comparing operations that make this possible:
    # Step one, find the 'down' vector-- the vector that points to the child joint and record the 
    # "swap"
    s_down_vec = find_down_axis(subject, child_name=s_child)
    t_down_vec = find_down_axis(target, child_name=t_child)

    if(s_down_vec == None or t_down_vec == None):
        if(s_child==None or t_child==None):
            pm.error("There's no child joint to derive a down vector from on one or both {} and {}"
            .format(subject, target))

    # Get the child to peform the deparent:
    if(reparent):
        if(t_child is None):
            print("Finding child...")
            child_joint =pm.listRelatives(target, c=True)[0]
        else:
            child_joint = pm.PyNode(t_child)
        print("Deparenting {}".format(child_joint))
        pm.parent(child_joint, w=True, a=True)

    down_swap = (s_down_vec[0], t_down_vec[0])

    # Step two, find the closest matching angles between the source and target, while excluding the 
    # down angles:
    side_swap = closest_axis(subject, target, s_exclude_axis=down_swap[0], 
        t_exclude_axis=down_swap[1])[:2]

    # Finally, knowing the swappable match facing down/aim, and the swappable match that is used as
    # an "up vector", perform the swap by deconstructing and re-constructing the matrix:
    swap_axis(target, aim_swap=down_swap, up_swap=side_swap, orient_joint=True)

    if(reparent):
        pm.parent(child_joint, target, a=True)

    # Finish by selecting target.
    if(ui_mode):
        pm.select(target, r=True)

    return


def dumb_copy_orient(subject=None, target=None):
    '''
    Given a target pynode and a subject pynode (Or selections), match the orientation of the target 
    with the subjects.
    '''

    if(subject == None or target == None):
        selection = pm.ls(sl=True)
        if(len(selection) != 2):
            pm.error("Must select exactly two joints for this operation.")
        else:
            subject = selection[0]
            target = selection[1]

    copied_matrix = subject.getMatrix(worldSpace=True)
    target.setMatrix(copied_matrix, worldSpace=True)


def swap_axis(subject, aim_swap, up_swap, orient_joint=False, parent_safe=True):
    '''
    Given the target axis that represents the new way it should be oriented, shuffle the contents 
    of the matrix such that the alignment's axis can be switched
    '''

    # Swap relationships come in as tuples-- the second index being the axis to be replaced, and the 
    # first being the axis to replace it with.  We assign the xfor, yfor, zfor vars we use later
    # based on these tuples.
    xfor = yfor = zfor = None
    if(aim_swap[1] == 'x'):
        xfor = aim_swap[0]
    elif(aim_swap[1] == 'y'):
        yfor = aim_swap[0]
    elif(aim_swap[1] == 'z'):
        zfor = aim_swap[0]

    if(up_swap[1] == 'x'):
        xfor = up_swap[0]
    if(up_swap[1] == 'y'):
        yfor = up_swap[0]
    if(up_swap[1] == 'z'):
        zfor = up_swap[0]

    # After the shuffling has been done from the tuples to the 'fors', we can sanitize we got enough
    # axis specified.  Without enough swaps to derive a full 4x4 matrix, we throw an error.
    axis_count = 0
    if(xfor != None):
        axis_count += 1
    if(yfor != None):
        axis_count += 1
    if(zfor != None):
        axis_count += 1

    if(axis_count < 2):
        pm.error(
            "Not enough swap axis were specified.  Use at least two of xfor, yfor, zfor arguments"
            )
        return

    # If the node is a joint, begin the process by moving joint orientation to eular rotations
    if(orient_joint):
        subject.rotate.set(subject.jointOrient.get())
        subject.jointOrient.set(0,0,0)

    s_matrix = subject.getMatrix(worldSpace=True)  
    s_translate = dt.Vector(s_matrix.translate)

    fresh_matrix = dt.Matrix()

    # Populate the source vectors with the contents of the source matrix.
    s_x_vec = dt.Vector(s_matrix[0][:3])
    s_y_vec = dt.Vector(s_matrix[1][:3])
    s_z_vec = dt.Vector(s_matrix[2][:3])

    # Initialize the target vectors as None, so that we can discover which one should be a cross
    # product on account of being left out by the "x/y/zfor" flags.
    t_x_vec = None
    t_y_vec = None
    t_z_vec = None

    # Vector replacements, case by case.
    if(xfor == None):
        pass
    elif(xfor == 'x'):
        t_x_vec = s_x_vec
    elif(xfor == 'y'):
        t_x_vec = s_y_vec
    elif(xfor == 'z'):
        t_x_vec = s_z_vec
    elif(xfor == '-x'):
        t_x_vec = -s_x_vec
    elif(xfor == '-y'):
        t_x_vec = -s_y_vec
    elif(xfor == '-z'):
        t_x_vec = -s_z_vec
    else:
        pm.error("Bad input for xfor flag; must be a letter axis x y z, or -x,-y,-z.")
        return

    if(yfor == None):
        pass
    elif(yfor == 'x'):
        t_y_vec = s_x_vec
    elif(yfor == 'y'):
        t_y_vec = s_y_vec
    elif(yfor == 'z'):
        t_y_vec = s_z_vec
    elif(yfor == '-x'):
        t_y_vec = -s_x_vec
    elif(yfor == '-y'):
        t_y_vec = -s_y_vec
    elif(yfor == '-z'):
        t_y_vec = -s_z_vec
    else:
        pm.error("Bad input for yfor flag; must be a letter axis x y z, or -x,-y,-z.")
        return
    
    if(zfor == None):
        pass
    elif(zfor == 'x'):
        t_z_vec = s_x_vec
    elif(zfor == 'y'):
        t_z_vec = s_y_vec
    elif(zfor == 'z'):
        t_z_vec = s_y_vec
    elif(zfor == '-x'):
        t_z_vec = -s_x_vec
    elif(zfor == '-y'):
        t_z_vec = -s_y_vec
    elif(zfor == '-z'):
        t_z_vec = -s_z_vec
    else:
        pm.error("Bad input for zfor flag; must be a letter axis x y z, or -x,-y,-z.")
        return

    # Check which axis is the "None" and derive it with cross products.
    if(t_x_vec == None):
        print("X vector for target in this case will be cross product.")
        t_y_vec.normalize()
        t_z_vec.normalize()
        t_x_vec = t_y_vec.cross(t_z_vec)
        t_x_vec.normalize()

    elif(t_y_vec == None):
        print("Y vector for target in this case will be cross product.")
        t_x_vec.normalize()
        t_z_vec.normalize()
        t_y_vec = t_x_vec.cross(t_z_vec)
        t_y_vec.normalize()

    elif(t_z_vec == None):
        print("Z vector for target in this case will be cross product.")
        t_x_vec.normalize()
        t_y_vec.normalize()
        t_z_vec = t_x_vec.cross(t_y_vec)
        t_z_vec.normalize()

    # Reconstruct the matrix values:
    m0 = list(t_x_vec.get())
    m1 = list(t_y_vec.get())
    m2 = list(t_z_vec.get())

    m3 = pm.xform(subject, t=True, q=True, ws=True)
    m3.append(1.0)

    # Reconstruct the forth column:
    for row in [m0, m1, m2]:
        row.append(0.0)

    # Reconstruct the translate
    fresh_matrix = dt.Matrix(m0, m1, m2, m3)

    # Since Maya's own jointOrient command is pretty weak, we will temporarily de-parent things.
    if(parent_safe):
        child_list = (
            [child for child in pm.listRelatives(subject, c=True) 
            if(child.type() in ['transform', 'joint'])]
            )
        print("Got child list:\n{}".format(child_list))
        if(len(child_list) > 0):
            for child in child_list:
                pm.parent(child, w=True)[0]
        parents = pm.listRelatives(subject, p=True)
        if(len(parents) == 1):
            parent_joint = parents[0]
        else:
            parent_joint = None
        pm.parent(subject, w=True)

    # Apply the newly constructed matrix
    subject.setMatrix(fresh_matrix, worldSpace=True)

    if(parent_safe):
        for child in child_list:
            pm.parent(child, subject)
        if(parent_joint != None):
            pm.parent(subject, parent_joint)

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
    joint_ws = dt.Vector(pm.xform(joint_node, q=True, ws=True, t=True))
    child_ws = dt.Vector(pm.xform(child, q=True, ws=True, t=True))
    down_vec = child_ws - joint_ws
    down_vec.normalize()

    # Now that we have the vector pointing to the next joint, which find which part of the matrix
    # has the closest angle to it
    joint_matrix = joint_node.getMatrix(worldSpace=True)
    # Take apart the matrix into vectors for each axis
    x_axis = dt.Vector(joint_matrix[0][:3])
    y_axis = dt.Vector(joint_matrix[1][:3])
    z_axis = dt.Vector(joint_matrix[2][:3])

    # Collect a list of angles betwee existing axis and our "down vector".  The smallest angle will 
    # be from the intended "down axis"
    angle_list = []
    for axis_vec in [x_axis, y_axis, z_axis]:
        if(down_vec.normal() != axis_vec.normal()):
            angle_list.append(down_vec.angle(axis_vec))
        else:
            angle_list.append(0.0)
    # Get an int 0,1,2 for x,y,z
    smallest_angle = min(angle_list)
    axis_index = angle_list.index(smallest_angle)

    # Prep readable strings instead of the sint:
    axis_strings = ['x', 'y', 'z']

    return (axis_strings[axis_index], down_vec)


def closest_axis(source_joint, target_joint, s_exclude_axis=None, t_exclude_axis=None):
    '''
    Find which two axis between two joints have similarly parallel alignment between bones, 
    in order to use this relationship to determine the alignment later.

    usage:
    closest_axis(target_joint, source_joint, s_exclude_axis=(string))
    - target_joint: (pynode) of the joint we are snapping to.
    - source_joint: pynode of the joint we are aligning by.
    - excluse_axis: Char value of the previously determined "down axis" that doesn't need checking.

    returns:
    (tuple) (closest matching source axis, closest matching target axis, closest target's vector)
    '''

    target_matrix = target_joint.getMatrix(worldSpace=True)
    source_matrix = source_joint.getMatrix(worldSpace=True)

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

    # Get the "s_exclude_axis" flag's demands sorted-- a 'None' gets skipped later.
    if(s_exclude_axis != None):
        if(s_exclude_axis in axis):
            source_vectors[axis.index(s_exclude_axis)] = None
        else:
            pm.error("Bad string for 's_exlude_axis' flag.  Must be ['x','y','z','-x','-y','-z']")

    if(t_exclude_axis != None):
        if(t_exclude_axis in axis):
            target_vectors[axis.index(t_exclude_axis)] = None
        else:
            pm.error("Bad string for 's_exlude_axis' flag.  Must be ['x','y','z']")


    smallest_angle = 360.1
    for s_vector in source_vectors:
        # Check if this axis has been excluded and continue in that case
        if s_vector is None:
            continue
        for t_vector in target_vectors:
            if(t_vector == None):
                continue
            if(s_vector.angle(t_vector) < smallest_angle):
                smallest_angle = s_vector.angle(t_vector)
                t_match_axis = axis[target_vectors.index(t_vector)]
                s_match_axis = axis[source_vectors.index(s_vector)]
                t_match_vec = s_vector

    return (s_match_axis, t_match_axis, t_match_vec)



def aim_at(subject, target, up_vector=(0.0, 0.0, 1.0), aim_axis=0, up_axis=2):
    '''
    Aims the subject node down the target node, and twists it to the provided up-vector.
    Axis involved are specificially defined as 0-2, for x-z.
    
    usage:
    aim_at(PyNode, PyNode, up_vector=(float, float, float), aim_axis=int, up_axis=int)
    '''

    fix_determinant = False # A flag to fix negative determinants

    subject_position = subject.getTranslation(space='world')
    target_position = target.getTranslation(space='world')

    aim_vector = target_position - subject_position
    aim_vector.normalize()

    up_vector_scoped = dt.Vector(up_vector) # named to separate it from the arg.
    up_vector_scoped.normalize()

    last_vector = up_vector_scoped.cross(aim_vector)
    last_vector.normalize()

    # Some combination of chosen axis will create a negative determinent.  This gets reconciled by
    # the scale becoming negative.
    flip_combos = [(0,1), (1,2), (2,0)]
    if((aim_axis, up_axis) in flip_combos):
        fix_determinant = True # With this flag, we know to re-calc the last_axis.

    up_vector_scoped = aim_vector.cross(last_vector)
    up_vector_scoped.normalize()

    # Now the three vectors are ready, their position inside the matrix has to get chosen.
    axes = ['x', 'y', 'z']

    if(fix_determinant):
        # By re-discovering the cross product at this point, we "reverse" it (not negate it!) which
        # will prevent a negative scale in certain arrangements of the matrix (half of the total 
        # possible configurations have this problem.)
        last_vector = aim_vector.cross(up_vector_scoped)
        last_vector.normalize()
        
    if(aim_axis == 0):
        x_row = list(aim_vector)
        axes.remove('x')
    elif(aim_axis == 1):
        y_row = list(aim_vector)
        axes.remove('y')
    elif(aim_axis == 2):
        z_row = list(aim_vector)
        axes.remove('z')
    else:
        pm.error("Bad axis int given for aim_axis: {}; should be 0,1,2 for x,y,z.".format(aim_axis))

    if(up_axis == 0):
        x_row = list(up_vector_scoped)
        axes.remove('x')
    elif(up_axis == 1):
        y_row = list(up_vector_scoped)
        axes.remove('y')
    elif(up_axis == 2):
        z_row = list(up_vector_scoped)
        axes.remove('z')
    else:
        pm.error("Bad axis int given for up_axis: {}; should be 0,1,2 for x,y,z.".format(up_axis))

    if(axes[0] == 'x'):
        x_row = list(last_vector)
    elif(axes[0] == 'y'):
        y_row = list(last_vector)
    elif(axes[0] == 'z'):
        z_row = list(last_vector)
    else:
        pm.error("Failed to determine last vector.  This is a bug.")

    # Append fourth values to the matrix' right side.
    for row in [x_row, y_row, z_row]:
        row.append(0.0)

    # Create the bottom row of the matrix using the transform of the subject, plus a final 1.0
    trans_row = list(subject_position)
    trans_row.append(1.0)

    new_matrix = dt.Matrix(x_row, y_row, z_row, trans_row)
    subject.setMatrix(new_matrix, worldSpace=True)

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

