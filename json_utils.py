import pymel.core as pm

import json 

def write_json(contents, directory, name):
    """
    gets dict info and write json file
        params: contents (dict)
                name (str): file name
        returns file name
    """
    if ".json" not in name:
        name += ".json"
    
    path = directory[0] + "/" + name

    #print (">all contents are: {0}".format(contents))

    with open(path, "w") as jsonFile:
        json.dump(contents, jsonFile, indent=1)

    print ("Data was successfully written to {0}".format(path))

    return path


def read_json(directory):
    """retrieves data from given json file name
        params: 
                name(str)
    """

    path = directory
    try:
      with open(path, 'r') as jsonFile:
          return json.load(jsonFile)
    except:
        pm.error("Could not read {0}".format(name))


