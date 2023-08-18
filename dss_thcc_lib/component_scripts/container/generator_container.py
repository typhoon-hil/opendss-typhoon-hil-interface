def update_properties(mdl, _Generator_mask):
    ## PROPERTIES

    _Generator_mask_phases = mdl.create_property(
        item_handle=_Generator_mask,
        name="phases",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_kw = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_kvar = mdl.create_property(
        item_handle=_Generator_mask,
        name="kvar",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_kv = mdl.create_property(
        item_handle=_Generator_mask,
        name="kv",
        label="Nominal line voltage",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General:1",
        unit="kV"
    )
    _Generator_mask_global_basefreq = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_baseFreq = mdl.create_property(
        item_handle=_Generator_mask,
        name="baseFreq",
        label="Nominal Frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="General",
        unit="Hz"
    )
    _Generator_mask_nom_rpm = mdl.create_property(
        item_handle=_Generator_mask,
        name="nom_rpm",
        label="Nominal RPM",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General",
        unit="rpm"
    )
    _Generator_mask_kVA = mdl.create_property(
        item_handle=_Generator_mask,
        name="kVA",
        label="Nominal Apparent Power",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General",
        unit="kVA"
    )
    _Generator_mask_pf = mdl.create_property(
        item_handle=_Generator_mask,
        name="pf",
        label="Nominal Power Factor ",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Generator_mask_model = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_Xd = mdl.create_property(
        item_handle=_Generator_mask,
        name="Xd",
        label="Synchronous Reactance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Circuit Parameters:2",
        unit="pu"
    )
    _Generator_mask_Xdp = mdl.create_property(
        item_handle=_Generator_mask,
        name="Xdp",
        label="Transient Reactance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Circuit Parameters",
        unit="pu"
    )
    _Generator_mask_Xdpp = mdl.create_property(
        item_handle=_Generator_mask,
        name="Xdpp",
        label="Sub-Transient Reactance",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Circuit Parameters",
        unit="pu"
    )
    _Generator_mask_XRdp = mdl.create_property(
        item_handle=_Generator_mask,
        name="XRdp",
        label="Transient X/R ratio",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Circuit Parameters",
        unit=""
    )
    _Generator_mask_H = mdl.create_property(
        item_handle=_Generator_mask,
        name="H",
        label="Mass Constant",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Circuit Parameters",
        unit="s"
    )
    _Generator_mask_J = mdl.create_property(
        item_handle=_Generator_mask,
        name="J",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_rs = mdl.create_property(
        item_handle=_Generator_mask,
        name="rs",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Lls = mdl.create_property(
        item_handle=_Generator_mask,
        name="Lls",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Lmq = mdl.create_property(
        item_handle=_Generator_mask,
        name="Lmq",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Lmd = mdl.create_property(
        item_handle=_Generator_mask,
        name="Lmd",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Lmzq = mdl.create_property(
        item_handle=_Generator_mask,
        name="Lmzq",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Lmzd = mdl.create_property(
        item_handle=_Generator_mask,
        name="Lmzd",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_rkq = mdl.create_property(
        item_handle=_Generator_mask,
        name="rkq",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_rkq2 = mdl.create_property(
        item_handle=_Generator_mask,
        name="rkq2",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_rkd = mdl.create_property(
        item_handle=_Generator_mask,
        name="rkd",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_rfd = mdl.create_property(
        item_handle=_Generator_mask,
        name="rfd",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Llkq = mdl.create_property(
        item_handle=_Generator_mask,
        name="Llkq",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Llkq2 = mdl.create_property(
        item_handle=_Generator_mask,
        name="Llkq2",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Llkd = mdl.create_property(
        item_handle=_Generator_mask,
        name="Llkd",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Llfd = mdl.create_property(
        item_handle=_Generator_mask,
        name="Llfd",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_PP = mdl.create_property(
        item_handle=_Generator_mask,
        name="PP",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_w_base = mdl.create_property(
        item_handle=_Generator_mask,
        name="w_base",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_T_base = mdl.create_property(
        item_handle=_Generator_mask,
        name="T_base",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_ws = mdl.create_property(
        item_handle=_Generator_mask,
        name="ws",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_ws_inv = mdl.create_property(
        item_handle=_Generator_mask,
        name="ws_inv",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Z_base = mdl.create_property(
        item_handle=_Generator_mask,
        name="Z_base",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_G_mod = mdl.create_property(
        item_handle=_Generator_mask,
        name="G_mod",
        label="Generator model",
        widget="combo",
        combo_values=['Constant kW', 'Constant admittance', 'Constant kW, Constant kV', 'Constant kW, Fixed Q', 'Constant kW, Fixed Q (constant reactance)'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="OpenDSS model setting:3",
        unit=""
    )
    _Generator_mask_execution_rate = mdl.create_property(
        item_handle=_Generator_mask,
        name="execution_rate",
        label="Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Execution rate:4",
        unit="s"
    )
    _Generator_mask_dA = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA11 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA11",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA12 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA12",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA13 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA13",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA14 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA14",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA21 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA21",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA22 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA22",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA23 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA23",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA24 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA24",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA31 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA31",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA32 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA32",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA33 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA33",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA34 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA34",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA41 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA41",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA42 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA42",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA43 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA43",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dA44 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dA44",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB11 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB11",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB12 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB12",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB13 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB13",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB21 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB21",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB22 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB22",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB23 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB23",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB31 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB31",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB32 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB32",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB33 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB33",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB41 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB41",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB42 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB42",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_dB43 = mdl.create_property(
        item_handle=_Generator_mask,
        name="dB43",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_Init_En = mdl.create_property(
        item_handle=_Generator_mask,
        name="Init_En",
        label="Initialization",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Initialization:5",
        unit=""
    )
    _Generator_mask_Init_switch = mdl.create_property(
        item_handle=_Generator_mask,
        name="Init_switch",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Generator_mask_V_ph_init = mdl.create_property(
        item_handle=_Generator_mask,
        name="V_ph_init",
        label="Initial phase voltage magnitude",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Initialization",
        unit="kV"
    )
    _Generator_mask_thet_ph_init = mdl.create_property(
        item_handle=_Generator_mask,
        name="thet_ph_init",
        label="Initial phase voltage angle",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Initialization",
        unit="Rad"
    )
    _Generator_mask_V2M_t = mdl.create_property(
        item_handle=_Generator_mask,
        name="V2M_t",
        label="Transition time from V Source to Machine",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Initialization",
        unit="s"
    )
    _Generator_mask_Mech_En = mdl.create_property(
        item_handle=_Generator_mask,
        name="Mech_En",
        label="Mechanical system enable time",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Initialization",
        unit="s"
    )
    _Generator_mask_gen_ts_en = mdl.create_property(
        item_handle=_Generator_mask,
        name="gen_ts_en",
        label="Enable time series (override gen control)",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _Generator_mask_load_loadshape = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_loadshape_name = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_loadshape_from_file = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_loadshape_from_file_path = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_loadshape_from_file_header = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_loadshape_from_file_column = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_useactual = mdl.create_property(
        item_handle=_Generator_mask,
        name="useactual",
        label="Actual gen value",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Time Series Settings",
        unit=""
    )
    _Generator_mask_loadshape = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_loadshape_int = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_gen_ts_en_bit = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_T_Ts = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_T_mode = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_S_Ts = mdl.create_property(
        item_handle=_Generator_mask,
        name="S_Ts",
        label="Power profile",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Time Series Settings",
        unit="pu"
    )
    _Generator_mask_Q_Ts = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_S_Ts_mode = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_timespan = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_T_Ts_internal = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_dssT = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_dssnpts = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_T_Ts_max = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_del_Ts = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_Slen = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_T_lim_low = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_T_lim_high = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_Ts_switch = mdl.create_property(
        item_handle=_Generator_mask,
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
    _Generator_mask_enable_monitoring = mdl.create_property(
        item_handle=_Generator_mask,
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

    mdl.set_property_value(mdl.prop(_Generator_mask, "phases"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "kw"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "kvar"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "kv"), "1")
    mdl.set_property_value(mdl.prop(_Generator_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Generator_mask, "baseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Generator_mask, "nom_rpm"), "1800")
    mdl.set_property_value(mdl.prop(_Generator_mask, "kVA"), "1000")
    mdl.set_property_value(mdl.prop(_Generator_mask, "pf"), ".96")
    mdl.set_property_value(mdl.prop(_Generator_mask, "model"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Xd"), "1")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Xdp"), "0.3")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Xdpp"), ".2")
    mdl.set_property_value(mdl.prop(_Generator_mask, "XRdp"), "50")
    mdl.set_property_value(mdl.prop(_Generator_mask, "H"), "0.5")
    mdl.set_property_value(mdl.prop(_Generator_mask, "J"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "rs"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Lls"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Lmq"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Lmd"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Lmzq"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Lmzd"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "rkq"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "rkq2"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "rkd"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "rfd"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Llkq"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Llkq2"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Llkd"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Llfd"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "PP"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "w_base"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_base"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "ws"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "ws_inv"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Z_base"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "G_mod"), "Constant kW, Fixed Q")
    mdl.set_property_value(mdl.prop(_Generator_mask, "execution_rate"), "100e-6")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA11"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA12"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA13"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA14"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA21"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA22"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA23"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA24"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA31"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA32"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA33"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA34"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA41"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA42"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA43"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dA44"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB11"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB12"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB13"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB21"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB22"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB23"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB31"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB32"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB33"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB41"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB42"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dB43"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Init_En"), "True")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Init_switch"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "V_ph_init"), "0.581")
    mdl.set_property_value(mdl.prop(_Generator_mask, "thet_ph_init"), "-1.58")
    mdl.set_property_value(mdl.prop(_Generator_mask, "V2M_t"), "5")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Mech_En"), "9")
    mdl.set_property_value(mdl.prop(_Generator_mask, "gen_ts_en"), "True")
    mdl.set_property_value(mdl.prop(_Generator_mask, "load_loadshape"), "Choose")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape_name"), "Default")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape_from_file"), "False")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape_from_file_path"), "")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape_from_file_header"), "True")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape_from_file_column"), "1")
    mdl.set_property_value(mdl.prop(_Generator_mask, "useactual"), "False")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape"), "[0.4, 0.3, 0.2, 0.2, 0.2, 0.2, 0.3, 0.5, 0.6, 0.7, 0.7, 0.8, 0.7, 0.7, 0.8, 0.8, 0.8, 1.0, 1.0, 1.0, 1.0, 0.9, 0.7, 0.5]")
    mdl.set_property_value(mdl.prop(_Generator_mask, "loadshape_int"), "1")
    mdl.set_property_value(mdl.prop(_Generator_mask, "gen_ts_en_bit"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_Ts"), "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_mode"), "Time")
    mdl.set_property_value(mdl.prop(_Generator_mask, "S_Ts"), "[0.2,0.28,0.5,0.32,0.2]")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Q_Ts"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "S_Ts_mode"), "Manual input")
    mdl.set_property_value(mdl.prop(_Generator_mask, "timespan"), "Daily")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_Ts_internal"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dssT"), "1")
    mdl.set_property_value(mdl.prop(_Generator_mask, "dssnpts"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_Ts_max"), "20")
    mdl.set_property_value(mdl.prop(_Generator_mask, "del_Ts"), "10")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Slen"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_lim_low"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "T_lim_high"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "Ts_switch"), "0")
    mdl.set_property_value(mdl.prop(_Generator_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Generator_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Generator_mask_global_basefreq, "property_value_edited", _Generator_mask_global_basefreq_property_value_edited)
    _Generator_mask_gen_ts_en_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Generator_mask_gen_ts_en, "property_value_edited", _Generator_mask_gen_ts_en_property_value_edited)
    _Generator_mask_loadshape_name_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Generator_mask_loadshape_name, "property_value_edited", _Generator_mask_loadshape_name_property_value_edited)
    _Generator_mask_loadshape_from_file_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Generator_mask_loadshape_from_file, "property_value_edited", _Generator_mask_loadshape_from_file_property_value_edited)
    _Generator_mask_useactual_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Generator_mask_useactual, "property_value_edited", _Generator_mask_useactual_property_value_edited)
    _Generator_mask_loadshape_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Generator_mask_loadshape, "property_value_edited", _Generator_mask_loadshape_property_value_edited)
    _Generator_mask_loadshape_int_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Generator_mask_loadshape_int, "property_value_edited", _Generator_mask_loadshape_int_property_value_edited)
    _Generator_mask_T_mode_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Generator_mask_T_mode, "property_value_edited", _Generator_mask_T_mode_property_value_edited)
    _Generator_mask_S_Ts_mode_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Generator_mask_S_Ts_mode, "property_value_edited", _Generator_mask_S_Ts_mode_property_value_edited)


    ## BUTTON HANDLERS

    _Generator_mask_load_loadshape_button_clicked = """
    comp_script_load = return_comp_script_load()
    comp_script_load.load_loadshape(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Generator_mask_load_loadshape, "button_clicked", _Generator_mask_load_loadshape_button_clicked)


    ## CHANGED HANDLERS

    _Generator_mask_S_Ts_mode_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Generator_mask_S_Ts_mode, "property_value_changed",
                         _Generator_mask_S_Ts_mode_property_value_changed)

    _Generator_mask_gen_ts_en_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Generator_mask_gen_ts_en, "property_value_changed",
                         _Generator_mask_gen_ts_en_property_value_changed)

    _Generator_mask_Init_En_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Generator_mask_Init_En, "property_value_changed",
                         _Generator_mask_Init_En_property_value_changed)

def ports_initialization(mdl, _Generator_mask):
    _Generator = mdl.get_parent(_Generator_mask)


    ## CREATE INITIALIZATION PORTS 

    _Generator_A1 = mdl.create_port(
        name="A1",
        parent=_Generator,
        label="A1",
        kind="pe",
        dimension=(1,),
        terminal_position=(48.0, -32.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(5176, 8280)
    )
    _Generator_B1 = mdl.create_port(
        name="B1",
        parent=_Generator,
        label="B1",
        kind="pe",
        dimension=(1,),
        terminal_position=(48.0, 0.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(5176, 8376)
    )
    _Generator_C1 = mdl.create_port(
        name="C1",
        parent=_Generator,
        label="C1",
        kind="pe",
        dimension=(1,),
        terminal_position=(48.0, 32.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(5176, 8472)
    )
    _Generator_Vfd_in = mdl.create_port(
        name="Vfd_in",
        parent=_Generator,
        label="Vfd",
        kind="sp",
        direction="in",
        dimension=(1,),
        terminal_position=(-32.0, -80.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(4176, 7712)
    )
    _Generator_Tm_in = mdl.create_port(
        name="Tm_in",
        parent=_Generator,
        label="Tm",
        kind="sp",
        direction="in",
        dimension=(1,),
        terminal_position=(-16.0, -80.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(4176, 7768)
    )
    _Generator_meas = mdl.create_port(
        name="meas",
        parent=_Generator,
        label="meas",
        kind="sp",
        direction="out",
        dimension=(1,),
        terminal_position=(32.0, -80.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(6848, 8040)
    )
    _Generator_ctrl = mdl.create_port(
        name="ctrl",
        parent=_Generator,
        label="ctrl",
        kind="sp",
        direction="out",
        dimension=(1,),
        terminal_position=(16.0, -80.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(6840, 8624)
    )
    _Generator_Vfd0 = mdl.create_port(
        name="Vfd0",
        parent=_Generator,
        label="Vfd0",
        kind="sp",
        direction="out",
        dimension=(1,),
        terminal_position=(-48.0, 64.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(5968, 7640)
    )
    _Generator_Tm0 = mdl.create_port(
        name="Tm0",
        parent=_Generator,
        label="Tm0",
        kind="sp",
        direction="out",
        dimension=(1,),
        terminal_position=(-48.0, 48.0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(5936, 7824)
    )
