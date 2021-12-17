"""
globals.py

Global settings to be read across modules.
"""

srsu_version = "0.1.06"

# Standards requested by SSC clients that differ will have to be in an external JSON eventually, to 
# hide their identity and pipeline design.
NAME_STANDARD = {
    'ik_arm':{
        'shoulder_ctrl':'shoulder_Ctrl',
        'elbow_pv_ctrl':'ArmPV_Ctrl',
        'wrist_ctrl':'armWristIK_Ctrl',
        'shoulder_joint':'armUpr_SHJnt',
        'elbow_joint':'armLwr_SHJnt',
        'wrist_joint':'armWrist_SHJnt',

    },
    'ik_leg':{
        'hip_ctrl':'legUprIK_Ctrl',
        'knee_pv_ctrl':'LegPV_Ctrl',
        'ankle_ctrl':'L_legAnkleIK_Ctrl',
        'hip_joint':'legUpr_SHJnt',
        'knee_joint':'legLwr_SHJnt',
        'ankle_joint':'L_legAnkle_SHJnt',
    }

}