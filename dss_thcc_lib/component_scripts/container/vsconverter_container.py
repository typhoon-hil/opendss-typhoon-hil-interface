def update_properties(mdl, _VSConverter_mask):
    ## PROPERTIES

    _VSConverter_mask_ctrl_mode_str = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="ctrl_mode_str",
        label="Inverter control mode",
        widget="combo",
        combo_values=['PQ', 'PV', 'Vdc-Vac', 'Vdc-Q', 'Grid Forming', 'External Control'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Control mode:2",
        unit=""
    )
    _VSConverter_mask_ctrl_mode_int = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="ctrl_mode_int",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_ext_mode = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="ext_mode",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_P_ref_str = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="P_ref_str",
        label="Active power reference (kW)",
        widget="combo",
        combo_values=['External input', 'Converter nominal'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Control mode",
        unit=""
    )
    _VSConverter_mask_P_sel = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="P_sel",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_Q_ref_str = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Q_ref_str",
        label="Reactive power reference (kVAR)",
        widget="combo",
        combo_values=['External input', 'Converter nominal'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Control mode",
        unit=""
    )
    _VSConverter_mask_Q_sel = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Q_sel",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_V_ref_str = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="V_ref_str",
        label="Line voltage reference (kV)",
        widget="combo",
        combo_values=['External input', 'Converter nominal'],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Control mode",
        unit=""
    )
    _VSConverter_mask_V_sel = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="V_sel",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_vdc_ref_str = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="vdc_ref_str",
        label="DC Link voltage (kV)",
        widget="combo",
        combo_values=['External input', 'Converter nominal'],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Control mode",
        unit=""
    )
    _VSConverter_mask_fs_ref_str = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="fs_ref_str",
        label="Frequency (Hz)",
        widget="combo",
        combo_values=['External input', 'Converter nominal'],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Control mode",
        unit=""
    )
    _VSConverter_mask_w_sel = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="w_sel",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_P_kp = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="P_kp",
        label="P Controller proportional gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Controller settings:3",
        unit=""
    )
    _VSConverter_mask_P_ki = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="P_ki",
        label="P Controller integral gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_Q_kp = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Q_kp",
        label="Q Controller proportional gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_Q_ki = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Q_ki",
        label="Q Controller integral gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_V_kp = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="V_kp",
        label="V Controller proportional gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_V_ki = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="V_ki",
        label="V Controller integral gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_vdc_kp = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="vdc_kp",
        label="DC-Link Voltage Controller proportional gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_vdc_ki = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="vdc_ki",
        label="DC-Link Voltage Controller integral gain",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="Controller settings",
        unit=""
    )
    _VSConverter_mask_vdc_set = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="vdc_set",
        label="Inverter DC-Link Voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters:1",
        unit="kV"
    )
    _VSConverter_mask_dc_cap_en = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="dc_cap_en",
        label="Use Internal DC-Link Capacitor",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit=""
    )
    _VSConverter_mask_dc_cap = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="dc_cap",
        label="Internal DC-Link Capacitor",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="F"
    )
    _VSConverter_mask_dc_snub = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="dc_snub",
        label="DC-Link Snubber Resistance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="Ω"
    )
    _VSConverter_mask_vac_set = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="vac_set",
        label="Nominal AC Line voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="kV"
    )
    _VSConverter_mask_global_basefreq = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="global_basefreq",
        label="Global base frequency",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit=""
    )
    _VSConverter_mask_Fs = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Fs",
        label="Nominal Frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Inverter Parameters",
        unit="Hz"
    )
    _VSConverter_mask_Sinv = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Sinv",
        label="Nominal Active Power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="kW"
    )
    _VSConverter_mask_Qinv = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Qinv",
        label="Nominal Reactive Power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="kVAR"
    )
    _VSConverter_mask_Rac = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Rac",
        label="Series ac resistance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="Ω"
    )
    _VSConverter_mask_Lac = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Lac",
        label="Series ac inductance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Inverter Parameters",
        unit="H"
    )
    _VSConverter_mask_execution_rate = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="execution_rate",
        label="Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Execution Rate:5",
        unit="s"
    )
    _VSConverter_mask_cont_t = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="cont_t",
        label="Controller start time ",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Initialization:4",
        unit="s"
    )
    _VSConverter_mask_dss_ctrl = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="dss_ctrl",
        label="OpenDSS control mode",
        widget="combo",
        combo_values=['Fixed', 'PacVac', 'PacQac', 'VdcVac', 'VdcQac'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="OpenDSS Setting:6",
        unit=""
    )
    _VSConverter_mask_Phases = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Phases",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_kv = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="kv",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_kw = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="kw",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_pf = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="pf",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_model = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="model",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_baseFreq = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="baseFreq",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_r0 = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="r0",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_r1 = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="r1",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_x0 = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="x0",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_x1 = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="x1",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_pu = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="pu",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_Angle = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Angle",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_Frequency = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Frequency",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_basekv = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="basekv",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _VSConverter_mask_gen_ts_en = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="gen_ts_en",
        label="Enable time series",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings:6",
        unit=""
    )
    _VSConverter_mask_load_loadshape = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="load_loadshape",
        label="LoadShape object",
        widget="button",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        button_label="Choose",
        unit=""
    )
    _VSConverter_mask_loadshape_name = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_loadshape_from_file = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_useactual = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="useactual",
        label="Actual value",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_loadshape_from_file_path = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_loadshape_from_file_column = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_loadshape_from_file_header = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_loadshape = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="loadshape",
        label="LoadShape points",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_loadshape_int = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="loadshape_int",
        label="LoadShape interval",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit="h"
    )
    _VSConverter_mask_gen_ts_en_bit = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="gen_ts_en_bit",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_T_Ts = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="T_Ts",
        label="LoadShape time range",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit="h"
    )
    _VSConverter_mask_T_mode = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_S_Ts = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="S_Ts",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_Q_Ts = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Q_Ts",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_timespan = mdl.create_property(
        item_handle=_VSConverter_mask,
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
    _VSConverter_mask_T_Ts_internal = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="T_Ts_internal",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_dssT = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="dssT",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_dssnpts = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="dssnpts",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_T_Ts_max = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="T_Ts_max",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_del_Ts = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="del_Ts",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_Slen = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Slen",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_T_lim_low = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="T_lim_low",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_T_lim_high = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="T_lim_high",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_Ts_switch = mdl.create_property(
        item_handle=_VSConverter_mask,
        name="Ts_switch",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _VSConverter_mask_enable_monitoring = mdl.create_property(
        item_handle=_VSConverter_mask,
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

    mdl.set_property_value(mdl.prop(_VSConverter_mask, "ctrl_mode_str"), "PQ")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "ctrl_mode_int"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "ext_mode"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "P_ref_str"), "Converter nominal")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "P_sel"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Q_ref_str"), "Converter nominal")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Q_sel"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "V_ref_str"), "Converter nominal")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "V_sel"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "vdc_ref_str"), "Converter nominal")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "fs_ref_str"), "Converter nominal")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "w_sel"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "P_kp"), "2e-3")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "P_ki"), "0.2")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Q_kp"), "2e-3")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Q_ki"), "0.05")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "V_kp"), "1e-6")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "V_ki"), "50")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "vdc_kp"), "1000e-6")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "vdc_ki"), "0.01")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "vdc_set"), "2.5")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "dc_cap_en"), "True")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "dc_cap"), "1e-2")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "dc_snub"), "500")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "vac_set"), "1.73")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Fs"), "60")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Sinv"), "500")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Qinv"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Rac"), "0.01")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Lac"), "3e-5")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "execution_rate"), "100e-6")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "cont_t"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "dss_ctrl"), "Fixed")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Phases"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "kv"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "kw"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "pf"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "model"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "baseFreq"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "r0"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "r1"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "x0"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "x1"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "pu"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Angle"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Frequency"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "basekv"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "gen_ts_en"), "False")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "load_loadshape"), "Choose")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape_name"), "Default")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape_from_file"), "False")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "useactual"), "False")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape_from_file_path"), "")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape_from_file_column"), "1")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape_from_file_header"), "True")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape"), "[0.4, 0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.7, 0.7, 0.8, 0.7, 0.7, 0.8, 0.8, 0.8, 1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.5]")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "loadshape_int"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "gen_ts_en_bit"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "T_Ts"), "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "T_mode"), "Time")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "S_Ts"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Q_Ts"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "timespan"), "Daily")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "T_Ts_internal"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "dssT"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "dssnpts"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "T_Ts_max"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "del_Ts"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Slen"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "T_lim_low"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "T_lim_high"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "Ts_switch"), "0")
    mdl.set_property_value(mdl.prop(_VSConverter_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _VSConverter_mask_ctrl_mode_str_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.inv_control_mode_value_edited(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_ctrl_mode_str, "property_value_edited", _VSConverter_mask_ctrl_mode_str_property_value_edited)
    _VSConverter_mask_dc_cap_en_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.dc_link_cap_value_edited(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_dc_cap_en, "property_value_edited", _VSConverter_mask_dc_cap_en_property_value_edited)
    _VSConverter_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.toggle_frequency_prop(mdl, container_handle)
    
    """
    mdl.set_handler_code(_VSConverter_mask_global_basefreq, "property_value_edited", _VSConverter_mask_global_basefreq_property_value_edited)
    _VSConverter_mask_gen_ts_en_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.enable_time_series_value_edited(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_gen_ts_en, "property_value_edited", _VSConverter_mask_gen_ts_en_property_value_edited)
    _VSConverter_mask_loadshape_name_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_loadshape_name, "property_value_edited", _VSConverter_mask_loadshape_name_property_value_edited)
    _VSConverter_mask_loadshape_from_file_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_loadshape_from_file, "property_value_edited", _VSConverter_mask_loadshape_from_file_property_value_edited)
    _VSConverter_mask_loadshape_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_loadshape, "property_value_edited", _VSConverter_mask_loadshape_property_value_edited)
    _VSConverter_mask_loadshape_int_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_VSConverter_mask_loadshape_int, "property_value_edited", _VSConverter_mask_loadshape_int_property_value_edited)
    _VSConverter_mask_T_mode_property_value_edited = """
    if new_value == "Time":
        mdl.enable_property(mdl.prop(container_handle, "T_Ts"))
    else:
        mdl.disable_property(mdl.prop(container_handle, "T_Ts"))
    
    """
    mdl.set_handler_code(_VSConverter_mask_T_mode, "property_value_edited", _VSConverter_mask_T_mode_property_value_edited)


    ## BUTTON HANDLERS

    _VSConverter_mask_load_loadshape_button_clicked = """
    comp_script_load = return_comp_script_load()
    comp_script_load.load_loadshape(mdl, container_handle)
    
    """
    mdl.set_handler_code(_VSConverter_mask_load_loadshape, "button_clicked", _VSConverter_mask_load_loadshape_button_clicked)


    ## CHANGED HANDLERS

def ports_initialization(mdl, _VSConverter_mask):
    _VSConverter = mdl.get_parent(_VSConverter_mask)


    ## CREATE INITIALIZATION PORTS 

    _VSConverter_A1 = mdl.create_port(
        name="A1",
        parent=_VSConverter,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, -32.0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(9224, 9424)
    )
    _VSConverter_B1 = mdl.create_port(
        name="B1",
        parent=_VSConverter,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, 0.0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(9224, 9504)
    )
    _VSConverter_C1 = mdl.create_port(
        name="C1",
        parent=_VSConverter,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32.0, 32.0),
        rotation="down",
        flip="flip_none",
        hide_name=True,
        position=(9224, 9584)
    )
    _VSConverter_DC_ = mdl.create_port(
        name="DC+",
        parent=_VSConverter,
        label="DC+",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32.0, -32.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7640, 9424)
    )
    _VSConverter_DC_ = mdl.create_port(
        name="DC-",
        parent=_VSConverter,
        label="DC-",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32.0, 32.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7640, 9608)
    )
