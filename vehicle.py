import sys
import os
import maya.utils
import maya.utils
import pymel.core as pm


def vetala_importer():
    """imports vetala suite"""
    file_path = os.path.realpath(__file__)
    splitter = file_path.split("\\vehicle.py")[0]
    vet_path = splitter + "\\Vetala"
    vet_path.replace("\\\\", "\\")

    os.sys.path.append(vet_path)
    os.chdir(vet_path)

    def run_tools_ui(directory = None):
        from vtool.maya_lib import ui
        ui.tool_manager(directory = directory)
    maya.utils.executeDeferred(run_tools_ui)


def vetala_controls():
    """imports custom control maker for vehicles"""

    file_path = os.path.realpath(__file__)
    splitter = file_path.split("\\vehicle.py")[0]
    vet_path = splitter + "\\Vetala"
    vet_path.replace("\\\\", "\\")

    os.sys.path.append(vet_path)
    os.chdir(vet_path)

    from vtool.maya_lib import rigs
    from vtool.maya_lib import rigs_util
    from vtool.maya_lib import space
    ##Made by: NathanSegre :) ##
    #True/False values
    subControl = False
    autoName = 1
    fkChainValue = 0
    localValue = 0
    #################################################################
    ###Chain control creation
    # VETALA FK RIG
    def fkChain():
        rig = rigs.FkRig(controlName, sideAttrValue)
        rig.set_joints(selObj)
        #rig.set_use_joint_controls(False)
        #cube,ball,square...
        rig.set_control_shape(curveAttrValue)
        rig.set_control_color(ciAttr)
        #add var to false
        rig.set_create_sub_controls(subControl)
        rig.set_control_size(sizeAttrValue)
        rig.delete_setup()
        rig.create()
    #fkChain()
    ###Chain control creation
    # VETALA FK LOCAL RIG
    def fkLocalChain():
        rig = rigs.FkLocalRig(controlName, sideAttrValue)
        rig.set_joints(selObj)
        #rig.set_use_joint_controls(False)
        #cube,ball,square...
        rig.set_control_shape(curveAttrValue)
        rig.set_control_color(ciAttr)
        #add var to false
        rig.set_create_sub_controls(subControl)
        rig.set_control_size(sizeAttrValue)
        rig.create()
    #----------------------------------------------------------------
    ###NON chain control creation
    # VETALA FK RIG
    def fkControl():
        if autoName == 1:
            for jnt in selObj:    
                rig = rigs.FkRig(jnt, sideAttrValue)
                rig.set_joints(jnt)
                rig.set_control_shape(curveAttrValue)
                rig.set_control_color(ciAttr)
                #add var to false
                rig.set_create_sub_controls(subControl)
                rig.set_control_size(sizeAttrValue)
                rig.delete_setup()
                rig.create() 
        if autoName == 0:      
            for jnt in selObj:    
                rig = rigs.FkRig(controlName, sideAttrValue)
                rig.set_joints(jnt)
                rig.set_control_shape(curveAttrValue)
                rig.set_control_color(ciAttr)
                #add var to false
                rig.set_create_sub_controls(subControl)
                rig.set_control_size(sizeAttrValue)
                rig.delete_setup()
                rig.create()
    ###Non chain control creation
    # VETALA FK LOCAL RIG
    def fkLocalControl():
        if autoName == 1:
            for jnt in selObj:    
                rig = rigs.FkLocalRig(jnt, sideAttrValue)
                rig.set_joints(jnt)
                rig.set_control_shape(curveAttrValue)
                rig.set_control_color(ciAttr)
                #add var to false
                rig.set_create_sub_controls(subControl)
                rig.set_control_size(sizeAttrValue)
                #rig.delete_setup()
                rig.create()
        if autoName == 0:    
            for jnt in selObj:    
                rig = rigs.FkLocalRig(controlName, sideAttrValue)
                rig.set_joints(jnt)
                rig.set_control_shape(curveAttrValue)
                rig.set_control_color(ciAttr)
                #add var to false
                rig.set_create_sub_controls(subControl)
                rig.set_control_size(sizeAttrValue)
                #rig.delete_setup()
                rig.create()        
    ###################################################################
    def pickColourI():
        global ciAttr   
        ciQ = pm.colorIndexSliderGrp('test2', q=True, value=True)
        print (ciQ)
        ciAttr = ciQ - 1  
        print (ciAttr)
    def controlValues():
        global ciQ
        global ciAttr
        ciQ = pm.colorIndexSliderGrp('test2', q=True, value=True)
        ciAttr = ciQ - 1
        global curveAttrValue
        curveAttrValue = pm.optionMenu('curveAttr', q = True, v = True)
        global sideAttrValue
        sideAttrValue = pm.optionMenu('sideAttr', q = True, v = True)
        global sizeAttrValue
        sizeAttrValue = pm.intField( sizeAttr, q = True, value = True)  
        global controlName
        if autoName==1:
            controlName = selObj[0]      
        if autoName==0:
            controlName = pm.textField('customNameField', q = True, text = True)
    def defaultButtonPush(*args):
        def fkDef():
            if localValue == 0:
                fkControl()
            if localValue == 1:
                fkLocalControl()
        def fkChainDef():
            if localValue == 0:
                fkChain()
            if localValue == 1:
                fkLocalChain()            
        global selObj 
        selObj = pm.ls(sl=True)
        controlValues()
        print (controlName)
        print (autoName)
        print (sizeAttrValue)
        print (subControl)
        print (sideAttrValue)
        print (fkChainValue)
        print (curveAttrValue)
        print (ciQ)
        if fkChainValue == 0:
            fkDef()
        if fkChainValue == 1:
            fkChainDef()
    ######     UI       ######################################################################
    def sbcmUI(*args):
        global fieldStatus
        def fieldStatus(*args):
            if autoName==1:
                pm.textField('customNameField', edit=True, enable = False) 
                print ('ran')
            if autoName==0:
                pm.textField('customNameField', edit=True, enable = True)
                print ('ran2')
        '''
        global autoCheck
        def autoCheck(*args):
            #if fkChainValue == 0:
            #    print ok
            if fkChainValue == 1:
                pm.checkBox('AutoNameBox',edit=True, v=False, offCommand='autoName = 0')
                pm.textField('customNameField', edit=True, enable = True)
                autoName = 0
                #fieldStatus()
                print autoName
            if fkChainValue == 0:
                pm.checkBox('AutoNameBox',edit=True, v=True, onCommand='autoName = 1')
                pm.textField('customNameField', edit=True, enable = False)
                autoName = 1
                print autoName                
            fieldStatus()  
        '''          
        windowID = 'SnowballControl'
        if pm.window(windowID, exists=True):
            pm.deleteUI(windowID)
        gui = pm.window(windowID, title='Vetala Control Maker', sizeable=False, rtf=True, w=400, h=100)
        #gui = pm.window('WhTF', title='test', wh=(300,300))
        pm.rowColumnLayout(numberOfColumns= 4, columnWidth = [(1,100),(2,40),(3,75),(4,161)], columnOffset=[ (1,'right', 3),(4,'left', 3)])
        pm.text(label ='NAME:', align = 'right', w=40, h=30 )
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        #Auto Name
        pm.text(label = 'Auto', align = 'right') 
        nameBox = pm.checkBox('AutoNameBox',label='', v=True, align='right', offCommand='autoName = 0', onCommand='autoName = 1', changeCommand = 'fieldStatus()')
        #Custom Name
        pm.text(label = 'Custom', align = 'right', w =40)
        pm.textField('customNameField', enable = False, w = 159)
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        #Attributes title
        pm.text(label = 'ATTRIBUTES:', align = 'right')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        #Size
        pm.text(label = 'Size:', align = 'right')
        global sizeAttr
        sizeAttr = pm.intField( value = 3 )
        #FK local
        pm.text(label = 'Local', align = 'right')
        localBox = pm.checkBox(label = '', v = False, align = 'right', ofc = 'localValue = 0', onc = 'localValue = 1')
        #sub
        pm.text(label = 'Sub', align = 'right')
        subBox = pm.checkBox(label = '', v = False, align = 'left', offCommand = 'subControl = False', onCommand = 'subControl = True')
        #FK Chain
        pm.text(label = 'FK Chain', align = 'right')
        chainBox = pm.checkBox(label = '*Recommend custom name', v = False, align = 'right', ofc = 'fkChainValue = 0', onc = 'fkChainValue = 1')
        #Side
        pm.text(label = 'Side:', align = 'right')
        pm.optionMenu('sideAttr')
        pm.menuItem(label = '')
        pm.menuItem(label = 'C')
        pm.menuItem(label = 'R')
        pm.menuItem(label = 'L')
        #style
        #pm.separator(h=10,style='none')
        #pm.separator(h=10,style='none')
        pm.text(label = 'Style', align = 'right')
        pm.optionMenu('curveAttr', w=159)
        pm.menuItem(label = 'circle')
        pm.menuItem(label = 'square')
        pm.menuItem(label = 'cube')
        pm.menuItem(label = 'sphere')
        pm.menuItem(label = 'pill')
        pm.menuItem(label = 'triangle')
        pm.menuItem(label = 'push')
        pm.menuItem(label = 'inOut')
        pm.menuItem(label = 'yaw')
        pm.menuItem(label = 'outwardPointer')
        pm.menuItem(label = 'outwardCirclePointer')
        pm.menuItem(label = 'spin')
        pm.menuItem(label = 'gear')
        pm.menuItem(label = 'star')
        pm.menuItem(label = 'lightbulb')
        pm.menuItem(label = 'pin')
        pm.menuItem(label = 'pin_round')
        pm.menuItem(label = 'squarePointer')
        pm.menuItem(label = 'cross')
        pm.menuItem(label = 'rotateTwoDirections')
        pm.menuItem(label = 'circleLiner')
        pm.menuItem(label = 'circleGrabber')
        pm.menuItem(label = 'circleLiner')
        pm.menuItem(label = 'circle_corner')
        pm.menuItem(label = 'cylinder')
        pm.menuItem(label = 'twoAxisRotate')
        pm.menuItem(label = 'fx')
        #just space
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        #Button
        pm.button( label='CREATE', command=defaultButtonPush ,align='right', w=80 ) 
        pm.separator(h=10,style='none')  
        #Colour Picker
        pm.colorIndexSliderGrp('test2', min=0, max=32, value=18, w= 242, h=10,  cc= 'pickColourI()' )
        #JUST SPACE
        #pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        pm.separator(h=10,style='none')
        #pm.button( label='CREATE', command=defaultButtonPush ,align='right', w=75 )
        pm.showWindow(gui)
    sbcmUI()

        