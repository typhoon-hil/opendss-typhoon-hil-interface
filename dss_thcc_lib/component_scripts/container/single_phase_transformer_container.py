def update_properties(mdl, _Single_Phase_Transformer_mask):
    ## PROPERTIES

    _Single_Phase_Transformer_mask_num_windings = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="num_windings",
        label="Number of windings",
        widget="combo",
        combo_values=['2', '3', '4', '5', '6', '7', '8', '9', '10'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_12 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_12",
        label="Embedded coupling 1-2",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_13 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_13",
        label="Embedded coupling 1-3",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_14 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_14",
        label="Embedded coupling 1-4",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_15 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_15",
        label="Embedded coupling 1-5",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_16 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_16",
        label="Embedded coupling 1-6",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_17 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_17",
        label="Embedded coupling 1-7",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_18 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_18",
        label="Embedded coupling 1-8",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_19 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_19",
        label="Embedded coupling 1-9",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_embedded_cpl_110 = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="embedded_cpl_110",
        label="Embedded coupling 1-10",
        widget="combo",
        combo_values=['None', 'Ideal Transformer', 'TLM'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Core coupling:3",
        unit=""
    )
    _Single_Phase_Transformer_mask_KVs = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="KVs",
        label="Array of rated winding phase voltages",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="kV"
    )
    _Single_Phase_Transformer_mask_KVAs = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="KVAs",
        label="Array of winding kVA ratings",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="kVA"
    )
    _Single_Phase_Transformer_mask_percentRs = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="percentRs",
        label="Array of winding percent resistances",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Single_Phase_Transformer_mask_XArray = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="XArray",
        label="Winding reactances",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Single_Phase_Transformer_mask_XscArray = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="XscArray",
        label="Array of short-circuit reactances",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit="%"
    )
    _Single_Phase_Transformer_mask_global_basefreq = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
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
    _Single_Phase_Transformer_mask_Basefreq = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="Basefreq",
        label="Base frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit="Hz"
    )
    _Single_Phase_Transformer_mask_percentNoloadloss = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="percentNoloadloss",
        label="No-load losses",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Single_Phase_Transformer_mask_percentimag = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="percentimag",
        label="Magnetizing current",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Single_Phase_Transformer_mask_regcontrol_on = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="regcontrol_on",
        label="Activate RegControl",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="RegControl:4",
        unit=""
    )
    _Single_Phase_Transformer_mask_maxtap = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="maxtap",
        label="Maximum tap voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="pu"
    )
    _Single_Phase_Transformer_mask_mintap = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="mintap",
        label="Minimum tap voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="pu"
    )
    _Single_Phase_Transformer_mask_numtaps = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="numtaps",
        label="Number of taps",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit=""
    )
    _Single_Phase_Transformer_mask_ctrl_winding = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="ctrl_winding",
        label="Monitored winding",
        widget="combo",
        combo_values=['Winding 1', 'Winding 2'],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit=""
    )
    _Single_Phase_Transformer_mask_vreg = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="vreg",
        label="Vreg",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="V"
    )
    _Single_Phase_Transformer_mask_ptratio = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="ptratio",
        label="PT ratio",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="V"
    )
    _Single_Phase_Transformer_mask_winding_voltage = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="winding_voltage",
        label="Voltage result",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="V"
    )
    _Single_Phase_Transformer_mask_band = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="band",
        label="Bandwidth",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="V"
    )
    _Single_Phase_Transformer_mask_delay = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="delay",
        label="Delay",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="s"
    )
    _Single_Phase_Transformer_mask_execution_rate = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="execution_rate",
        label="Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="RegControl:4",
        unit="s"
    )
    _Single_Phase_Transformer_mask_enable_monitoring = mdl.create_property(
        item_handle=_Single_Phase_Transformer_mask,
        name="enable_monitoring",
        label="Enable monitoring",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Monitoring:5",
        unit=""
    )


    ## SET PROPERTIES TO DEFAULT VALUES

    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "num_windings"), "2")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_12"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_13"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_14"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_15"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_16"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_17"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_18"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_19"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "embedded_cpl_110"), "None")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "KVs"), "[12.47e3, 12.47e3]")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "KVAs"), "[12e6, 6e6]")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "percentRs"), "[2, 2]")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "XArray"), "[1, 1]")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "XscArray"), "[1]")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "Basefreq"), "60")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "percentNoloadloss"), "1")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "percentimag"), "0")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "regcontrol_on"), "False")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "maxtap"), "1.1")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "mintap"), "0.9")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "numtaps"), "32")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "ctrl_winding"), "Winding 1")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "vreg"), "207.84")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "ptratio"), "60")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "winding_voltage"), "12470")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "band"), "3")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "delay"), "15")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "execution_rate"), "100e-6")
    mdl.set_property_value(mdl.prop(_Single_Phase_Transformer_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Single_Phase_Transformer_mask_num_windings_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.show_hide_couplings(mdl, container_handle)
    comp_script.update_regctrl_combo(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_num_windings, "property_value_edited", _Single_Phase_Transformer_mask_num_windings_property_value_edited)
    _Single_Phase_Transformer_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.toggle_frequency_prop(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_global_basefreq, "property_value_edited", _Single_Phase_Transformer_mask_global_basefreq_property_value_edited)
    _Single_Phase_Transformer_mask_regcontrol_on_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.toggle_regcontrol_props(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_regcontrol_on, "property_value_edited", _Single_Phase_Transformer_mask_regcontrol_on_property_value_edited)
    _Single_Phase_Transformer_mask_vreg_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.calculate_winding_voltage(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_vreg, "property_value_edited", _Single_Phase_Transformer_mask_vreg_property_value_edited)
    _Single_Phase_Transformer_mask_ptratio_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_ptratio, "property_value_edited", _Single_Phase_Transformer_mask_ptratio_property_value_edited)
    _Single_Phase_Transformer_mask_winding_voltage_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_winding_voltage, "property_value_edited", _Single_Phase_Transformer_mask_winding_voltage_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Single_Phase_Transformer_mask_num_windings_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    if not new_value == old_value: # If the model is not being loaded.
        comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Single_Phase_Transformer_mask_num_windings, "property_value_changed",
                         _Single_Phase_Transformer_mask_num_windings_property_value_changed)

def ports_initialization(mdl, _Single_Phase_Transformer_mask):
    _Single_Phase_Transformer = mdl.get_parent(_Single_Phase_Transformer_mask)


    ## CREATE INITIALIZATION PORTS 

    _Single_Phase_Transformer_A1 = mdl.create_port(
        name="A1",
        parent=_Single_Phase_Transformer,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32.0, -16.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7992, 8104)
    )
    _Single_Phase_Transformer_B1 = mdl.create_port(
        name="B1",
        parent=_Single_Phase_Transformer,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32.0, 16.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7992, 8296)
    )
    _Single_Phase_Transformer_A2 = mdl.create_port(
        name="A2",
        parent=_Single_Phase_Transformer,
        label="",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(32.0, -16.0),
        rotation="up",
        flip="flip_horizontal",
        hide_name=False,
        position=(9376, 8192)
    )
    _Single_Phase_Transformer_B2 = mdl.create_port(
        name="B2",
        parent=_Single_Phase_Transformer,
        label="",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(32.0, 16.0),
        rotation="up",
        flip="flip_horizontal",
        hide_name=False,
        position=(9376, 8288)
    )
