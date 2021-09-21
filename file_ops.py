'''
file_ops.py

Module for loading and saving of rigging-relvent data-sets.

Matt Riche, 2021
'''


import json
import pymel.core as pm

def json_out(data, filepath):
    '''
    Generic "dictionary to JSON" serialize.

    Usage:
    json_out(data, filepath)

    data - (dict) Data to serialize.
    filepath - (string) file path on drive locally.
    '''

    try:
        with open(filepath, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)
            print("Wrote {}".format(filepath))
    except:
        print("File related error writng {}.\n  Check that path has write permissions or drive is "
            "not full.".format(filepath))
        return False

    return True


def json_in(filepath):
    '''
    Given a filepath,
    Load JSON data from drive.

    Usage:
    data = json_in(filepath)

    filepath - (string) file path on drive locally where .JSON data exists.
    '''

    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except:
        print("File related error reading {}.\nCheck that the file exists.".format(filepath))
        return False

    return data


def prompt_for_filepath(fm, ext='*.json', caption='Specify filepath'):
    '''
    Acquire a filepath by prompting the user with Maya's regular filepath dialog.

    Usage:
    prompt_for_filepath()
    fm - (int) 0 for save, 1 for load.
    ext - (string) if beginning with a wildcard, like '*.json', will search only for that type.
    caption - (string) What the file dialog will tell the user it's doing.
    '''
    
    filepath = pm.fileDialog2(
        ff=ext,
        fm=0, 
        dialogStyle=2,
        cap=caption,
        )[0]

    return filepath