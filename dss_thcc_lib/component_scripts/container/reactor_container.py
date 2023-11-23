def update_properties(mdl, _Reactor_mask):
    ## PROPERTIES

    _Reactor_mask_tp_connection = mdl.create_property(
        item_handle=_Reactor_mask,
        name="tp_connection",
        label="Connection",
        widget="combo",
        combo_values=['Y - Grounded', 'Y', 'Δ', 'In series'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Reactor_mask_global_basefreq = mdl.create_property(
        item_handle=_Reactor_mask,
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
    _Reactor_mask_baseFreq = mdl.create_property(
        item_handle=_Reactor_mask,
        name="baseFreq",
        label="Base frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit="Hz"
    )
    _Reactor_mask_phases = mdl.create_property(
        item_handle=_Reactor_mask,
        name="phases",
        label="Phases",
        widget="combo",
        combo_values=['3', '2', '1'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Reactor_mask_Kv = mdl.create_property(
        item_handle=_Reactor_mask,
        name="Kv",
        label="kV",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="kV"
    )
    _Reactor_mask_Kvar = mdl.create_property(
        item_handle=_Reactor_mask,
        name="Kvar",
        label="kVar",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="kVAr"
    )
    _Reactor_mask_C = mdl.create_property(
        item_handle=_Reactor_mask,
        name="L",
        label="L",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Reactor_mask_enable_monitoring = mdl.create_property(
        item_handle=_Reactor_mask,
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

    mdl.set_property_value(mdl.prop(_Reactor_mask, "tp_connection"), "Y - Grounded")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "baseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "phases"), "3")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "Kv"), "12.47")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "Kvar"), "600")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "L"), "0.69")
    mdl.set_property_value(mdl.prop(_Reactor_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Reactor_mask_tp_connection_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Reactor_mask_tp_connection, "property_value_edited", _Reactor_mask_tp_connection_property_value_edited)
    _Reactor_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Reactor_mask_global_basefreq, "property_value_edited", _Reactor_mask_global_basefreq_property_value_edited)
    _Reactor_mask_phases_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Reactor_mask_phases, "property_value_edited", _Reactor_mask_phases_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Reactor_mask_tp_connection_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Reactor_mask_tp_connection, "property_value_changed",
                         _Reactor_mask_tp_connection_property_value_changed)

    _Reactor_mask_phases_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Reactor_mask_phases, "property_value_changed",
                         _Reactor_mask_phases_property_value_changed)

def ports_initialization(mdl, _Reactor_mask):
    _Reactor = mdl.get_parent(_Reactor_mask)


    ## CREATE INITIALIZATION PORTS 

    _Reactor_A1 = mdl.create_port(
        name="A1",
        parent=_Reactor,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(8392, 8096)
    )
    _Reactor_B1 = mdl.create_port(
        name="B1",
        parent=_Reactor,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(0.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(8392, 8192)
    )
    _Reactor_C1 = mdl.create_port(
        name="C1",
        parent=_Reactor,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(8392, 8288)
    )
