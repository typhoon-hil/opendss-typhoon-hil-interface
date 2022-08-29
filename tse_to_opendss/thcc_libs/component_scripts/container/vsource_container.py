def update_properties(mdl, _Vsource_mask):
    ## PROPERTIES

    _Vsource_mask_ground_connected = mdl.create_property(
        item_handle=_Vsource_mask,
        name="ground_connected",
        label="Ground-connected",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Vsource_mask_basekv = mdl.create_property(
        item_handle=_Vsource_mask,
        name="basekv",
        label="Base voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="kV"
    )
    _Vsource_mask_pu = mdl.create_property(
        item_handle=_Vsource_mask,
        name="pu",
        label="pu",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Vsource_mask_Angle = mdl.create_property(
        item_handle=_Vsource_mask,
        name="Angle",
        label="Angle",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="°"
    )
    _Vsource_mask_Frequency = mdl.create_property(
        item_handle=_Vsource_mask,
        name="Frequency",
        label="Frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="Hz"
    )
    _Vsource_mask_global_basefreq = mdl.create_property(
        item_handle=_Vsource_mask,
        name="global_basefreq",
        label="Global base frequency",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Vsource_mask_BaseFreq = mdl.create_property(
        item_handle=_Vsource_mask,
        name="BaseFreq",
        label="Base frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit="Hz"
    )
    _Vsource_mask_r1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="r1",
        label="Positive-sequence resistance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="Ω"
    )
    _Vsource_mask_x1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x1",
        label="Positive-sequence reactance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="Ω"
    )
    _Vsource_mask_r0 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="r0",
        label="Zero-sequence resistance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="Ω"
    )
    _Vsource_mask_x0 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x0",
        label="Zero-sequence reactance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="Ω"
    )
    _Vsource_mask_enable_monitoring = mdl.create_property(
        item_handle=_Vsource_mask,
        name="enable_monitoring",
        label="Enable monitoring",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Monitoring",
        unit=""
    )


    ## SET PROPERTIES TO DEFAULT VALUES

    mdl.set_property_value(mdl.prop(_Vsource_mask, "ground_connected"), "True")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "basekv"), "115")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "pu"), "1")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "Angle"), "0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "Frequency"), "60")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "BaseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "r1"), "1.65")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x1"), "6.6")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "r0"), "1.9")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x0"), "5.7")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Vsource_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Vsource_mask_global_basefreq, "property_value_edited", _Vsource_mask_global_basefreq_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Vsource_mask_ground_connected_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Vsource_mask_ground_connected, "property_value_changed",
                         _Vsource_mask_ground_connected_property_value_changed)

def ports_initialization(mdl, _Vsource_mask):
    _Vsource = mdl.get_parent(_Vsource_mask)


    ## CREATE INITIALIZATION PORTS 

    _Vsource_A1 = mdl.create_port(
        name="A1",
        parent=_Vsource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8496, 8096)
    )
    _Vsource_B1 = mdl.create_port(
        name="B1",
        parent=_Vsource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, 0.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8496, 8192)
    )
    _Vsource_C1 = mdl.create_port(
        name="C1",
        parent=_Vsource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, 32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8496, 8288)
    )
