def update_properties(mdl, _Capacitor_Bank_mask):
    ## PROPERTIES

    _Capacitor_Bank_mask_tp_connection = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
        name="tp_connection",
        label="Connection",
        widget="combo",
        combo_values=['Y', 'Y-grounded', 'Δ', 'Series'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Capacitor_Bank_mask_global_basefreq = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
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
    _Capacitor_Bank_mask_BaseFreq = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
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
    _Capacitor_Bank_mask_phases = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
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
    _Capacitor_Bank_mask_Kv = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
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
    _Capacitor_Bank_mask_Kvar = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
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
    _Capacitor_Bank_mask_C = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
        name="C",
        label="C",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Capacitor_Bank_mask_enable_monitoring = mdl.create_property(
        item_handle=_Capacitor_Bank_mask,
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

    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "tp_connection"), "Y")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "BaseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "phases"), "3")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "Kv"), "12.47")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "Kvar"), "600")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "C"), "1e-6")
    mdl.set_property_value(mdl.prop(_Capacitor_Bank_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Capacitor_Bank_mask_tp_connection_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Capacitor_Bank_mask_tp_connection, "property_value_edited", _Capacitor_Bank_mask_tp_connection_property_value_edited)
    _Capacitor_Bank_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Capacitor_Bank_mask_global_basefreq, "property_value_edited", _Capacitor_Bank_mask_global_basefreq_property_value_edited)
    _Capacitor_Bank_mask_phases_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Capacitor_Bank_mask_phases, "property_value_edited", _Capacitor_Bank_mask_phases_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Capacitor_Bank_mask_tp_connection_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Capacitor_Bank_mask_tp_connection, "property_value_changed",
                         _Capacitor_Bank_mask_tp_connection_property_value_changed)

    _Capacitor_Bank_mask_phases_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Capacitor_Bank_mask_phases, "property_value_changed",
                         _Capacitor_Bank_mask_phases_property_value_changed)

def ports_initialization(mdl, _Capacitor_Bank_mask):
    _Capacitor_Bank = mdl.get_parent(_Capacitor_Bank_mask)


    ## CREATE INITIALIZATION PORTS 

    _Capacitor_Bank_A1 = mdl.create_port(
        name="A1",
        parent=_Capacitor_Bank,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8392, 8096)
    )
    _Capacitor_Bank_B1 = mdl.create_port(
        name="B1",
        parent=_Capacitor_Bank,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(0.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8392, 8192)
    )
    _Capacitor_Bank_C1 = mdl.create_port(
        name="C1",
        parent=_Capacitor_Bank,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8392, 8288)
    )
