'''
constraints.py

Module for constraint related automation
'''

import pymel.core as pm

cons_types = ['pointConstraint', 'parentConstraint', 'aimConstraint', 'scaleConstraint']

class StoredConstraint:
    '''
    Instance contrain all the data for remaking a constraint.
    '''

    def __init__(self, node, delete=False):
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

        self.ctx = self.cty = self.ctz = None
        self.crx = self.cry = self.crz = None
 
        for connex in input_list:
            if(connex[0].attrName() == 'ctx'):
                self.ctx = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'cty'):
                self.cty = (connex[1].node(), connex[1].attrName()) 
            elif(connex[0].attrName() == 'ctz'):
                self.ctz = (connex[1].node(), connex[1].attrName())

            elif(connex[0].attrName() == 'crx'):
                self.crx = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'cry'):
                self.cry = (connex[1].node(), connex[1].attrName())
            elif(connex[0].attrName() == 'crz'):
                self.crz = (connex[1].node(), connex[1].attrName())





