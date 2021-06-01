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
