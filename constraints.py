'''
constraints.py

Module for constraint related automation
'''

import pymel.core as pm

cons_types = ['pointConstraint', 'parentConstraint', 'aimConstraint', 'scaleConstraint', 
    'orientConstraint']

class StoredConstraint:
    '''
    Instance contrain all the data for remaking a constraint.
    '''

    def __init__(self, node, delete=True):
        '''
        Specify a constraint node as 'node'
        '''

        if(node.type() not in cons_types):
            pm.error("Trying to store something that isn't a constraint.")
            return

        # type will be an integer determining that constraint type.  It has the same order as the 
        # cons_types list.  0=pointConstraint, 1=parentConstraint, 2=aimConstraint, 
        # 3=scaleConstraint
        self.type = cons_types.index(node.type())
        print("The type int is {}, which is {}".format(self.type, cons_types[self.type]))

        # The connected attributes must be found and stored.
        input_list = node.listConnections(p=True, d=True, s=False, c=True)

        # These input connections are for the channel box content. All set to none in the case 
        # Of constraint types that don't require them all.
        self.input_connections = [None, None, None, None, None, None, None, None, None]

        # Target transform will be discovered in this loop:
        self.target_trans = None
 
        for connex in input_list:
            print(connex)
            print(connex[0].attrName())
            if(connex[0].attrName() == 'ctx'):
                self.input_connections[0] = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'cty'):
                self.input_connections[1] = (connex[1].node(), connex[1].attrName()) 
            elif(connex[0].attrName() == 'ctz'):
                self.input_connections[2] = (connex[1].node(), connex[1].attrName())

            elif(connex[0].attrName() == 'crx'):
                self.input_connections[3] = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'cry'):
                self.input_connections[4] = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'crz'):
                self.input_connections[5] = (connex[1].node(), connex[1].attrName())

            elif(connex[0].attrName() == 'csx'):
                self.input_connections[6] = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'csy'):
                self.input_connections[7] = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'csz'):
                self.input_connections[8] = (connex[1].node(), connex[1].attrName())

            # We detect the target transform by seeing if any of the transform channels are 
            # connected.
            if(self.target_trans == None):
                if(connex[0].attrName() in ['ctx', 'cty', 'ctz', 'crx', 'cry', 'crz', 'csx', 'csy', 
                    'csz']):
                    self.target_trans = connex[1].node()

        # The connected attributes must be found and stored.
        output_list = node.listConnections(p=True, d=False, s=True, c=True)
        self.output_connections = []
        self.output_targets = []

        for out_connex in output_list:
            print(out_connex)
            print(out_connex[0].attrName())
            if(out_connex[0].attrName() == 'tw'):
                self.output_connections.append(out_connex[0])
            if(out_connex[0].attrName() in ['tr', 'tt', 'trp', 'trt']):
                if(out_connex[1].node() not in self.output_targets):
                    self.output_targets.append(out_connex[1].node())

        # Store the node name of the constraint node for rebuilding:
        self.name = node.name()

        if(delete):
            pm.delete(node)

        return

    
    def report(self):
        '''
        Reports all the stored content of the instance.
        Generally for debug purposes.
        '''

        for attribute in dir(self):
            if("__" in attribute or attribute in ['report', 'rebuild']):
                continue
            print("{}:".format(attribute))
            exec("print(self.{}\n)".format(attribute))
            print('\n')

        return


    def rebuild(self):
        '''
        Using the stored data, remake the constraint as it was.
        '''

        if(self.type == cons_types.index('pointConstraint')):
            print("Rebuilding a pointConstraint called {}".format(self.name))
            skip_string = ''
            # Determine the skip_axis
            if(self.input_connections[0] == None):
                skip_string.append('x')
            if(self.input_connections[1] == None):
                skip_string.append('y')
            if(self.input_connections[2] == None):
                skip_string.append('z')
                
            print("skip string is {}".format(skip_string))
            # Remake a point constraint
            if(skip_string != ''):
                pm.pointConstraint(
                    self.output_targets, self.target_trans, mo=True, sk=skip_string, n=self.name
                    )
            else:
                pm.pointConstraint(self.output_targets, self.target_trans, mo=True, n=self.name)

        elif(self.type == cons_types.index('parentConstraint')):
            print("Rebuilding a parentConstraint called {}".format(self.name))
            trans_skip_string = rot_skip_string = None

            # What happens next is somewhat ugly-- None as the channel skip argument will skip no
            # channels, but we have to compose a string of 'xyz' or just 'x' or any combo to get 
            # the right argument.  We can't execute the .append() unless we are working on a string
            # so we continually check if it == None over and over.  Can't see a way that is any more
            # elegant.  I suppose a definition inside a definition wouldn't be too crazy.

            # Build the skip translate argument string;
            if(self.input_connections[0] == None):
                if(trans_skip_string == None):
                    trans_skip_string = ''
                trans_skip_string += 'x'
            if(self.input_connections[1] == None):
                if(trans_skip_string == None):
                    trans_skip_string = ''
                trans_skip_string += 'y'
            if(self.input_connections[2] == None):
                if(trans_skip_string == None):
                    trans_skip_string = ''
                trans_skip_string += 'z'

            # Build the skip rotation argument string;
            if(self.input_connections[3] == None):
                if(rot_skip_string == None):
                    rot_skip_string = ''
                rot_skip_string += 'x'
            if(self.input_connections[4] == None):
                if(rot_skip_string == None):
                    rot_skip_string = ''
                rot_skip_string += 'y'
            if(self.input_connections[5] == None):
                if(rot_skip_string == None):
                    rot_skip_string = ''
                rot_skip_string += 'z'
            
            pm.parentConstraint(
                self.output_targets, self.target_trans, st=trans_skip_string, 
                sr=rot_skip_string, mo=True, n=self.name
                )

        elif(self.type == cons_types.index('orientConstraint')):
            print("Rebuilding an orientConstraint called {}".format(self.name))

            rot_skip_string = None

            # Build the skip rotation argument string;
            if(self.input_connections[3] == None):
                if(rot_skip_string == None):
                    rot_skip_string = ''
                rot_skip_string += 'x'
            if(self.input_connections[4] == None):
                if(rot_skip_string == None):
                    rot_skip_string = ''
                rot_skip_string += 'y'
            if(self.input_connections[5] == None):
                if(rot_skip_string == None):
                    rot_skip_string = ''
                rot_skip_string += 'z'

            pm.orientConstraint(
                self.output_targets, self.target_trans, sk=rot_skip_string, mo=True, n=self.name
                )

        elif(self.type == cons_types.index('scaleConstraint')):
            print("Rebuilding a scaleConstraint called {}".format(self.name))

            s_skip_string = None
            # Build the skip rotation argument string;
            if(self.input_connections[6] == None):
                if(s_skip_string == None):
                    s_skip_string = ''
                s_skip_string += 'x'
            if(self.input_connections[7] == None):
                if(s_skip_string == None):
                    s_skip_string = ''
                s_skip_string += 'y'
            if(self.input_connections[8] == None):
                if(s_skip_string == None):
                    s_skip_string = ''
                s_skip_string += 'z'

            pm.scaleConstraint(
                self.output_targets, self.target_trans, sk=s_skip_string, mo=True, n=self.name
                )

        return

        


