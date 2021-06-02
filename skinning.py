# skinning.py
# Matt Riche 2021
# sr_suite_utilities module for skinning related operations.

import pymel.core as pm
import progbar as pb
import skeleton as sk
import maya.mel as mel


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
    joints = select_bound_joints(source)

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
            pm.skinCluster(geo.name(), joints, omi=True, tsb=True)
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


def find_related_skinCluster(node=None):
    '''
    find_related_skinCluster
    Finds a relative of the type "skinCluster".
    In a sensible rig there will only be one such a time, so there's no checking for more.

    usage:
    find_related_skinCluster([geo's shapeNode])
    '''
    
    select_mode = False

    if(node == None):
        select_mode = True
        print ("Running the UI version of this command, return value will be selected.")
        node = pm.ls(sl=True)[0]

    print ("Checking {}'s connections...".format(node))
    skin_cluster = None
    for nodes in node.getShape().connections():
        if nodes.nodeType() == 'skinCluster':
            print ("Found {}.".format(nodes))
            skin_cluster = nodes
            break


    if(select_mode):
        pm.select(skin_cluster)

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


def harden():
    '''
    harden
    With a single component of a skinned mesh selected, copy the identical skinweights through out
    the entire "shell" until an edge it met.  (Good for scales or solid blocks.)
    
    usage:
    harden() # With single vert selected.
    '''
               
    selection_size = pm.ls( sl=True )
    last_selection_size = []
    
    # Copy skinweight into buffer.
    try:
        mel.eval("artAttrSkinWeightCopy;")
        # Note: This mel based command is fast and cheap, but ideally we'd use skinPercent to be non
        # mel dependant, but that would be slower for no reason.
    except:
        pm.warning("Couldn't copy skin-weight.  You probably don't have a vertex selected.")
        return
    
    print ("Getting selection...")
    # Grow selection select entire shell.
    while last_selection_size != selection_size:
        # Get current selection size.
        last_selection_size = selection_size
        mel.eval("GrowPolygonSelectionRegion;")
        # Once again, the mel command here is fast and cheap.  The actual Python may be worse.
        # Shamelessly going to remain mel dependant on this one.
        selection_size = pm.ls( sl=True )
            
    mel.eval("artAttrSkinWeightPaste;")
    print ("Weights spread to {} vertices.".format(len(selection_size)))

    return


def save_skin():
    '''
    save_skin
    Saves skin weights as a dict that's influences-per-vertex, which is then exported to .json.

    usage:
    save_skin() # With skinned geo selected.
    '''

    # Acquire selection
    mesh = pm.ls(sl=True)[0]

    joints = select_bound_joints(node=mesh)

    pm.error("NOT IMPLEMENTED!")

    for joint in joints:
        # Get the skinPercent per vert, per joint.
        pass


def rip_skin(source_mesh=None, target_mesh=None):
    '''
    rip_skin
    Copies skinning from one mesh to another, using duplicated joints instead of the same ones.
    Capable of pulling a skin from a referenced rig.

    usage:
    rip_skin(source_mesh=[PyNode], target_mesh=[PyNode])

    If source_mesh and target_mesh aren't specificed, function will resort to selection.
    '''

    if(source_mesh == None):

        source_mesh = pm.ls(sl=True)[0]
        target_mesh = pm.ls(sl=True)[1]

    # Get the skincluster and list of influences on the source mesh
    old_skinCluster = find_related_skinCluster(node=source_mesh)
    old_joints = select_bound_joints(node=source_mesh)

    # Get the skincluster and the list of influences on the new mesh
    new_skinCluster = find_related_skinCluster(node=target_mesh)
    new_joints = select_bound_joints(node=target_mesh)

    # Make a list of just the joint names for comparision
    old_names=[]
    for joint in old_joints:
        old_names.append(joint.name())
    missing_infs = old_joints

    # Now make warnings about what is or isn't matching in the lists.
    for joint in new_joints:
        if(joint.name() in old_names):
            missing_infs.remove(joint.name())
            
    # Now new_joint and old_joints should have contents with the same names... let's check how much
    # they do or do not match.
