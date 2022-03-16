# skinning.py
# Matt Riche 2021
# sr_suite_utilities module for skinning related operations.

import pymel.core as pm
from . import progbar
from . import skeleton
import maya.mel as mel
from . import json_utils
from . import progbar as prg

def copy_skinweights(source="", target=""):
    '''
    copy_skinweights

    Copy the skin influences from a source (even between unlike pieces of geo) to any numbe  r of 
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
    progbar.start_progbar(
        max_value=len(target), message="Copying skins from {} to target(s)".format(source)
        )

    count = 0
    for geo in target:
        # Build a skinCluster node on the target
        #pm.skinCluster()
        print ("Copying skin influences to {}".format(geo))
        
        try:
            pm.skinCluster(geo.name(), joints, omi=False, tsb=True)
        except:
            print ("{} already has a skinCluster on it...".format(geo.name()))
            progbar.update_progbar()
            continue

        try:
            dest_skin = find_related_skinCluster(geo)
        except:
            print ("{} already has a skinCluster on it...".format(dest_skin))
            progbar.update_progbar()
            continue
        pm.copySkinWeights(ss=sourceSkin, ds=dest_skin, noMirror=True, sm=True)
        progbar.update_progbar()
        count += 1

    print ("Done.  Copied skins to {} target geos.".format(count))
    progbar.end_progbar()

    return 


def find_related_skinCluster(node = None):
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
    pm.select(node)
    node = pm.ls(selection = True)[0]
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


def get_info(source_mesh=None, target_mesh=None):
    '''
    rip_skin
    Copies skinning from one mesh to another, using duplicated joints instead of the same ones.
    Capable of pulling a skin from a referenced rig.

    usage:
    rip_skin(source_mesh=[PyNode], target_mesh=[PyNode])

    If source_mesh and target_mesh aren't specificed, function will resort to selection.
    '''


    # Get the skincluster and list of influences on the source mesh
    old_skinCluster = find_related_skinCluster(node=source_mesh)
    old_joints = select_bound_joints(node=source_mesh)

    # Get the skincluster and the list of influences on the new mesh
    new_skinCluster = find_related_skinCluster(node=target_mesh)
    new_joints = select_bound_joints(node=target_mesh)

    #get shape nodes
    old_shapeNode = pm.listRelatives(source_mesh, shapes = True)[0]
    new_shapeNode = pm.listRelatives(target_mesh, shapes = True)[0]
    
    #get vertices
    source_vertex = pm.ls(source_mesh+'.vtx[*]', fl=True)
    target_vertex = pm.ls(target_mesh+'.vtx[*]', fl=True)

    source_vtx = []
    target_vtx = []

    

    for k in source_vertex:
        source_vtx.append(str(k))
    
    for k in target_vertex:
        target_vtx.append(str(k))
    

    print ("source_vtx", source_vtx)

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
    source_data = {'skinCluster': old_skinCluster, 
                    'shapeNode': old_shapeNode,
                    'vertex': source_vtx,
                    'joints': old_joints}
    target_data = {'skinCluster': new_skinCluster, 
                    'shapeNode': new_shapeNode,
                    'vertex': target_vtx,
                    'joints': old_joints}
    return (source_data, target_data)


def get_skinCluster_info(vertices, skinCluster):

    if len(vertices) != 0 and skinCluster != "":
        verticeDict = {}
        
        for vtx in vertices:
            influenceVals = pm.skinPercent(skinCluster, vtx, 
                                             q=1, v=1, ib=0.001)
            
            influenceNames = pm.skinPercent(skinCluster, vtx, 
                                              transform=None, q=1, 
                                              ib=0.001) 
                        
            verticeDict[vtx] = list(zip(influenceNames, influenceVals))
        
        return verticeDict
    else:
        pm.error("No Vertices or SkinCluster passed.")
    

def serialise_skin(name = None, option = 0):
    """Save skinning data by vertex id and influence in a json
        params: name(str): default -> skinWeights.json
        Gets mesh by selection
    """

    #get mesh by selection
    mesh = pm.ls(sl=True)[0]

    #get mesh info
    info = get_info(mesh, mesh)
    data = info[0]

    #set mesh info into variables
    skin = data['skinCluster']
    shape = data['shapeNode']
    vtx = data['vertex']
    joints = data['joints']

    #get skin cluster
    skin_info = get_skinCluster_info(vtx, skin)

    #set file name   
    temp_file_name = name + "skinWeights.json" 

    #option 0 is for export, and saves data in json library
    if option == 0:   

        export_influences(mesh, vtx, skin, temp_file_name)
        
    #option 1 is for import, and retrieves data from json library
    else:     

        import_influences(mesh, skin, temp_file_name)
    
    return
    

def rip_skin(source_mesh = None, target_mesh = None, match_option = 0, influence = 0):
    """select source mesh, target mesh and run this to copy skin
        params:
            source mesh (str): either by selection or input
            target mesh (str): either by selection or input
            match option (int): 0 -> closest point, 1 -> UVs
            influence(int): 0 -> closest joint, 1 -> name
    """
    
    if(source_mesh == None):
        #checks if source mesh exists and selects 

        source_mesh = pm.ls(sl=True)[0]
        target_mesh = pm.ls(sl=True)[1]

    pm.select(source_mesh, target_mesh)


    if influence == 0:
        if match_option == 0:
            #if the options selected are closest points and closest joint
            pm.copySkinWeights(surfaceAssociation = "closestPoint", 
                                influenceAssociation = "closestJoint", noMirror = True)
        else:
            #if the options selected are uv and closest joint
            pm.copySkinWeights(surfaceAssociation = "closestPoint", uvSpace = ['map1', 'map1'], 
                                influenceAssociation = "closestJoint", noMirror = True)
    else:
        joints = select_bound_joints(node = source_mesh)
        pm.select(joints)
        strip = pm.selected()[0].namespace()
        for jnt in joints:
            #stripping namespace
            name = jnt.replace(strip, "")
            pm.rename(jnt, name)
        if match_option == 0:
            #if the options selected are closest points and namespace
            pm.copySkinWeights(surfaceAssociation = "closestPoint", 
                                influenceAssociation = "name", noMirror = True)
        else:
            #if the options selected are uv and namespace
            pm.copySkinWeights(surfaceAssociation = "closestPoint", uvSpace = ['map1', 'map1'], 
                                influenceAssociation = "name", noMirror = True)
        
        for jnt in joints:
            name = jnt
            if "|" in jnt:
                #adding namespace back
                name = jnt.split("|")[-1]
            pm.rename(jnt, strip + name)
    
    return

def export_influences(geo, vtx, skinCluster, name):
    """
    condenses given data into dictionary and stores in json file
    params:
        geo(str)
        vtx(list)
        skinCluster(str)
        name(str)
    """
    path = pm.fileDialog2(caption="Select folder to save json", dialogStyle=1, fileMode=3)

    #dictionary storing all vertex and influence data   
    verticeDict = get_skinCluster_info(vertices=vtx,
                                            skinCluster=skinCluster)

    prg.start_progbar(max_value = len(verticeDict), message="Getting vertex data")

        
    
    #strip joint namespace
    for influence in verticeDict:
        defaults = ['UI', 'shared']
        namespaces = (ns for ns in pm.namespaceInfo(lon=True) if ns not in defaults)
        namespaces = (pm.Namespace(ns) for ns in namespaces)
        for ns in namespaces:
            ns.remove() 


    #check if influences exist and store in json file
    if len(verticeDict) >= 1:
        json_utils.write_json(contents=verticeDict, directory = path, name=name)
        prg.update_progbar()

        print ("{0} vertices info was written to JSON file".format(len(verticeDict)))
        return name

    else:
        pm.error("No vertices selected to write to JSON")

    prg.end_progbar()
    
    return path

def import_influences(geo = None, skinCluster = None, name = None):
    """
    accesses and parses data from json file

    params:
        geo(str)
        skinCluster(str)
        name(str)
    """

    print ("Accessing {0}".format(name))

    path = pm.fileDialog2(caption="Select folder with json", dialogStyle=1, fileMode=3)
    
    vertData = json_utils.read_json(name = name, directory = path)   
    print (vertData)
    prg.start_progbar(max_value = len(vertData), message="Importing Influence Data")
    
    if len(vertData) > 0:
        
        #for each vertex, set influence using skinpercent
        for key in vertData.keys():
            
            #change vertex to target name
            keys = key.split("Shape")
            new_name = geo + "Shape" + keys[1]

            try:
                #get joint from joint heirarchy    
                jnt = vertData[key][0][0]
                if "|" in jnt:
                    jnt = vertData[key][0][0].split("|")[-1]
                    vertData[key][0][0] = jnt
                    prg.update_progbar()

                #print ("skin cluster {0}".format(skinCluster))
                #print ("key {0}".format(new_name))
                #print ("value {0}".format(vertData[key][0]))
                
                #changing skin influence
                pm.skinPercent(skinCluster, new_name, tv=vertData[key][0], zri=1)

                prg.update_progbar()

            except:
                pm.error("Something went wrong with the skinning")
        print ("{0} vertices were set to specificed values.".format(len(vertData.keys())))
        
    else:
        pm.error("JSON File was empty")
    
    prg.end_progbar()

    return
