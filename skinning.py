# skinning.py
# Matt Riche 2021
# sr_suite_utilities module for skinning related operations.

import pymel.core as pm
import progbar as pb

def copy_skinweights(source="", target=""):
    '''
    copy_skinweights

    Copy the skin influences from a source (even between unlike pieces of geo) to any number of 
    targets.

    usage:
    copy_skinweights(source=[string/PyNode], target=[string/PyNode])
    
    source - a string or PyNode pointing to a skinned piece of geo.
    target - a string or PyNode pointing to an unskinned piece of geo.
    '''

    # If nothing is supplied by argument, use a selection.
    if(source == "" or target == ""):
        selection = pm.ls(sl=True)
        if(selection == []):
            pm.warning("Must select some skinned geo.")
            return

    source = selection[0]
    del selection[0]
    target = selection

    # Find joints and skinCluster node:
    sourceSkin = find_related_skinCluster(source)
    joints = pm.listConnections((sourceSkin + ".matrix"), d=False, s=True)

    # Start a progress bar
    pb.start_progbar(
        max_value=len(target), message="Copying skins from {} to target(s)".format(source)
        )

    count = 0
    for geo in target:
        # Build a skinCluster node on the target
        #pm.skinCluster()
        print ("Copying skin influences to {}".format(geo))
        
        try:
            pm.skinCluster(geo.name(), joints, omi=True, tsb=False)
        except:
            print ("{} already has a skinCluster on it...".format(geo.name()))
            pb.update_progbar()
            continue

        try:
            dest_skin = find_related_skinCluster(geo)
        except:
            print ("{} already has a skinCluster on it...".format(dest_skin))
            pb.update_progbar()
            continue
        pm.copySkinWeights(ss=sourceSkin, ds=dest_skin, noMirror=True, sm=True)
        pb.update_progbar()
        count += 1

    print ("Done.  Copied skins to {} target geos.".format(count))
    pb.end_progbar()

    return 


def find_related_skinCluster(node):
    '''
    find_related_skinCluster
    Finds a relative of the type "skinCluster".
    In a sensible rig there will only be one such a time, so there's no checking for more.

    usage:
    find_related_skinCluster([geo's shapeNode])
    '''

    print ("Checking {} connections...".format(node))

    skin_cluster = None
    for nodes in node.getShape().connections():
        if nodes.nodeType() == 'skinCluster':
            skin_cluster = nodes
            break

    return skin_cluster


def select_bound_joints(node=None):
    '''
    select_bound_joints
    Selected the joints that are bound by skinCluster to the selected geo.

    usage:
    select_bound_joints(node=[geo node]) # node defaults to using the selection if not specified.
    '''

    if(node == None):
        node = pm.ls(sl=True)[0]
        
    print ("Looking for joints influencing {}...".format(node))
    
    #joints = pm.listConnections((node.name() + ".matrix"), d=False, s=True)
    joints = pm.skinCluster(node, query=True, inf=True)
    print ("Selected joints influencing {}:\n{}".format(node, joints))

    pm.select(cl=True)
    pm.select(joints)

    return joints
