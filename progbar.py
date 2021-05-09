# progbar.py
# Matt Riche 2021
# sr_suite_utilities module for instantiating progress bars.

import pymel.core as pm
import maya.mel

def start_progbar(max_value, message="Please Wait."):
    '''
    start_progbar

    Starts a breakable "main progress bar" in a Maya scene.  This allows for the breaking of loops
    by a user with ESC as well.

    usage - start_progbar([int], message=[string])
    first int is the maximum size of the progbar.
    message - the displayed status message next to the progress bar.
    '''

    globals()['gMainProgressBar'] = maya.mel.eval('$tmp = $gMainProgressBar')
    pm.progressBar( globals()['gMainProgressBar'],
                    edit=True,
                    beginProgress=True,
                    isInterruptable=True,
                    status=message,
                    maxValue=max_value,
                    minValue=0
                    )

    return


def update_progbar(step_size=1):
    '''
    update_progbar

    Updates the progress bar easily.
    Won't work unless 'gMainProgressBar' is registered in globals().

    usage - update_progbar(step_size=int)
    step_size - how many units the progbar will step by.
    '''
    
    pm.progressBar(globals()['gMainProgressBar'], edit=True, step=step_size)

    return


def end_progbar():
    '''
    end_progbar

    Ends the progress bar easily.
    There must be 'gMainProgressBar' registered in globals().

    usage - end_progbar()
    '''

    pm.progressBar(globals()['gMainProgressBar'], edit=True, endProgress=True)
    
    return