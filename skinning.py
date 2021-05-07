# skinning.py
# Matt Riche 2021
# sr_suite_utilities module for skinning related operations.

import pymel.core as pm

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

        source = selection[0]
        del selection[0]
        target = selection

    print ("Copying skin cluster influences from {} onto {}".format(source, target))

    # Start a progress bar


    return 
