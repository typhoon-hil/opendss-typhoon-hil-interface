def update_properties(mdl, _Isource_mask):
    ## PROPERTIES

    _Isource_mask_amps = mdl.create_property(
        item_handle=_Isource_mask,
        name="amps",
        label="Current",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="A"
    )
    _Isource_mask_Angle = mdl.create_property(
        item_handle=_Isource_mask,
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
    _Isource_mask_Frequency = mdl.create_property(
        item_handle=_Isource_mask,
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
    _Isource_mask_global_basefreq = mdl.create_property(
        item_handle=_Isource_mask,
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
    _Isource_mask_BaseFreq = mdl.create_property(
        item_handle=_Isource_mask,
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
    _Isource_mask_enable_monitoring = mdl.create_property(
        item_handle=_Isource_mask,
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

    mdl.set_property_value(mdl.prop(_Isource_mask, "amps"), "0")
    mdl.set_property_value(mdl.prop(_Isource_mask, "Angle"), "0")
    mdl.set_property_value(mdl.prop(_Isource_mask, "Frequency"), "60")
    mdl.set_property_value(mdl.prop(_Isource_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Isource_mask, "BaseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Isource_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Isource_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Isource_mask_global_basefreq, "property_value_edited", _Isource_mask_global_basefreq_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

def ports_initialization(mdl, _Isource_mask):
    _Isource = mdl.get_parent(_Isource_mask)


    ## CREATE INITIALIZATION PORTS 

    _Isource_A1 = mdl.create_port(
        name="A1",
        parent=_Isource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8496, 8096)
    )
    _Isource_B1 = mdl.create_port(
        name="B1",
        parent=_Isource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, 0.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8496, 8192)
    )
    _Isource_C1 = mdl.create_port(
        name="C1",
        parent=_Isource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, 32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8496, 8288)
    )
