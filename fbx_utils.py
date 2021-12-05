import maya.cmds as cmds
import maya.mel as mel
from pprint import pprint
import os
import sys

def import_skeleton(file_path):
	"""
	imports FBX skel 
	returns: 
		- joints, transform data (list of dicts)
		- duplicate nodes (list)
	"""

	fbx_exts = ['.fbx', '.FBX']
	#validates given file path
	try:
		base_file = os.path.basename(file_path)
		ext = os.path.splitext(base_file)[1]
	except:
		cmds.error("import_skeleton() failed: file_path given is not valid")
		return
	#Checks file type of given file
	if not ext in fbx_exts:
		cmds.error("import_skeleton() failed: file given is not an FBX")
		return

	skel_nodes = cmds.file(file_path, i=True, returnNewNodes=True, ns='match_import')

	if skel_nodes:
		skel_node_data = []
		duplicate_names = []
		for node in skel_nodes:
			try:
				node_data, dups = get_joint_data(node)
				if node_data:
					skel_node_data.append(node_data)
				if dups:
					duplicate_names.append(dups)

				print(node_data)
			except:
				continue

		cmds.delete(skel_nodes)

		return skel_node_data, duplicate_names
	else:
		cmds.error(
			"import_skeleton() failed: Not working with a clean scene (or FBX file is empty)"
			)
		return


def get_joint_data(node):
	'''
	Get the serializable data of a node.

	:param node: Joint or transform name.
	:return: Data dictionary.
	'''
	
	ATTRIBUTES = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx,', 'sy', 'sz', 'jointOrient']

	node_type = cmds.nodeType(node)
	shapes = cmds.listRelatives(node, children=True, shapes=True)
	# Skip nodes that are not joints or transforms or if there are shapes below.
	if node_type not in ["joint", "transform"] or (shapes and node_type == "transform"):
		return None

	parent = cmds.listRelatives(node, parent=True)
	parent = parent[0] if parent else None
	children = cmds.listRelatives(node, children=True)
	
	#converts short names / full names, finds duplicate names
	duplicate_names = []
	if '|' in node:
		short_name = cmds.ls(node, sn=True)
		if len(short_name) > 1:
			duplicate_names.append(short_name[0])
		short_name = short_name[0]
		full_name = node
	else:
		short_name = node
		full_name = cmds.ls(node, l=True)
		if len(full_name) > 1:
			duplicate_names.append(short_name)
		full_name = full_name[0]

	joint_data = {
		"nodeType": node_type, 
		"name": short_name,
		"full_name" : full_name, 
		"parent": parent,
		"children": children
					}

	if node_type == 'joint':
		joint_data['rotate_order'] = cmds.joint(node, q=True, rotationOrder=True)
		
	for attr in ATTRIBUTES:
		attribute = "{}.{}".format(node, attr)
		if not cmds.objExists(attribute):
			continue
		value = cmds.getAttr(attribute)
		if isinstance(value, list):
			value = list(value[0])
		joint_data[attr] = value

	world_space_pos = cmds.xform(full_name, q=True, ws=True, t=True)
	joint_data['world_space_pos'] = world_space_pos
	
	return joint_data, duplicate_names