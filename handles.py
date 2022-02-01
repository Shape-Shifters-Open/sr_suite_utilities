# handles.py
# Matt Riche 2021
# Shaper Rigs suite utilities relating to the setup of handles and controls.

import pymel.core as pm
from . import dict_lib as dl

offset_string = "_Offset"

class CounterTransHandle:
	'''
	A build idiom that contains a handle that has an inverse relationship with
	a transnode it's parented.  As such, the handle has changing channels, but
	stays evidently frozen in space.  Helps to create illusionary relationship
	that make controller handles easier to understand.
	'''

	def __init__(self, group_name='new_counterTrans_handle', 
		position=(0,0,0), target=None):

		# We make the controller, trans group, and parent them in structure
		self.control_curve = create_control()
		self.trans_group = pm.createNode('transform')
		pm.parent(self.control_curve, self.trans_group)

		# Make MultiplyDivide node.
		self.mult_div = pm.createNode('multiplyDivide')
		self.mult_div.input2X.set(-1)
		self.mult_div.input2Y.set(-1)
		self.mult_div.input2Z.set(-1)

		# Connect the circular (but not cyclic!) relationship
		self.mult_div.output >> self.trans_group.translate
		self.control_curve.translate >> self.mult_div.input1


def create_offset(suffix=offset_string):
    '''
    Creates an offset group above the selection.
    
    Return value: List of new offset nodes (PyNodes)

    Usage:
    create_offset(suffix=[string]) # With selection

    suffix - string that defaults to a constant, usually "_Offset"
    '''

    selection = pm.ls(sl=True)

    offsets_list = []

    for node in selection:
        # Create empty xform node.
        group = pm.group(empty=True, n=(node.name() + suffix))
        offsets_list.append(group)
        # Move group node to same world-space xform as the selection
        pm.matchTransform(group, node)

        # Arrange desired hierarachy (Node beneath new transform, new transform beneath old parent.)
        parent = pm.listRelatives(node, parent=True)
        pm.parent(node, group, a=True)
        if(parent != []):
            pm.parent(group, parent[0], a=True)

    return offsets_list


# Functions for creating controllers
def create_control (target_position=None, shape='ring', rot=[0, 0, 0], 
	name='Unnamed_Ctrl', colour='yellow', size=1):
	print ("Making a handle by the name of {}.").format(name)

	unmade = True
	# Hijack this process for simple primitives:
	if(shape=='circle'):
		unmade = False
		new_handle = pm.circle( nr=(0, 1, 0), c=(0, 0, 0), r=15 )
		new_control = new_handle[0]

	if(unmade):
		# We can make curves based upon what we've stores in a dict.
		new_handle = pm.curve(
			per=dl.controlsDict[shape]['per'],
			p=dl.controlsDict[shape]['points'],
			k=dl.controlsDict[shape]['knots'],
			d=dl.controlsDict[shape]['degree']
			)
		new_control = new_handle
	
	change_colour(new_control, colour=colour)

	pm.setAttr(new_control.scaleX, size)
	pm.setAttr(new_control.scaleY, size)
	pm.setAttr(new_control.scaleZ, size)

	new_control.rename(name)

	# TODO
	# Snap it to a target node...
	# Apply it's rotational offset.

	return new_control


def learn_curve ( target_curve, do_print=True ):
	# Collect data from a curve.
    # This may never get called internally.
    # If target_curve is not a pyNode, not sure what could happen.

	# Record the points from a curve.
	points = []
	for cv in target_curve.cv:
		x = pm.getAttr(cv)[0]
		y = pm.getAttr(cv)[1]
		z = pm.getAttr(cv)[2]
		points.append((x, y, z))
        
	# Can't pull knots from the curve node itself, gotta hook one of these up;
	curve_inf = pm.createNode('curveInfo')
	pm.connectAttr(target_curve.getShape().worldSpace, curve_inf.inputCurve)
	
	knots = pm.getAttr(curve_inf.knots)
    
	degree = target_curve.degree()

	curve_dict = {}
	curve_dict['points'] = points
	curve_dict['knots'] = knots
	curve_dict['degree'] = degree

	# TODO this may not be evaluating correctly.  Need to dig into the enum value.
	if(target_curve.form == 'periodic'):
		curve_dict['periodic'] = True
	else:
		curve_dict['periodic'] = False
    
	if(do_print):
		print ("The dict is as follows...")
		print (curve_dict)

	# Delete the temporary node we used.
	pm.delete(curve_inf)
    
	return curve_dict


def change_colour(node, colour='red', shape=True ):

	print ("changing colour override.")
	node.overrideEnabled.set(True)
	node.overrideColor.set(dl.colourDict[colour])
	if(shape):
		node.getShape().overrideEnabled.set(True)
		node.getShape().overrideColor.set(dl.colourDict[colour])
	print ("Changed the colour override of {} to {}.").format(node, colour)
