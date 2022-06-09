# deform.py
# Created: Monday, 14th February 2022 8:32:59 am
# Matthew Riche
# Last Modified: Monday, 14th February 2022 8:33:05 am
# Modified By: Matthew Riche

'''
Operations related to deformations
'''

from . import component as cmp
from . import progbar as prg
from . import skinning

import pymel.core as pm
import maya.cmds as cmds
import sys


def deltas_to_tweak(new_geo, old_geo, tweak):
    '''
    Applies a list of vertex deltas, generated by component.list_vertex_deltas() to the inside
    of a tweak node.
    '''

    
    deltas = cmp.list_vertex_deltas(new_geo, old_geo)

    prg.start_progbar(max_value=len(deltas), message="Baking Deltas to Tweak node...")

    for i in range(0, len(deltas)):
        tweak_vert = tweak.plist[0].controlPoints[i]
        tweak_vert.xValue.set(deltas[i][0])
        tweak_vert.yValue.set(deltas[i][1])
        tweak_vert.zValue.set(deltas[i][2])
        prg.update_progbar()

    prg.end_progbar()

    print("Vertex deltas from {} are now baked to {}.".format(new_geo.name(), tweak))

    return


def save_skins_unbind():
    """
    step one in baking deltas 
    saves skin cluster in a duplicate node and unbinds skin. 
    runs based on selection
    """  
    #takes selection
    old_geo = pm.ls(selection = True)

    #duplicates selection, saves skincluster and ubinds original skin
    dup_geo = []
    dup_grp = pm.group(em = True)
    ex_joint = pm.joint(n = "temp_jnt", p = (0, 0, 0))
    for i in old_geo:
        dup = pm.duplicate(i, n = "dupe" + i)
        hist = pm.listHistory(i, pdo=True)
        skins = pm.ls(hist, type="skinCluster")[0]
        jts = skinning.select_bound_joints(node = skins)
        pm.select(jts)
        joints = pm.ls(selection = True)
        pm.skinCluster(joints, dup)
        skinning.rip_skin(source_mesh = i, target_mesh = dup, match_option = 0, influence = 0)
        pm.parent(dup, dup_grp)
        pm.skinCluster(i, ub = True, e = True)
        pm.skinCluster(ex_joint, i)
        
    return


def bake_deltas(source_mesh = None, target_mesh = None):
    """
    bakes deltas based on selection
    select target mesh first, and then source mesh
    """
    meshes = pm.ls(selection = True)  
    target_mesh = meshes[0]
    source_mesh = meshes[1]
    
    #nodes = pm.listHistory(target_mesh, pruneDagObjects = True, interestLevel = 1)
    #tweak_node = None
    
    pm.select(target_mesh, r = True)
    pm.select(source_mesh  , add = True)

    try:
        batch_run()
        print("running batch run")
    except:
        pm.warning("unable to batch run bake deltas script")
        pass
    
    # try:
    #     pm.lockNode(source_mesh, l=False, lockUnpublished=False)
    # except:
    #     pass 
    #adds transform node 

    try:
        pm.polyMoveVertex(source_mesh, constructionHistory = 1, random = 0)
    except:
        pm.warning("unable to add transform node, please check if locked")
        pass

    pm.select(source_mesh)

    #bake transform node
    try:
        pm.bakePartialHistory(ppt = True)
    except:
        pm.warning("unable to bake partial history")
        pass


def getVtxPos(shapeNode, original) :
    print("getting vtx pos")
    vtxWorldPosition = []    # will contain positions un space of all object vertex
    print("11")
    vtxIndexList = cmds.getAttr(shapeNode + ".vrts", multiIndices=True )
    print(vtxIndexList)
    print("1")
    for i in vtxIndexList :
        print("2")
        curPointPosition = cmds.xform( str(shapeNode)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True )  
        print("3")
        curPointPositionOri = cmds.xform( str(original)+".pnts["+str(i)+"]", query=True, translation=True, worldSpace=True )     # [1.1269192869360154, 4.5408735275268555, 1.3387055339628269]
        print("4")
        ptdelt =[curPointPosition[0]-curPointPositionOri[0],curPointPosition[1]-curPointPositionOri[1],curPointPosition[2]-curPointPositionOri[2]]
        #if ptdelt[0]!= 0 or ptdelt[1]!= 0 or ptdelt[0]!= 1:
            #print "delta found on: ", original,".pnts[",str(i),"]", " delta value: ", ptdelt
        print("5")
        vtxWorldPosition.append(ptdelt)
    return vtxWorldPosition


def applyDeltaToTweak (shapeNode , original):
    pt = getVtxPos(shapeNode, original)
    print("bake all deformer delta for: ", original)
    history = cmds.listHistory(original,pdo=True)
    tweakNode = cmds.ls(history, type = "tweak")[0]
    index =0
    for each in pt:
        #print each
        item = tweakNode+".plist[0].controlPoints["+str(index)+"]"
        #print item
        cmds.setAttr(item+".xValue", each[0])
        cmds.setAttr(item+".yValue", each[1])
        cmds.setAttr(item+".zValue", each[2])
        index+=1


def batch_run():
    print("batch run function running")
    """delt_pairs_list= [["tgt_head_lod0_meshShape", "head_lod0_meshShape"],
                ["tgt_teeth_lod0_meshShape", "teeth_lod0_meshShape"],
                ["tgt_saliva_lod0_meshShape", "saliva_lod0_meshShape"],
                ["tgt_eyeLeft_lod0_meshShape", "eyeLeft_lod0_meshShape"],
                ["tgt_eyeRight_lod0_meshShape", "eyeRight_lod0_meshShape"],
                ["tgt_eyeshell_lod0_meshShape", "eyeshell_lod0_meshShape"],
                ["tgt_eyelashes_lod0_meshShape", "eyelashes_lod0_meshShape"],
                ["tgt_eyeEdge_lod0_mesh", "eyeEdge_lod0_mesh"],
                ["tgt_cartilage_lod0_meshShape", "cartilage_lod0_meshShape"],
                ["tgt_f_tal_nrw_body_lod0_meshShape", "f_tal_nrw_body_lod0_meshShape"]            
                ]"""
    print ("step 1")
    #test case, to be commented and left for further testing and edits 
    delt_pairs_list = [["pCubeShape2", "pCubeShape1"]]
    print ("step 2")
    for pairs in delt_pairs_list:
        print (pairs)
        print("applying delta to tweak")
        applyDeltaToTweak (pairs[0], pairs[1])
    pass


def clean_targets(orig = None):
    """
    checks for duplicates with skin cluster, reapplies skin cluster 
    and removes extra nodes
    can provide an original node if required
    """

    #finds duplicates based on prefix
    target_dupes = pm.ls("dupe*")
    par = pm.listRelatives(target_dupes[0], parent = True)[0]

    for i in target_dupes:
        #finds original
        orig = i.split("dupe")[1]
        if "Orig" in orig:
            orig = orig.split("Orig")[0]
        print ("original is ", orig)
        pm.skinCluster(orig, ub = True, e = True)
        #gets skincluster
        hist = pm.listHistory(i, pdo=True)
        skins = pm.ls(hist, type="skinCluster")
        #rebinds skin
        if skins:
            skins_cluster = skins[0]
        
        jts = skinning.select_bound_joints(node = skins_cluster)
        pm.select(jts)
        joints = pm.ls(selection = True)
        try:
            pm.select(orig, add = True)
        except:
            pm.warning("unable to find original mesh, please select it")
            pass

        try:
            pm.skinCluster()
        except:
            pm.warning("unable to bind skin")
            pass   

        try:
            skinning.rip_skin(source_mesh = i, target_mesh = orig, match_option = 0, influence = 0)
        except:
            pm.warning("rip skin not working")
            pass
            
        
    pm.delete(par)





