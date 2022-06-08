import pymel.core as pm

from . import all_control_options

def wheel_builder(wheel_up = 0, wheel_rotate = 1, wheel_type = 0):
    axes = {0: 'X',
            1: 'Y',
            2: 'Z'}
    ctrls = pm.ls(selection = True)
    for ctrl in ctrls:
        drv = pm.listRelatives(ctrl, parent = True)[0]
        xfrm = pm.listRelatives(drv, parent = True)[0]
        corrector = pm.group(em = True, name = drv + "_corrector")
        pm.matchTransform(corrector, xfrm)
        pm.parent(corrector, xfrm)
        pm.parent(drv, corrector)

        name = ctrl.split("CNT_")[1]
        grp_cnt = pm.group(em = True, n = "control_rotate" + name)
        xform_cnt = pm.group(em = True, n = "XFORM_rotate" + name)
        drv_cnt = pm.group(em = True, n = "DRV_rotate" + name)
        cnt = pm.group(em = True, n = "CNT_rotate" + name)
        pm.parent(cnt, drv_cnt)
        pm.parent(drv_cnt, xform_cnt)
        pm.parent(xform_cnt, grp_cnt)
        pm.matchTransform(xform_cnt, ctrl)
        pm.setAttr(xform_cnt + '.translate' + axes[wheel_up], 0)   
        pm.addAttr(cnt, ln = 'autoRoll', at = "enum", en = "OFF:ON:", keyable = True)
        pm.addAttr(cnt, ln = "speed", at = "double", keyable = True)

        decMat = pm.shadingNode('decomposeMatrix', asUtility = True)
        cond = pm.shadingNode('condition', asUtility = True)
        mulDiv = pm.shadingNode('multiplyDivide', asUtility = True)
        add_doub_01 = pm.shadingNode('addDoubleLinear', asUtility = True)
        add_doub_02 = pm.shadingNode('addDoubleLinear', asUtility = True)
        unit_conv = pm.shadingNode('unitConversion', asUtility = True)
        

        
        if wheel_type == 0:
            pm.setAttr(unit_conv + ".conversionFactor", -2)
        else:
            pm.setAttr(unit_conv + ".conversionFactor", 2)
        

        pm.connectAttr(cnt + ".worldInverseMatrix[0]", decMat + ".inputMatrix", force = True)
        pm.connectAttr(cnt + ".autoRoll", cond + ".firstTerm", force = True)
        pm.connectAttr(cnt + ".speed", cond + ".colorIfFalseR", force = True)

        wheel_front = 2

        for i in range(0, 2):
            if axes[i] != axes[wheel_up]:
                if axes[i] != axes[wheel_rotate]:
                    wheel_front = i
        

        pm.connectAttr(decMat + ".outputTranslate" + axes[wheel_front], add_doub_01 + ".input1", force = True)

        pm.connectAttr(add_doub_01 + ".output", mulDiv + ".input1X", force = True)

        pm.connectAttr(cond + ".outColorR", mulDiv + ".input2X", force = True)

        mulDiv_neg = pm.shadingNode('multiplyDivide', asUtility = True)
        if wheel_type == 0:
            pm.setAttr(mulDiv_neg + ".input2X", 1)
        else:
            pm.setAttr(mulDiv_neg + ".input2X", -1)

        pm.connectAttr(mulDiv + ".outputX", mulDiv_neg + ".input1X")

        pm.connectAttr(cnt + ".translate" + axes[wheel_up], unit_conv + ".input")
   

        
        pm.connectAttr(mulDiv_neg + ".outputX",  add_doub_02 + ".input2", force = True)
        pm.connectAttr(cnt + ".translate" + axes[wheel_up], unit_conv + ".input", force = True)
        pm.connectAttr(unit_conv + ".output", add_doub_02 + ".input1")
        pm.connectAttr(add_doub_02 + ".output", drv + ".rotate" + axes[wheel_rotate])
        pm.setAttr(cnt + ".autoRoll", 1)
        pm.setAttr(cnt + ".speed", 1)
        pm.select(drv)
        cur = pm.ls(selection = True)[0]
        correct_rot = pm.getAttr(cur + ".rotate" + axes[wheel_rotate])
        print(correct_rot)
        print(cur + ".rotate" + axes[wheel_rotate])
        print(drv + ".rotate" + axes[wheel_rotate])
        pm.setAttr(corrector + ".rotate" + axes[wheel_rotate], correct_rot*-1)
 
        

        pm.select(cnt)
        all_control_options.pick_control('circle')

        

        

def wheel_builder(wheel_up = "Y", wheel_rot = "X"):

    wheel_ctrl = pm.ls(selection = True)[0]
    wheel_drv = pm.listRelatives(wheel_ctrl, p = True)[0]

    #establish axes
    wheel_up = "Y"
    wheel_rot = "X"
    wheel_front = ""

    #get front axis
    if wheel_up == wheel_rot:
        pm.error("wheel rotate axis and up axis cannot be the same")

    allAxes = ["X", "Y", "Z"]
    for i in allAxes:
        if i == wheel_up or i == wheel_rot:
            pass
        else:
            wheel_front = i

    #create nodes
    decMat = pm.shadingNode("decomposeMatrix", asUtility = True)
    cond = pm.shadingNode("condition", asUtility = True)
    doubLin_01 = pm.shadingNode("addDoubleLinear", asUtility = True)
    doubLin_02 = pm.shadingNode("addDoubleLinear", asUtility = True)
    unitConv = pm.shadingNode("unitConversion", asUtility = True)
    mulDiv = pm.shadingNode("multiplyDivide", asUtility = True)
    plusMinus = pm.shadingNode("plusMinusAverage", asUtility = True)

    name = wheel_ctrl.split("_WHEEL")
    new_name = name[0] + "_WHEEL_BASE" + name[1]
    new_name = new_name.split("CNT_")[1]

    #create control setup
    ctrl = pm.group(em = True, n = "CNT_" + new_name)
    drv = pm.group(em = True, n = "DRV_" + new_name)
    xfrm = pm.group(em = True, n = "XFORM_" + new_name)
    par = pm.group(em = True, n = "control_" + new_name)
    pm.parent(ctrl, drv)
    pm.parent(drv, xfrm)
    pm.parent(xfrm, par)
    #place base
    pm.matchTransform(xfrm, wheel_ctrl)
    pm.setAttr(xfrm + ".translate" + wheel_up, 0)

    #create attrs
    pm.addAttr(ctrl, ln = "speed", at = "double", dv = 0, keyable = True)
    pm.addAttr(ctrl, ln = "autoRoll", at = "enum", en = "OFF:ON:", keyable = True)
    pm.setAttr(ctrl + ".speed", 1)
    pm.setAttr(ctrl + ".autoRoll", 1)

    #connect attrs
    pm.connectAttr(ctrl + ".worldInverseMatrix[0]", decMat + ".inputMatrix", force = True)
    pm.connectAttr(ctrl + ".speed", cond + ".colorIfFalseR", force = True)
    pm.connectAttr(ctrl + ".autoRoll", cond + ".firstTerm", force = True)
    pm.connectAttr(decMat + ".outputTranslate.outputTranslate" + wheel_front, doubLin_01 + ".input1", force = True)
    pm.connectAttr(doubLin_01 + ".output", mulDiv + ".input1X", force = True)
    pm.connectAttr(cond + ".outColorR", mulDiv + ".input2X", force = True)
    pm.connectAttr(mulDiv + ".outputX", plusMinus + ".input1D[0]", force = True)
    pm.disconnectAttr(mulDiv + ".outputX", plusMinus + ".input1D[0]")
    pm.connectAttr(mulDiv + ".outputX", plusMinus + ".input1D[1]", force = True)
    pm.setAttr(plusMinus + ".operation", 2)
    pm.connectAttr(ctrl + ".translate" + wheel_front, unitConv + ".input", force = True)
    pm.setAttr(unitConv + ".conversionFactor", -2, force = True)
    pm.connectAttr(unitConv + ".output", doubLin_02 + ".input1", force = True)
    pm.connectAttr(plusMinus + ".output1D", doubLin_02 + ".input2", force = True)
    pm.connectAttr(doubLin_02 + ".output", wheel_drv + ".rotate" + wheel_rot, force = True)
    pm.connectAttr(ctrl + ".translate" + wheel_up, wheel_drv + ".translate" + wheel_up, force = True)

    square_curve = pm.curve(d = 1, p = [(-60, 0, -60), (-60, 0, 60), (60, 0, 60), (60, 0, -60), (-60, 0, -60)], 
                            k = (0, 1, 2, 3, 4)) 

    pm.select(square_curve, r = True)
    pm.select(ctrl, add = True)

    all_control_options.swap_shape()











    return
  
