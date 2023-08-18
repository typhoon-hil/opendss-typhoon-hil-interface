def update_properties(mdl, _Storage_mask):
    ## PROPERTIES

    _Storage_mask_dispatch_p = mdl.create_property(
        item_handle=_Storage_mask,
        name="dispatch_p",
        label="Dispatch P",
        widget="combo",
        combo_values=['Default', 'Follow'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Storage_mask_dispatch_q = mdl.create_property(
        item_handle=_Storage_mask,
        name="dispatch_q",
        label="Dispatch Q",
        widget="combo",
        combo_values=['Unit PF', 'Constant PF', 'Constant kVAr'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Storage_mask_snap_status = mdl.create_property(
        item_handle=_Storage_mask,
        name="snap_status",
        label="Snap solve status",
        widget="combo",
        combo_values=['Charging', 'Discharging', 'Idling'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Storage_mask_kv = mdl.create_property(
        item_handle=_Storage_mask,
        name="kv",
        label="Nominal voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="kV"
    )
    _Storage_mask_global_basefreq = mdl.create_property(
        item_handle=_Storage_mask,
        name="global_basefreq",
        label="Global base frequency",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit=""
    )
    _Storage_mask_baseFreq = mdl.create_property(
        item_handle=_Storage_mask,
        name="baseFreq",
        label="Base frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="Hz"
    )
    _Storage_mask_kwrated = mdl.create_property(
        item_handle=_Storage_mask,
        name="kwrated",
        label="Rated kW",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="kW"
    )
    _Storage_mask_kwhrated = mdl.create_property(
        item_handle=_Storage_mask,
        name="kwhrated",
        label="Rated kWh",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="kWh"
    )
    _Storage_mask_chargetrigger = mdl.create_property(
        item_handle=_Storage_mask,
        name="chargetrigger",
        label="ChargeTrigger",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Storage_mask_dischargetrigger = mdl.create_property(
        item_handle=_Storage_mask,
        name="dischargetrigger",
        label="DischargeTrigger",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Storage_mask_pct_charge = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_charge",
        label="%Charge",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Storage_mask_pct_discharge = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_discharge",
        label="%Discharge",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Storage_mask_pct_effcharge = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_effcharge",
        label="Charge efficiency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="%"
    )
    _Storage_mask_pct_effdischarge = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_effdischarge",
        label="Discharge efficiency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="%"
    )
    _Storage_mask_kvar = mdl.create_property(
        item_handle=_Storage_mask,
        name="kvar",
        label="Reactive power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Ratings:3",
        unit="kVAr"
    )
    _Storage_mask_pf = mdl.create_property(
        item_handle=_Storage_mask,
        name="pf",
        label="Power factor",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Ratings:3",
        unit=""
    )
    _Storage_mask_pct_idlingkvar = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_idlingkvar",
        label="%IdlingkVAr",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Ratings:3",
        unit="%"
    )
    _Storage_mask_pct_idlingkw = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_idlingkw",
        label="Idling losses",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="%"
    )
    _Storage_mask_pct_reserve = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_reserve",
        label="Reserve mode SOC",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Ratings:3",
        unit="%"
    )
    _Storage_mask_load_loadshape = mdl.create_property(
        item_handle=_Storage_mask,
        name="load_loadshape",
        label="LoadShape object",
        widget="button",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings:2",
        button_label="Choose",
        unit=""
    )
    _Storage_mask_loadshape_name = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_name",
        label="LoadShape name",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_loadshape_from_file = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_from_file",
        label="From CSV file",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_useactual = mdl.create_property(
        item_handle=_Storage_mask,
        name="useactual",
        label="Actual value",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_loadshape_from_file_path = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_from_file_path",
        label="LoadShape from file - path",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_loadshape_from_file_column = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_from_file_column",
        label="LoadShape from file - column",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_loadshape_from_file_header = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_from_file_header",
        label="LoadShape from file - header",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_loadshape = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape",
        label="LoadShape points",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit="pu"
    )
    _Storage_mask_loadshape_int = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_int",
        label="LoadShape interval",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_timespan = mdl.create_property(
        item_handle=_Storage_mask,
        name="timespan",
        label="Loadshape time span",
        widget="combo",
        combo_values=['Daily', 'Yearly'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_T_Ts = mdl.create_property(
        item_handle=_Storage_mask,
        name="T_Ts",
        label="LoadShape time range",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit="h"
    )
    _Storage_mask_T_mode = mdl.create_property(
        item_handle=_Storage_mask,
        name="T_mode",
        label="LoadShape input mode",
        widget="combo",
        combo_values=['Loadshape index', 'Time'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _Storage_mask_pct_stored = mdl.create_property(
        item_handle=_Storage_mask,
        name="pct_stored",
        label="Initial SOC",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="%"
    )
    _Storage_mask_execution_rate = mdl.create_property(
        item_handle=_Storage_mask,
        name="execution_rate",
        label="Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Storage_mask_vmaxpu = mdl.create_property(
        item_handle=_Storage_mask,
        name="vmaxpu",
        label="vmaxpu",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Storage_mask_vminpu = mdl.create_property(
        item_handle=_Storage_mask,
        name="vminpu",
        label="vminpu",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Storage_mask_kva = mdl.create_property(
        item_handle=_Storage_mask,
        name="kva",
        label="kva",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Storage_mask_inv_r = mdl.create_property(
        item_handle=_Storage_mask,
        name="inv_r",
        label="AC-side resistance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter:4",
        unit="Ω"
    )
    _Storage_mask_inv_l = mdl.create_property(
        item_handle=_Storage_mask,
        name="inv_l",
        label="AC-side inductance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter:4",
        unit="H"
    )
    _Storage_mask_inv_rf = mdl.create_property(
        item_handle=_Storage_mask,
        name="inv_rf",
        label="Filter resistance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter:4",
        unit="Ω"
    )
    _Storage_mask_inv_cf = mdl.create_property(
        item_handle=_Storage_mask,
        name="inv_cf",
        label="Filter capacitance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter:4",
        unit="F"
    )
    _Storage_mask_inv_kp = mdl.create_property(
        item_handle=_Storage_mask,
        name="inv_kp",
        label="Controller Kp",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter:4",
        unit=""
    )
    _Storage_mask_inv_ki = mdl.create_property(
        item_handle=_Storage_mask,
        name="inv_ki",
        label="Controller Ki",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter:4",
        unit=""
    )
    _Storage_mask_loadshape_n_points = mdl.create_property(
        item_handle=_Storage_mask,
        name="loadshape_n_points",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Storage_mask_enable_monitoring = mdl.create_property(
        item_handle=_Storage_mask,
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

    mdl.set_property_value(mdl.prop(_Storage_mask, "dispatch_p"), "Default")
    mdl.set_property_value(mdl.prop(_Storage_mask, "dispatch_q"), "Unit PF")
    mdl.set_property_value(mdl.prop(_Storage_mask, "snap_status"), "Charging")
    mdl.set_property_value(mdl.prop(_Storage_mask, "kv"), "115")
    mdl.set_property_value(mdl.prop(_Storage_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Storage_mask, "baseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Storage_mask, "kwrated"), "25")
    mdl.set_property_value(mdl.prop(_Storage_mask, "kwhrated"), "50")
    mdl.set_property_value(mdl.prop(_Storage_mask, "chargetrigger"), "0.2")
    mdl.set_property_value(mdl.prop(_Storage_mask, "dischargetrigger"), "0.6")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_charge"), "100")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_discharge"), "100")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_effcharge"), "90")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_effdischarge"), "90")
    mdl.set_property_value(mdl.prop(_Storage_mask, "kvar"), "0")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pf"), "1")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_idlingkvar"), "0")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_idlingkw"), "1")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_reserve"), "20")
    mdl.set_property_value(mdl.prop(_Storage_mask, "load_loadshape"), "Choose")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_name"), "Default")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_from_file"), "False")
    mdl.set_property_value(mdl.prop(_Storage_mask, "useactual"), "False")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_from_file_path"), "")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_from_file_column"), "1")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_from_file_header"), "True")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape"), "[0.4, 0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.7, 0.7, 0.8, 0.7, 0.7, 0.8, 0.8, 0.8, 1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.5]")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_int"), "1")
    mdl.set_property_value(mdl.prop(_Storage_mask, "timespan"), "Daily")
    mdl.set_property_value(mdl.prop(_Storage_mask, "T_Ts"), "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]")
    mdl.set_property_value(mdl.prop(_Storage_mask, "T_mode"), "Time")
    mdl.set_property_value(mdl.prop(_Storage_mask, "pct_stored"), "100")
    mdl.set_property_value(mdl.prop(_Storage_mask, "execution_rate"), "100e-6")
    mdl.set_property_value(mdl.prop(_Storage_mask, "vmaxpu"), "1.1")
    mdl.set_property_value(mdl.prop(_Storage_mask, "vminpu"), "0.9")
    mdl.set_property_value(mdl.prop(_Storage_mask, "kva"), "0")
    mdl.set_property_value(mdl.prop(_Storage_mask, "inv_r"), "1e-5")
    mdl.set_property_value(mdl.prop(_Storage_mask, "inv_l"), "100e-6")
    mdl.set_property_value(mdl.prop(_Storage_mask, "inv_rf"), "100e-3")
    mdl.set_property_value(mdl.prop(_Storage_mask, "inv_cf"), "1.013e-3")
    mdl.set_property_value(mdl.prop(_Storage_mask, "inv_kp"), "0.0001")
    mdl.set_property_value(mdl.prop(_Storage_mask, "inv_ki"), "0.03")
    mdl.set_property_value(mdl.prop(_Storage_mask, "loadshape_n_points"), "0")
    mdl.set_property_value(mdl.prop(_Storage_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Storage_mask_dispatch_p_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.update_dispatch_mode(mdl, container_handle)
    mdl.refresh_icon(container_handle)
    
    """
    mdl.set_handler_code(_Storage_mask_dispatch_p, "property_value_edited", _Storage_mask_dispatch_p_property_value_edited)
    _Storage_mask_dispatch_q_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.update_dispatch_mode(mdl, container_handle)
    mdl.refresh_icon(container_handle)
    
    """
    mdl.set_handler_code(_Storage_mask_dispatch_q, "property_value_edited", _Storage_mask_dispatch_q_property_value_edited)
    _Storage_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.toggle_frequency_prop(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Storage_mask_global_basefreq, "property_value_edited", _Storage_mask_global_basefreq_property_value_edited)
    _Storage_mask_loadshape_name_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Storage_mask_loadshape_name, "property_value_edited", _Storage_mask_loadshape_name_property_value_edited)
    _Storage_mask_loadshape_from_file_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Storage_mask_loadshape_from_file, "property_value_edited", _Storage_mask_loadshape_from_file_property_value_edited)
    _Storage_mask_useactual_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Storage_mask_useactual, "property_value_edited", _Storage_mask_useactual_property_value_edited)
    _Storage_mask_loadshape_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Storage_mask_loadshape, "property_value_edited", _Storage_mask_loadshape_property_value_edited)
    _Storage_mask_loadshape_int_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Storage_mask_loadshape_int, "property_value_edited", _Storage_mask_loadshape_int_property_value_edited)
    _Storage_mask_T_mode_property_value_edited = """
    if new_value == "Time":
        mdl.enable_property(mdl.prop(container_handle, "T_Ts"))
    else:
        mdl.disable_property(mdl.prop(container_handle, "T_Ts"))
    
    """
    mdl.set_handler_code(_Storage_mask_T_mode, "property_value_edited", _Storage_mask_T_mode_property_value_edited)


    ## BUTTON HANDLERS

    _Storage_mask_load_loadshape_button_clicked = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.load_loadshape(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Storage_mask_load_loadshape, "button_clicked", _Storage_mask_load_loadshape_button_clicked)


    ## CHANGED HANDLERS

def ports_initialization(mdl, _Storage_mask):
    _Storage = mdl.get_parent(_Storage_mask)


    ## CREATE INITIALIZATION PORTS 

    _Storage_A1 = mdl.create_port(
        name="A1",
        parent=_Storage,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-40.0, -32.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7104, 8216)
    )
    _Storage_B1 = mdl.create_port(
        name="B1",
        parent=_Storage,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-40.0, 0.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7104, 8312)
    )
    _Storage_C1 = mdl.create_port(
        name="C1",
        parent=_Storage,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-40.0, 32.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7104, 8408)
    )
    _Storage_Load_point = mdl.create_port(
        name="Load point",
        parent=_Storage,
        label="t",
        kind="sp",
        direction="in",
        dimension=(1,),
        terminal_position=(0.0, -48.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7792, 7272)
    )
