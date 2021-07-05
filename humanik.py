'''
humanik.py

For automated interactions between HumanIK and our rigging standard.
'''

import pymel.core as pm
import pymel.core.datatypes as dt
import globals

# HIK uses arbitrary indices like so for each body part.
HIK_CHARACTERIZE_MAP = {
    'Head':15,
    'Hips':1,
    'LeftArm':9,
    'LeftFoot':4,
    'LeftForeArm':10,
    'LeftHand':11,
    'LeftLeg':3,
    'LeftShoudler':18,
    'LeftToeBase':16,
    'LeftUpLeg':2,
    'Neck':20,
    'RightArm':12,
    'RightFoot':7,
    'RightForeArm':13,
    'RightHand':14,
    'RightLeg':6,
    'RightShoulder':19,
    'RightToeBase':17,
    'RightUpLeg':5,
    'Spine':8,
    'Spine1':23
}


def controls_to_t_pose(z_up=False, 
    arm_targets=globals.NAME_STANDARD['ik_arm'], 
    leg_targets=globals.NAME_STANDARD['ik_leg']):
    '''
    Set the rig in-scene to t-pose
    '''

    # Steps to get the arm in t:
    # 1- Get the length of the arm-joints and store it.
    # Match Z trans of IK wrist and IK PV to shoulder's bone.
    # Move IK wrist position to arm-length away from shoulder joint for perfectly straight arms.
    # Mirror all these numbers to the right side.

    # Steps to get the legs in t:
    # Same as above, measure the bone length, move end and PV in alignment, but this time in Y (man
    # I hate Z up.)

    # Getting total length of the arm:
    shoulder_pos = dt.Vector(pm.xform(arm_targets['shoulder_joint'], q=True, t=True, ws=True))
    elbow_pos = dt.Vector(pm.xform(arm_targets['elbow_joint'], q=True, t=True, ws=True))
    wrist_pos = dt.Vector(pm.xform(arm_targets['wrist_joint'], q=True, t=True, ws=True))
    arm_length = ((shoulder_pos - elbow_pos) + (elbow_pos - wrist_pos))

    # Getting length of the leg:
    hip_pos = dt.Vector(pm.xform(arm_targets['shoulder_joint'], q=True, t=True, ws=True))
    elbow_pos = dt.Vector(pm.xform(arm_targets['elbow_joint'], q=True, t=True, ws=True))
    wrist_pos = dt.Vector(pm.xform(arm_targets['wrist_joint'], q=True, t=True, ws=True))
    arm_length = ((shoulder_pos - elbow_pos) + (elbow_pos - wrist_pos))

    # Move controls to matching up coordinate.

