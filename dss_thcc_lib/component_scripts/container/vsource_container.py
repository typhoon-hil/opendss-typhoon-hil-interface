def update_properties(mdl, _Vsource_mask):
    ## PROPERTIES

    _Vsource_mask_basekv = mdl.create_property(
        item_handle=_Vsource_mask,
        name="basekv",
        label="Base Voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General:1",
        unit="kV"
    )
    _Vsource_mask_baseMVA = mdl.create_property(
        item_handle=_Vsource_mask,
        name="baseMVA",
        label="Base Power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General",
        unit="MVA"
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
        tab_name="General",
        unit=""
    )
    _Vsource_mask_baseFreq = mdl.create_property(
        item_handle=_Vsource_mask,
        name="baseFreq",
        label="Base frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General",
        unit="Hz"
    )
    _Vsource_mask_tp_connection = mdl.create_property(
        item_handle=_Vsource_mask,
        name="tp_connection",
        label="Connection method",
        widget="combo",
        combo_values=['Y - Grounded', 'In series'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Vsource_mask_pu = mdl.create_property(
        item_handle=_Vsource_mask,
        name="pu",
        label="Voltage [pu]",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters:2",
        unit=""
    )
    _Vsource_mask_Angle = mdl.create_property(
        item_handle=_Vsource_mask,
        name="Angle",
        label="Phase [°]",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit=""
    )
    _Vsource_mask_Frequency = mdl.create_property(
        item_handle=_Vsource_mask,
        name="Frequency",
        label="Frequency [Hz]",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit=""
    )
    _Vsource_mask_input_method = mdl.create_property(
        item_handle=_Vsource_mask,
        name="input_method",
        label="Input Method",
        widget="combo",
        combo_values=['Z', 'Zpu', 'MVAsc', 'Isc'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit=""
    )
    _Vsource_mask_r1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="r1",
        label="R1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit="Ω"
    )
    _Vsource_mask_x1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x1",
        label="X1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit="Ω"
    )
    _Vsource_mask_r0 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="r0",
        label="R0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit="Ω"
    )
    _Vsource_mask_x0 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x0",
        label="X0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Parameters",
        unit="Ω"
    )
    _Vsource_mask_r1_pu = mdl.create_property(
        item_handle=_Vsource_mask,
        name="r1_pu",
        label="R1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="pu"
    )
    _Vsource_mask_x1_pu = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x1_pu",
        label="X1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="pu"
    )
    _Vsource_mask_r0_pu = mdl.create_property(
        item_handle=_Vsource_mask,
        name="r0_pu",
        label="R0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="pu"
    )
    _Vsource_mask_x0_pu = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x0_pu",
        label="X0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="pu"
    )
    _Vsource_mask_mva_sc3 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="mva_sc3",
        label="3ph Short Circuit Power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="MVA"
    )
    _Vsource_mask_mva_sc1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="mva_sc1",
        label="1ph Short Circuit Power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="MVA"
    )
    _Vsource_mask_i_sc3 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="i_sc3",
        label="3ph Short Circuit Current",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="A"
    )
    _Vsource_mask_i_sc1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="i_sc1",
        label="1ph Short Circuit Current",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit="A"
    )
    _Vsource_mask_x1r1 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x1r1",
        label="X1/R1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit=""
    )
    _Vsource_mask_x0r0 = mdl.create_property(
        item_handle=_Vsource_mask,
        name="x0r0",
        label="X0/R0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Parameters",
        unit=""
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
        tab_name="Monitoring:3",
        unit=""
    )


    ## SET PROPERTIES TO DEFAULT VALUES

    mdl.set_property_value(mdl.prop(_Vsource_mask, "basekv"), "115.0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "baseMVA"), "100.0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "global_basefreq"), "False")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "baseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "tp_connection"), "Y - Grounded")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "pu"), "1.0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "Angle"), "0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "Frequency"), "60")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "input_method"), "Z")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "r1"), "1.65")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x1"), "6.6")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "r0"), "1.9")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x0"), "5.7")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "r1_pu"), "0.0121")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x1_pu"), "0.0485")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "r0_pu"), "0.0136")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x0_pu"), "0.0407")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "mva_sc3"), "2000")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "mva_sc1"), "2100")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "i_sc3"), "10000")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "i_sc1"), "10500")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x1r1"), "4.0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "x0r0"), "3.0")
    mdl.set_property_value(mdl.prop(_Vsource_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Vsource_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Vsource_mask_global_basefreq, "property_value_edited", _Vsource_mask_global_basefreq_property_value_edited)
    _Vsource_mask_input_method_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Vsource_mask_input_method, "property_value_edited", _Vsource_mask_input_method_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Vsource_mask_to_connection_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    """
    mdl.set_handler_code(_Vsource_mask_to_connection, "property_value_changed",
                         _Vsource_mask_to_connection_property_value_changed)

    _Vsource_mask_ground_connected_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
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
        terminal_position=(32, -32),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(8496, 8096)
    )
    _Vsource_B1 = mdl.create_port(
        name="B1",
        parent=_Vsource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32, 0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(8496, 8192)
    )
    _Vsource_C1 = mdl.create_port(
        name="C1",
        parent=_Vsource,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32, 32),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(8496, 8288)
    )
