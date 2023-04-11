def update_properties(mdl, _Load_mask):
    ## PROPERTIES

    _Load_mask_global_basefreq = mdl.create_property(
        item_handle=_Load_mask,
        name="global_basefreq",
        label="Global base frequency",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General:1",
        unit=""
    )
    _Load_mask_fn = mdl.create_property(
        item_handle=_Load_mask,
        name="fn",
        label="Nominal frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="General:1",
        unit="Hz"
    )
    _Load_mask_conn_type = mdl.create_property(
        item_handle=_Load_mask,
        name="conn_type",
        label="Connection type",
        widget="combo",
        combo_values=['Y', 'Δ'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Load_mask_ground_connected = mdl.create_property(
        item_handle=_Load_mask,
        name="ground_connected",
        label="Ground-connected",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Load_mask_phases = mdl.create_property(
        item_handle=_Load_mask,
        name="phases",
        label="Number of Phases",
        widget="combo",
        combo_values=['3', '1'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Load_mask_Vn_3ph = mdl.create_property(
        item_handle=_Load_mask,
        name="Vn_3ph",
        label="Nominal line voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Load Parameters:2",
        unit="kV"
    )
    _Load_mask_Sn_3ph = mdl.create_property(
        item_handle=_Load_mask,
        name="Sn_3ph",
        label="Total Nominal power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Load Parameters",
        unit="kVA"
    )
    _Load_mask_pf_mode_3ph = mdl.create_property(
        item_handle=_Load_mask,
        name="pf_mode_3ph",
        label="Power factor mode",
        widget="combo",
        combo_values=['Lag', 'Lead', 'Unit'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Load Parameters",
        unit=""
    )
    _Load_mask_pf_3ph = mdl.create_property(
        item_handle=_Load_mask,
        name="pf_3ph",
        label="Power factor",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Load Parameters",
        unit=""
    )
    _Load_mask_pf_3ph_set = mdl.create_property(
        item_handle=_Load_mask,
        name="pf_3ph_set",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_load_model = mdl.create_property(
        item_handle=_Load_mask,
        name="load_model",
        label="Load Model",
        widget="combo",
        combo_values=['Constant Impedance', 'Constant Power', 'Constant Z,I,P'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Load Parameters",
        unit=""
    )
    _Load_mask_zip_vector = mdl.create_property(
        item_handle=_Load_mask,
        name="zip_vector",
        label="Active Z,I,P Weight vector",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Load Parameters",
        unit="Auto-Normalized"
    )
    _Load_mask_zip_vector_Q = mdl.create_property(
        item_handle=_Load_mask,
        name="zip_vector_Q",
        label="Reactive Z,I,P Weight vector",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Load Parameters",
        unit="Auto-Normalized"
    )
    _Load_mask_zip_internal = mdl.create_property(
        item_handle=_Load_mask,
        name="zip_internal",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_zip_internal_Q = mdl.create_property(
        item_handle=_Load_mask,
        name="zip_internal_Q",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_zip_internal_n = mdl.create_property(
        item_handle=_Load_mask,
        name="zip_internal_n",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_zip_internal_n_Q = mdl.create_property(
        item_handle=_Load_mask,
        name="zip_internal_n_Q",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_ZIPV = mdl.create_property(
        item_handle=_Load_mask,
        name="ZIPV",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_Vmaxpu = mdl.create_property(
        item_handle=_Load_mask,
        name="Vmaxpu",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_Vminpu = mdl.create_property(
        item_handle=_Load_mask,
        name="Vminpu",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_model = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_Pow_ref_s = mdl.create_property(
        item_handle=_Load_mask,
        name="Pow_ref_s",
        label="CPL Power reference source",
        widget="combo",
        combo_values=['Fixed', 'External input', 'Time Series'],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="CPL Parameters:3",
        unit=""
    )
    _Load_mask_execution_rate = mdl.create_property(
        item_handle=_Load_mask,
        name="execution_rate",
        label="CPL Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="CPL Parameters",
        unit="s"
    )
    _Load_mask_Tfast = mdl.create_property(
        item_handle=_Load_mask,
        name="Tfast",
        label="CPL Fast Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="CPL Parameters",
        unit="s"
    )
    _Load_mask_CPL_LMT = mdl.create_property(
        item_handle=_Load_mask,
        name="CPL_LMT",
        label="CPL Current limit",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="CPL Parameters",
        unit="pu"
    )
    _Load_mask_v_min_max = mdl.create_property(
        item_handle=_Load_mask,
        name="v_min_max",
        label="Transition to CIL cutoff voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="CPL Parameters",
        unit="[Vmin,Vmax] pu"
    )
    _Load_mask_rate_lmt = mdl.create_property(
        item_handle=_Load_mask,
        name="rate_lmt",
        label="Reference power rate limit",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="CPL Parameters",
        unit="Cycles to reach zero to nominal"
    )
    _Load_mask_zero_seq_remove = mdl.create_property(
        item_handle=_Load_mask,
        name="zero_seq_remove",
        label="Remove zero sequence",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="CPL Parameters",
        unit=""
    )
    _Load_mask_q_gain_k = mdl.create_property(
        item_handle=_Load_mask,
        name="q_gain_k",
        label="CPL Kalman Filter state matrix gain Q",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="CPL Parameters",
        unit=""
    )
    _Load_mask_r_gain_k = mdl.create_property(
        item_handle=_Load_mask,
        name="r_gain_k",
        label="CPL Kalman Filter measurement gain R",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=True,
        tab_name="CPL Parameters",
        unit=""
    )
    _Load_mask_Vn_3ph_CPL = mdl.create_property(
        item_handle=_Load_mask,
        name="Vn_3ph_CPL",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_P_CPL = mdl.create_property(
        item_handle=_Load_mask,
        name="P_CPL",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_Q_CPL = mdl.create_property(
        item_handle=_Load_mask,
        name="Q_CPL",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_kV = mdl.create_property(
        item_handle=_Load_mask,
        name="kV",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_pf = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_conn = mdl.create_property(
        item_handle=_Load_mask,
        name="conn",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_kVA = mdl.create_property(
        item_handle=_Load_mask,
        name="kVA",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_basefreq = mdl.create_property(
        item_handle=_Load_mask,
        name="basefreq",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Load_mask_gen_ts_en = mdl.create_property(
        item_handle=_Load_mask,
        name="gen_ts_en",
        label="Enable time series (forces CPL)",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_load_loadshape = mdl.create_property(
        item_handle=_Load_mask,
        name="load_loadshape",
        label="LoadShape object",
        widget="button",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings:4",
        button_label="Choose",
        unit=""
    )
    _Load_mask_loadshape_name = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape_name",
        label="LoadShape name",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_loadshape_from_file = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape_from_file",
        label="From CSV file",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_useactual = mdl.create_property(
        item_handle=_Load_mask,
        name="useactual",
        label="Actual value",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_loadshape_from_file_path = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape_from_file_path",
        label="LoadShape from file - path",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_loadshape_from_file_column = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape_from_file_column",
        label="LoadShape from file - column",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_loadshape_from_file_header = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape_from_file_header",
        label="LoadShape from file - header",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_loadshape = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape",
        label="LoadShape points",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_loadshape_int = mdl.create_property(
        item_handle=_Load_mask,
        name="loadshape_int",
        label="LoadShape interval",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings:4",
        unit=""
    )
    _Load_mask_S_Ts = mdl.create_property(
        item_handle=_Load_mask,
        name="S_Ts",
        label="Power profile",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings:4",
        unit="pu"
    )
    _Load_mask_Q_Ts = mdl.create_property(
        item_handle=_Load_mask,
        name="Q_Ts",
        label="Reactive power profile",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit="kVAR"
    )
    _Load_mask_T_Ts = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_T_mode = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_S_Ts_mode = mdl.create_property(
        item_handle=_Load_mask,
        name="S_Ts_mode",
        label="Power Profile mode",
        widget="combo",
        combo_values=['Manual input'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit=""
    )
    _Load_mask_timespan = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_T_Ts_internal = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_dssT = mdl.create_property(
        item_handle=_Load_mask,
        name="dssT",
        label="OpenDSS time interval",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit="h"
    )
    _Load_mask_dssnpts = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_T_Ts_max = mdl.create_property(
        item_handle=_Load_mask,
        name="T_Ts_max",
        label="Power profile loop cycle",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=False,
        tab_name="Time Series Settings",
        unit="s"
    )
    _Load_mask_del_Ts = mdl.create_property(
        item_handle=_Load_mask,
        name="del_Ts",
        label="Profile start delay",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=False,
        visible=False,
        tab_name="Time Series Settings",
        unit="s"
    )
    _Load_mask_Slen = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_T_lim_low = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_T_lim_high = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_Ts_switch = mdl.create_property(
        item_handle=_Load_mask,
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
    _Load_mask_enable_monitoring = mdl.create_property(
        item_handle=_Load_mask,
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

    mdl.set_property_value(mdl.prop(_Load_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Load_mask, "fn"), "60")
    mdl.set_property_value(mdl.prop(_Load_mask, "conn_type"), "Y")
    mdl.set_property_value(mdl.prop(_Load_mask, "ground_connected"), "False")
    mdl.set_property_value(mdl.prop(_Load_mask, "phases"), "3")
    mdl.set_property_value(mdl.prop(_Load_mask, "Vn_3ph"), "4.16")
    mdl.set_property_value(mdl.prop(_Load_mask, "Sn_3ph"), "3500")
    mdl.set_property_value(mdl.prop(_Load_mask, "pf_mode_3ph"), "Lag")
    mdl.set_property_value(mdl.prop(_Load_mask, "pf_3ph"), "0.9")
    mdl.set_property_value(mdl.prop(_Load_mask, "pf_3ph_set"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "load_model"), "Constant Impedance")
    mdl.set_property_value(mdl.prop(_Load_mask, "zip_vector"), "[0,0,1]")
    mdl.set_property_value(mdl.prop(_Load_mask, "zip_vector_Q"), "[0,0,1]")
    mdl.set_property_value(mdl.prop(_Load_mask, "zip_internal"), "[0,0,1]")
    mdl.set_property_value(mdl.prop(_Load_mask, "zip_internal_Q"), "[0,0,1]")
    mdl.set_property_value(mdl.prop(_Load_mask, "zip_internal_n"), "[0,0,1]")
    mdl.set_property_value(mdl.prop(_Load_mask, "zip_internal_n_Q"), "[0,0,1]")
    mdl.set_property_value(mdl.prop(_Load_mask, "ZIPV"), "[0,0,1,0,0,1,0]")
    mdl.set_property_value(mdl.prop(_Load_mask, "Vmaxpu"), "1.05")
    mdl.set_property_value(mdl.prop(_Load_mask, "Vminpu"), "0.95")
    mdl.set_property_value(mdl.prop(_Load_mask, "model"), "2")
    mdl.set_property_value(mdl.prop(_Load_mask, "Pow_ref_s"), "Fixed")
    mdl.set_property_value(mdl.prop(_Load_mask, "execution_rate"), "300e-6")
    mdl.set_property_value(mdl.prop(_Load_mask, "Tfast"), "100e-6")
    mdl.set_property_value(mdl.prop(_Load_mask, "CPL_LMT"), "2")
    mdl.set_property_value(mdl.prop(_Load_mask, "v_min_max"), "[0.95,1.05]")
    mdl.set_property_value(mdl.prop(_Load_mask, "rate_lmt"), "1")
    mdl.set_property_value(mdl.prop(_Load_mask, "zero_seq_remove"), "False")
    mdl.set_property_value(mdl.prop(_Load_mask, "q_gain_k"), "0.5")
    mdl.set_property_value(mdl.prop(_Load_mask, "r_gain_k"), "20")
    mdl.set_property_value(mdl.prop(_Load_mask, "Vn_3ph_CPL"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "P_CPL"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "Q_CPL"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "kV"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "pf"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "conn"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "kVA"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "basefreq"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "gen_ts_en"), "True")
    mdl.set_property_value(mdl.prop(_Load_mask, "load_loadshape"), "Choose")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape_name"), "Default")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape_from_file"), "False")
    mdl.set_property_value(mdl.prop(_Load_mask, "useactual"), "False")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape_from_file_path"), "")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape_from_file_column"), "1")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape_from_file_header"), "True")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape"), "[0.4, 0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.7, 0.7, 0.8, 0.7, 0.7, 0.8, 0.8, 0.8, 1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.5]")
    mdl.set_property_value(mdl.prop(_Load_mask, "loadshape_int"), "1")
    mdl.set_property_value(mdl.prop(_Load_mask, "S_Ts"), "[0.2,0.28,0.5,0.32,0.2]")
    mdl.set_property_value(mdl.prop(_Load_mask, "Q_Ts"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "T_Ts"), "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]")
    mdl.set_property_value(mdl.prop(_Load_mask, "T_mode"), "Time")
    mdl.set_property_value(mdl.prop(_Load_mask, "S_Ts_mode"), "Manual input")
    mdl.set_property_value(mdl.prop(_Load_mask, "timespan"), "Daily")
    mdl.set_property_value(mdl.prop(_Load_mask, "T_Ts_internal"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "dssT"), "1")
    mdl.set_property_value(mdl.prop(_Load_mask, "dssnpts"), "5")
    mdl.set_property_value(mdl.prop(_Load_mask, "T_Ts_max"), "10")
    mdl.set_property_value(mdl.prop(_Load_mask, "del_Ts"), "20")
    mdl.set_property_value(mdl.prop(_Load_mask, "Slen"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "T_lim_low"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "T_lim_high"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "Ts_switch"), "0")
    mdl.set_property_value(mdl.prop(_Load_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Load_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.toggle_frequency_prop(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Load_mask_global_basefreq, "property_value_edited", _Load_mask_global_basefreq_property_value_edited)
    _Load_mask_conn_type_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.conn_type_value_edited_fnc(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_Load_mask_conn_type, "property_value_edited", _Load_mask_conn_type_property_value_edited)
    _Load_mask_phases_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.phase_value_edited_fnc(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_Load_mask_phases, "property_value_edited", _Load_mask_phases_property_value_edited)
    _Load_mask_pf_mode_3ph_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.pf_mode_3ph_value_edited(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_Load_mask_pf_mode_3ph, "property_value_edited", _Load_mask_pf_mode_3ph_property_value_edited)
    _Load_mask_load_model_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.load_model_value_edited_fnc(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_Load_mask_load_model, "property_value_edited", _Load_mask_load_model_property_value_edited)
    _Load_mask_gen_ts_en_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    # comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Load_mask_gen_ts_en, "property_value_edited", _Load_mask_gen_ts_en_property_value_edited)
    _Load_mask_loadshape_name_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Load_mask_loadshape_name, "property_value_edited", _Load_mask_loadshape_name_property_value_edited)
    _Load_mask_loadshape_from_file_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Load_mask_loadshape_from_file, "property_value_edited", _Load_mask_loadshape_from_file_property_value_edited)
    _Load_mask_useactual_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Load_mask_useactual, "property_value_edited", _Load_mask_useactual_property_value_edited)
    _Load_mask_loadshape_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Load_mask_loadshape, "property_value_edited", _Load_mask_loadshape_property_value_edited)
    _Load_mask_loadshape_int_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Load_mask_loadshape_int, "property_value_edited", _Load_mask_loadshape_int_property_value_edited)
    _Load_mask_T_mode_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.t_mode_value_edited(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_Load_mask_T_mode, "property_value_edited", _Load_mask_T_mode_property_value_edited)
    _Load_mask_S_Ts_mode_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.s_ts_mode_value_edited(mdl, container_handle, new_value)
    
    """
    mdl.set_handler_code(_Load_mask_S_Ts_mode, "property_value_edited", _Load_mask_S_Ts_mode_property_value_edited)


    ## BUTTON HANDLERS

    _Load_mask_load_loadshape_button_clicked = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.load_loadshape(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Load_mask_load_loadshape, "button_clicked", _Load_mask_load_loadshape_button_clicked)


    ## CHANGED HANDLERS

    _Load_mask_conn_type_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Load_mask_conn_type, "property_value_changed",
                         _Load_mask_conn_type_property_value_changed)

    _Load_mask_ground_connected_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Load_mask_ground_connected, "property_value_changed",
                         _Load_mask_ground_connected_property_value_changed)

    _Load_mask_phases_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Load_mask_phases, "property_value_changed",
                         _Load_mask_phases_property_value_changed)

    _Load_mask_Pow_ref_s_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Load_mask_Pow_ref_s, "property_value_changed",
                         _Load_mask_Pow_ref_s_property_value_changed)

    _Load_mask_S_Ts_mode_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Load_mask_S_Ts_mode, "property_value_changed",
                         _Load_mask_S_Ts_mode_property_value_changed)

    _Load_mask_Ts_switch_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Load_mask_Ts_switch, "property_value_changed",
                         _Load_mask_Ts_switch_property_value_changed)

def ports_initialization(mdl, _Load_mask):
    _Load = mdl.get_parent(_Load_mask)


    ## CREATE INITIALIZATION PORTS 

    _Load_A1 = mdl.create_port(
        name="A1",
        parent=_Load,
        label="",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(-30.0, -32.0),
        rotation="right",
        flip="flip_none",
        hide_name=False,
        position=(7800, 7864)
    )
    _Load_B1 = mdl.create_port(
        name="B1",
        parent=_Load,
        label="",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(0.0, -32.0),
        rotation="right",
        flip="flip_none",
        hide_name=False,
        position=(7920, 7864)
    )
    _Load_C1 = mdl.create_port(
        name="C1",
        parent=_Load,
        label="",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(30.0, -32.0),
        rotation="right",
        flip="flip_none",
        hide_name=False,
        position=(8056, 7864)
    )
    _Load_N1 = mdl.create_port(
        name="N1",
        parent=_Load,
        label="",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(0.0, 30.0),
        rotation="left",
        flip="flip_none",
        hide_name=False,
        position=(7920, 8384)
    )
