import pymel.core as pm
import skinning as sn

import json 


def write_json(contents, name):
    """
    gets dict info and write json file
        params: contents (dict)
                name (str): file name
        returns file name
    """
    if ".json" not in name:
        name += ".json"

    #print (">all contents are: {0}".format(contents))

    with open(name, "w") as jsonFile:
        json.dump(contents, jsonFile, indent=1)

    print ("Data was successfully written to {0}".format(name))

    return name


def read_json(name):
    """retrieves data from given json file name
        params: 
                name(str)
    """
    try:
      with open(name, 'r') as jsonFile:
          return json.load(jsonFile)
    except:
        pm.error("Could not read {0}".format(name))


def export_influences(geo, vtx, skinCluster, name):
    """
    condenses given data into dictionary and stores in json file
    params:
        geo(str)
        vtx(list)
        skinCluster(str)
        name(str)
    """

    #dictionary storing all vertex and influence data
    verticeDict = sn.get_skinCluster_info(vertices=vtx,
                                            skinCluster=skinCluster)
    
    #strip joint namespace
    for influence in verticeDict:
        defaults = ['UI', 'shared']
        namespaces = (ns for ns in pm.namespaceInfo(lon=True) if ns not in defaults)
        namespaces = (pm.Namespace(ns) for ns in namespaces)
        for ns in namespaces:
            ns.remove() 

    #check if influences exist and store in json file
    if len(verticeDict) >= 1:
        write_json(contents=verticeDict,
                                name=name)

        print ("{0} vertices info was written to JSON file".format(len(verticeDict)))
        return name

    else:
        pm.error("No vertices selected to write to JSON")

    return

def import_influences(geo = None, skinCluster = None, name = None):
    """
    accesses and parses data from json file

    params:
        geo(str)
        skinCluster(str)
        name(str)
    """

    print ("Accessing {0}".format(name))
    
    
    vertData = read_json(name = name)   
    print (vertData)
    
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

                #print ("skin cluster {0}".format(skinCluster))
                #print ("key {0}".format(new_name))
                #print ("value {0}".format(vertData[key][0]))
                
                #changing skin influence
                pm.skinPercent(skinCluster, new_name, tv=vertData[key][0], zri=1)

            except:
                pm.error("Something went wrong with the skinning")
        print ("{0} vertices were set to specificed values.".format(len(vertData.keys())))
        
    else:
        pm.error("JSON File was empty")
