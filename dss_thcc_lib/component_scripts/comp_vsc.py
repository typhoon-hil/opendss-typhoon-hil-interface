import dss_thcc_lib.component_scripts.util as util
import importlib
import json


def get_sld_conversion_info(mdl, mask_handle, props_state):

    multiline_ports_1 = ["A1", "B1", "C1"]

    port_config_dict = {
        "SLD1": {
            "multiline_ports": multiline_ports_1,
            "side": "right",
            "bus_terminal_position": (32, 0),
            "hide_name": True,
        },
    }
    #
    # Tag info
    #
    tag_config_dict = {}

    #
    # Terminal positions
    #
    terminal_positions = {
        "A1": (32, -32),
        "B1": (32, 0),
        "C1": (32, 32),
    }

    return port_config_dict, tag_config_dict, terminal_positions


def inv_control_mode_value_edited(mdl, container_handle, new_value):
    if new_value == "PQ":
        prop_nominal_list = ['V_ref_str', 'vdc_ref_str', 'fs_ref_str']
        prop_external_list = []
        prop_disable_list = ["V_ref_str", "V_kp", "V_ki", "vdc_ref_str", "vdc_kp", "vdc_ki", "fs_ref_str"]
        prop_enable_list = ["Q_ref_str", "Q_kp", "Q_ki", "P_ref_str", "P_kp", "P_ki"]
    elif new_value == "PV":
        prop_nominal_list = ['Q_ref_str', 'vdc_ref_str', 'fs_ref_str']
        prop_external_list = []
        prop_disable_list = ["Q_ref_str", "Q_kp", "Q_ki", "vdc_ref_str", "vdc_kp", "vdc_ki", "fs_ref_str"]
        prop_enable_list = ["V_ref_str", "V_kp", "V_ki", "P_ref_str", "P_kp", "P_ki"]
    elif new_value == "Vdc-Vac":
        prop_nominal_list = ['P_ref_str', 'Q_ref_str', 'fs_ref_str']
        prop_external_list = []
        prop_disable_list = ["P_ref_str", "P_kp", "P_ki", "Q_ref_str", "Q_kp", "Q_ki", "fs_ref_str"]
        prop_enable_list = ["V_ref_str", "V_kp", "V_ki", "vdc_ref_str", "vdc_kp", "vdc_ki"]
    elif new_value == "Vdc-Q":
        prop_nominal_list = ['P_ref_str', 'V_ref_str', 'fs_ref_str']
        prop_external_list = []
        prop_disable_list = ["P_ref_str", "P_kp", "P_ki", "V_ref_str", "V_kp", "V_ki", "fs_ref_str"]
        prop_enable_list = ["Q_ref_str", "Q_kp", "Q_ki", "vdc_ref_str", "vdc_kp", "vdc_ki"]
    elif new_value == "Grid Forming":
        prop_nominal_list = ['P_ref_str', 'Q_ref_str', 'vdc_ref_str']
        prop_external_list = []
        prop_disable_list = ["P_ref_str", "P_kp", "P_ki", "Q_ref_str", "Q_kp", "Q_ki",
                             "vdc_ref_str", "vdc_kp", "vdc_ki"]
        prop_enable_list = ["V_ref_str", "V_kp", "V_ki", "fs_ref_str"]
    else:  # if new_value == "External Control":
        prop_nominal_list = []
        prop_external_list = ['P_ref_str', 'Q_ref_str', 'V_ref_str', 'vdc_ref_str', 'fs_ref_str']
        prop_disable_list = []
        prop_enable_list = ["P_ref_str", "P_kp", "P_ki", "Q_ref_str", "Q_kp", "Q_ki", "fs_ref_str", "V_ref_str",
                            "V_kp", "V_ki", "vdc_ref_str", "vdc_kp", "vdc_ki"]

    for prop in prop_nominal_list:
        mdl.set_property_disp_value(mdl.prop(container_handle, prop), "Converter nominal")

    for prop in prop_external_list:
        mdl.set_property_disp_value(mdl.prop(container_handle, prop), "External input")

    for prop in prop_disable_list:
        mdl.disable_property(mdl.prop(container_handle, prop))

    for prop in prop_enable_list:
        mdl.enable_property(mdl.prop(container_handle, prop))


def define_icon(mdl, mask_handle):

    all_ports = mdl.get_items(parent=mdl.get_parent(mask_handle), item_type="port")
    if any(mdl.get_connectable_kind(port) == "sp" for port in all_ports):
        mdl.set_component_icon_image(mask_handle, 'images/vsconverter_sp_ports.svg')
    else:
        mdl.set_component_icon_image(mask_handle, 'images/vsconverter.svg')


def toggle_frequency_prop(mdl, mask_handle, init=False):
    frequency_prop = mdl.prop(mask_handle, "Fs")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_disp_value(global_frequency_prop)

    if use_global:
        if "simdss_basefreq" in mdl.get_ns_vars():
            mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            mdl.hide_property(frequency_prop)
        else:
            mdl.set_property_disp_value(global_frequency_prop, False)
            mdl.info("Add a SimDSS component to define the global frequency value.")
    else:
        mdl.show_property(frequency_prop)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    pass


def update_frequency_property(mdl, mask_handle, init=False):

    frequency_prop = mdl.prop(mask_handle, "Fs")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_value(global_frequency_prop)

    if init:
        mdl.hide_property(frequency_prop)
    else:
        if use_global:
            if "simdss_basefreq" in mdl.get_ns_vars():
                mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            else:
                mdl.set_property_value(global_frequency_prop, False)
        toggle_frequency_prop(mdl, mask_handle, init)


def set_timeseries_switch(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)

    ref_pos = (5600, 8504)

    if new_value is True:
        ts_switch = mdl.get_item("Ts_switch", parent=comp_handle, item_type="component")
        if not ts_switch:
            ts_switch = mdl.create_component("Constant", parent=comp_handle,
                                             name="Ts_switch", position=(ref_pos[0], ref_pos[1]))
            mdl.set_property_value(mdl.prop(ts_switch, "value"), "Ts_switch")
            mdl.set_property_value(mdl.prop(ts_switch, "execution_rate"), "execution_rate")

        port_t = mdl.get_item("T", parent=comp_handle, item_type="port")
        if not port_t:
            port_t = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                     terminal_position=(-10, -87), label="T_series",
                                     position=(ref_pos[0], ref_pos[1] + 128))
        else:
            mdl.set_port_properties(port_t, terminal_position=(50, 0))

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle, item_type="component")
        if not signal_switch:
            signal_switch = mdl.create_component("Signal switch", parent=comp_handle,
                                                 name="Signal switch", position=(ref_pos[0] + 256, ref_pos[1] + 112))
            mdl.set_property_value(mdl.prop(signal_switch, "criterion"), "ctrl >= threshold")
            mdl.set_property_value(mdl.prop(signal_switch, "threshold"), 0.5)

        round_comp = mdl.get_item("Round", parent=comp_handle, item_type="component")
        if not round_comp:
            round_comp = mdl.create_component("Round", parent=comp_handle,
                                              name="Round", position=(ref_pos[0] + 128, ref_pos[1] + 128))
            mdl.set_property_value(mdl.prop(round_comp, "round_fn"), "floor")

        limit = mdl.get_item("Limit", parent=comp_handle, item_type="component")
        if not limit:
            limit = mdl.create_component("Limit", parent=comp_handle,
                                         name="Limit", position=(ref_pos[0] + 376, ref_pos[1] + 112))
            mdl.set_property_value(mdl.prop(limit, "upper_limit"), "T_lim_high")
            mdl.set_property_value(mdl.prop(limit, "lower_limit"), "T_lim_low")

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        if not ts_module:
            ts_module = mdl.create_component("OpenDSS/TS_module", parent=comp_handle,
                                             name="TS_module", position=(ref_pos[0] + 456, ref_pos[1] + 48),
                                             rotation="left")
            mdl.set_property_value(mdl.prop(ts_module, "Texec"), "execution_rate")
            mdl.set_property_value(mdl.prop(ts_module, "P_nom"), "Sinv")
            mdl.set_property_value(mdl.prop(ts_module, "Q_nom"), "Qinv")

        conn_term_list = [(mdl.term(ts_switch, "out"), mdl.term(signal_switch, "in2")),
                          (port_t, mdl.term(signal_switch, "in")),
                          (port_t, mdl.term(round_comp, "in")),
                          (mdl.term(round_comp, "out"), mdl.term(signal_switch, "in1")),
                          (mdl.term(signal_switch, "out"), mdl.term(limit, "in")),
                          (mdl.term(limit, "out"), mdl.term(ts_module, "T"))]
        for conn_term in conn_term_list:
            if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
                mdl.create_connection(conn_term[0], conn_term[1])

    else:
        ts_switch = mdl.get_item("Ts_switch", parent=comp_handle, item_type="component")
        if ts_switch:
            mdl.delete_item(ts_switch)

        port_t = mdl.get_item("T", parent=comp_handle, item_type="port")
        if port_t:
            mdl.delete_item(port_t)

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle, item_type="component")
        if signal_switch:
            mdl.delete_item(signal_switch)

        round_comp = mdl.get_item("Round", parent=comp_handle, item_type="component")
        if round_comp:
            mdl.delete_item(round_comp)

        limit = mdl.get_item("Limit", parent=comp_handle, item_type="component")
        if limit:
            mdl.delete_item(limit)

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        if ts_module:
            mdl.delete_item(ts_module)

    mdl.refresh_icon(mask_handle)

    return port_t


def set_control_mode(mdl, container_handle, new_value):

    comp_handle = mdl.get_sub_level_handle(container_handle)

    mode_ext = mdl.get_item("mode", parent=comp_handle, item_type="port")
    mode_inp = mdl.get_item("Gain32", parent=comp_handle, item_type="component")
    term_mode = mdl.get_item("Termination5", parent=comp_handle, item_type="component")
    mode_int = mdl.get_item("From25", parent=comp_handle, item_type="tag")

    if new_value == "External Control":
        if len(mdl.find_connections(mode_int, mdl.term(mode_inp, "in"))) > 0:
            for conn in mdl.find_connections(mode_int, mdl.term(mode_inp, "in")):
                mdl.delete_item(conn)

        if not term_mode:
            term_mode = mdl.create_component("Termination", parent=comp_handle,
                                             name="Termination5", position=(7047, 9200),
                                             hide_name=True)
        if len(mdl.find_connections(mdl.term(term_mode, "in"), mode_int)) == 0:
            mdl.create_connection(mdl.term(term_mode, "in"), mode_int)

        if not mode_ext:
            mode_ext = mdl.create_port(parent=comp_handle, name="mode", direction="in", kind="sp",
                                       terminal_position=(-16, 80),
                                       position=(7120, 9201))
        if len(mdl.find_connections(mdl.term(mode_inp, "in"), mode_ext)) == 0:
            mdl.create_connection(mdl.term(mode_inp, "in"), mode_ext)
    else:
        if mode_ext:
            mdl.delete_item(mode_ext)
        if term_mode:
            mdl.delete_item(term_mode)
        if len(mdl.find_connections(mode_int, mdl.term(mode_inp, "in"))) == 0:
            mdl.create_connection(mdl.term(mode_inp, "in"), mode_int)

    mdl.refresh_icon(container_handle)


def set_external_input(mdl, container_handle, prop_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    input_dict = {"P_ref_str": {"external_port": {"name": "P_set",
                                                  "position": (6642, 8348),
                                                  "terminal_position": (-16, -80)},
                                "input_comp": {"name": "Sum9"},
                                "input_term": {"name": "Termination1",
                                               "position": (6567, 8352),
                                               "comp_type": "Termination"},
                                "input_tag": {"name": "From11"}},
                  "Q_ref_str": {"external_port": {"name": "Q_set",
                                                  "position": (6504, 8753),
                                                  "terminal_position": (0, -80)},
                                "input_comp": {"name": "Sum7"},
                                "input_term": {"name": "Termination2",
                                               "position": (6424, 8751),
                                               "comp_type": "Termination"},
                                "input_tag": {"name": "From10"}},
                  "V_ref_str": {"external_port": {"name": "V_set",
                                                  "position": (6450, 8926),
                                                  "terminal_position": (16, -80)},
                                "input_comp": {"name": "Sum11"},
                                "input_term": {"name": "Termination3",
                                               "position": (6376, 8930),
                                               "comp_type": "Termination"},
                                "input_tag": {"name": "From15"}},
                  "vdc_ref_str": {"external_port": {"name": "vdc_set",
                                                    "position": (6695, 8660),
                                                    "terminal_position": (0, 80)},
                                  "input_comp": {"name": "Gain30"},
                                  "input_term": {"name": "Termination4",
                                                 "position": (6621, 8663),
                                                 "comp_type": "Termination"},
                                  "input_tag": {"name": "From22"}},
                  "fs_ref_str": {"external_port": {"name": "fs_set",
                                                   "position": (6893, 8248),
                                                   "terminal_position": (16, 80)},
                                 "input_comp": {"name": "Gain33"},
                                 "input_term": {"name": "Termination8",
                                                "position": (6767, 8247),
                                                "comp_type": "Termination"},
                                 "input_tag": {"name": "From44"}},
                  }

    prop_name = mdl.get_property_type_attributes(prop_handle)["name"]

    external_port = mdl.get_item(input_dict[prop_name]["external_port"]["name"],
                                 parent=comp_handle, item_type="port")
    input_comp = mdl.get_item(input_dict[prop_name]["input_comp"]["name"],
                              parent=comp_handle, item_type="component")
    input_term = mdl.get_item(input_dict[prop_name]["input_term"]["name"],
                              parent=comp_handle, item_type="component")
    input_tag = mdl.get_item(input_dict[prop_name]["input_tag"]["name"],
                             parent=comp_handle, item_type="tag")

    if new_value == "External input":
        if len(mdl.find_connections(input_tag, mdl.term(input_comp, "in"))) > 0:
            for conn in mdl.find_connections(input_tag, mdl.term(input_comp, "in")):
                mdl.delete_item(conn)

        if not input_term:
            input_term = mdl.create_component(input_dict[prop_name]["input_term"]["comp_type"], parent=comp_handle,
                                              name=input_dict[prop_name]["input_term"]["name"],
                                              position=input_dict[prop_name]["input_term"]["position"],
                                              hide_name=True)
            mdl.create_connection(mdl.term(input_term, "in"), input_tag)

        if not external_port:
            external_port = mdl.create_port(parent=comp_handle, name=input_dict[prop_name]["external_port"]["name"],
                                            direction="in", kind="sp",
                                            terminal_position=input_dict[prop_name]["external_port"]["terminal_"
                                                                                                     "position"],
                                            position=input_dict[prop_name]["external_port"]["position"])
            mdl.create_connection(mdl.term(input_comp, "in"), external_port)
    elif new_value == "Converter nominal":

        if external_port:
            mdl.delete_item(external_port)
        if input_term:
            mdl.delete_item(input_term)

        if len(mdl.find_connections(input_tag, mdl.term(input_comp, "in"))) == 0:
            mdl.create_connection(mdl.term(input_comp, "in"), input_tag)

    mdl.refresh_icon(container_handle)


def enable_time_series(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    pref_in = mdl.get_item("Constant22", parent=comp_handle, item_type="component")
    qref_in = mdl.get_item("Constant23", parent=comp_handle, item_type="component")
    pref_tag = mdl.get_item("Goto10", parent=comp_handle, item_type="tag")
    qref_tag = mdl.get_item("Goto11", parent=comp_handle, item_type="tag")
    pref_term = mdl.get_item("pref_term", parent=comp_handle, item_type="component")
    qref_term = mdl.get_item("qref_term", parent=comp_handle, item_type="component")

    pos_ref = (6112, 8384)

    if new_value:

        set_timeseries_switch(mdl, container_handle, True)

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")

        if len(mdl.find_connections(mdl.term(pref_in, "out"), pref_tag)) > 0:
            for conn in mdl.find_connections(mdl.term(pref_in, "out"), pref_tag):
                mdl.delete_item(conn)
        if len(mdl.find_connections(mdl.term(qref_in, "out"), qref_tag)) > 0:
            for conn in mdl.find_connections(mdl.term(qref_in, "out"), qref_tag):
                mdl.delete_item(conn)

        if len(mdl.find_connections(mdl.term(ts_module, "P"), pref_tag)) == 0:
            mdl.create_connection(mdl.term(ts_module, "P"), pref_tag)
        if len(mdl.find_connections(mdl.term(ts_module, "Q"), qref_tag)) == 0:
            mdl.create_connection(mdl.term(ts_module, "Q"), qref_tag)

        mdl.set_position(pref_tag, pos_ref)
        mdl.set_position(qref_tag, (pos_ref[0], pos_ref[1] + 40))

        if not pref_term:
            pref_term = mdl.create_component("Termination", name="pref_term", position=(pos_ref[0] + 216, pos_ref[1]),
                                             parent=comp_handle, hide_name=True)

        if not qref_term:
            qref_term = mdl.create_component("Termination", name="qref_term",
                                             position=(pos_ref[0] + 216, pos_ref[1] + 40),
                                             parent=comp_handle, hide_name=True)

        if len(mdl.find_connections(mdl.term(pref_in, "out"), mdl.term(pref_term, "in"))) == 0:
            mdl.create_connection(mdl.term(pref_in, "out"), mdl.term(pref_term, "in"))
        if len(mdl.find_connections(mdl.term(qref_in, "out"), mdl.term(qref_term, "in"))) == 0:
            mdl.create_connection(mdl.term(qref_in, "out"), mdl.term(qref_term, "in"))

    else:
        set_timeseries_switch(mdl, container_handle, False)

        if pref_term:
            mdl.delete_item(pref_term)
        if qref_term:
            mdl.delete_item(qref_term)

        if len(mdl.find_connections(mdl.term(pref_in, "out"), pref_tag)) == 0:
            mdl.create_connection(mdl.term(pref_in, "out"), pref_tag)
        if len(mdl.find_connections(mdl.term(qref_in, "out"), qref_tag)) == 0:
            mdl.create_connection(mdl.term(qref_in, "out"), qref_tag)

        mdl.set_position(pref_tag, (pos_ref[0] + 216, pos_ref[1]))
        mdl.set_position(qref_tag, (pos_ref[0] + 216, pos_ref[1] + 40))


def place_internal_dc_capacitor(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    if new_value:
        c_dc = mdl.get_item("dccap", parent=comp_handle, item_type="component")
        dc_p_port = mdl.get_item("Junction121", parent=comp_handle, item_type="junction")
        dc_n_port = mdl.get_item("Junction120", parent=comp_handle, item_type="junction")
        if not c_dc:
            c_dc = mdl.create_component("Capacitor", parent=comp_handle, name="dccap", position=(7709, 9516),
                                        rotation="right")
            mdl.set_property_value(mdl.prop(c_dc, "capacitance"), "dc_cap")
            mdl.set_property_value(mdl.prop(c_dc, "initial_voltage"), "1000*vdc_set")
            mdl.create_connection(mdl.term(c_dc, "p_node"), dc_p_port, name="dcConnp")
            mdl.create_connection(mdl.term(c_dc, "n_node"), dc_n_port, name="dcConnn")

    else:
        c_dc = mdl.get_item("dccap", parent=comp_handle, item_type="component")
        if c_dc:
            mdl.delete_item(c_dc)


def enable_time_series_value_edited(mdl, container_handle, new_value):
    prop_list = ["ctrl_mode_str",
                 "P_ref_str",
                 "Q_ref_str",
                 "V_ref_str",
                 "vdc_ref_str",
                 "fs_ref_str"]

    if new_value:
        for prop_name in prop_list:
            if prop_name != "ctrl_mode_str":
                mdl.set_property_value(mdl.prop(container_handle, prop_name), "Converter nominal")
            else:
                mdl.set_property_value(mdl.prop(container_handle, prop_name), "PQ")

            mdl.disable_property(mdl.prop(container_handle, prop_name))

    else:
        for prop_name in prop_list:
            if prop_name in ["ctrl_mode_str", "P_ref_str", "Q_ref_str"]:
                mdl.enable_property(mdl.prop(container_handle, prop_name))


def dc_link_cap_value_edited(mdl, container_handle, new_value):
    if new_value is False:
        mdl.disable_property(mdl.prop(container_handle, "dc_cap"))
    elif new_value is True:
        mdl.enable_property(mdl.prop(container_handle, "dc_cap"))


def vsc_pre_compile_function(mdl, item_handle, prop_dict):

    pu = 1
    angle = 0
    r0 = 0.001
    r1 = 0.001
    x0 = 0.001
    x1 = 0.001

    phases = 3
    kv = prop_dict["vac_set"]
    kw = prop_dict["Sinv"]
    basefreq = prop_dict["Fs"]
    frequency = prop_dict["Fs"]
    basekv = kv

    if prop_dict["Qinv"] >= 0:
        pf = prop_dict["Sinv"] / ((prop_dict["Sinv"] ** 2 + prop_dict["Qinv"] ** 2) ** 0.5)
    else:
        pf = -prop_dict["Sinv"] / ((prop_dict["Sinv"] ** 2 + prop_dict["Qinv"] ** 2) ** 0.5)

    if prop_dict["ctrl_mode_str"] == "PQ":
        ctrl_mode_int = 1
        ext_mode = 0
        model = 1
    elif prop_dict["ctrl_mode_str"] == "PV":
        ctrl_mode_int = 0
        ext_mode = 0
        model = 3
    elif prop_dict["ctrl_mode_str"] == "Vdc-Vac":
        ctrl_mode_int = 2
        ext_mode = 0
        model = 3
    elif prop_dict["ctrl_mode_str"] == "Vdc-Q":
        ctrl_mode_int = 3
        ext_mode = 0
        model = 1
    elif prop_dict["ctrl_mode_str"] == "Grid Forming":
        ctrl_mode_int = 4
        ext_mode = 0
        model = 2
    elif prop_dict["ctrl_mode_str"] == "External Control":
        ctrl_mode_int = -1
        ext_mode = 1
        model = 1
    else:
        ctrl_mode_int = 0
        ext_mode = 0
        model = 1

    s_ts = prop_dict["loadshape"]
    dss_t = prop_dict["loadshape_int"]
    slen = len(s_ts)

    dssnpts = len(s_ts)

    if prop_dict["T_mode"] == "Time":
        t_ts_internal = [t_val for t_val in prop_dict["T_Ts"]]
        ts_switch = 1
    else:  # if prop_dict["T_mode"] == "Loadshape index":
        t_ts_internal = [x for x in range(slen)]
        ts_switch = 0

    t_lim_low = t_ts_internal[0]
    t_lim_high = t_ts_internal[- 1]

    mdl.set_property_value(mdl.prop(item_handle, "ctrl_mode_int"), ctrl_mode_int)
    mdl.set_property_value(mdl.prop(item_handle, "ext_mode"), ext_mode)

    mdl.set_property_value(mdl.prop(item_handle, "Phases"), phases)
    mdl.set_property_value(mdl.prop(item_handle, "kv"), kv)
    mdl.set_property_value(mdl.prop(item_handle, "kw"), kw)
    mdl.set_property_value(mdl.prop(item_handle, "pf"), pf)
    mdl.set_property_value(mdl.prop(item_handle, "model"), model)
    mdl.set_property_value(mdl.prop(item_handle, "baseFreq"), basefreq)

    mdl.set_property_value(mdl.prop(item_handle, "r0"), r0)
    mdl.set_property_value(mdl.prop(item_handle, "r1"), r1)
    mdl.set_property_value(mdl.prop(item_handle, "x0"), x0)
    mdl.set_property_value(mdl.prop(item_handle, "x1"), x1)
    mdl.set_property_value(mdl.prop(item_handle, "Frequency"), frequency)
    mdl.set_property_value(mdl.prop(item_handle, "basekv"), basekv)
    mdl.set_property_value(mdl.prop(item_handle, "Angle"), angle)
    mdl.set_property_value(mdl.prop(item_handle, "pu"), pu)

    mdl.set_property_value(mdl.prop(item_handle, "S_Ts"), s_ts)

    mdl.set_property_value(mdl.prop(item_handle, "T_lim_low"), t_lim_low)
    mdl.set_property_value(mdl.prop(item_handle, "T_lim_high"), t_lim_high)
    mdl.set_property_value(mdl.prop(item_handle, "Ts_switch"), ts_switch)
    mdl.set_property_value(mdl.prop(item_handle, "Slen"), slen)
    mdl.set_property_value(mdl.prop(item_handle, "T_Ts_internal"), t_ts_internal)


def topology_dynamics(mdl, mask_handle, prop_handle, new_value, old_value):
    comp_handle = mdl.get_parent(mask_handle)

    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"

    #
    # Get new property values to be applied
    # If multiple properties are changed, there is a temporary mismatch between
    # display values (the final values) and current values.
    #
    new_prop_values = {}
    current_pass_prop_values = {
        k: str(v) for k, v in mdl.get_property_values(comp_handle).items()
    }
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        if isinstance(mdl.get_property_disp_value(p), str):
            disp_str = str(mdl.get_property_disp_value(p))
            if "[" in disp_str and "]" in disp_str:
                disp_value = str(json.loads(disp_str))
            else:
                disp_value = disp_str
        else:
            disp_value = str(mdl.get_property_disp_value(p))
        new_prop_values[prop] = disp_value

    #
    # Topology dynamics need to be applied on multiline format
    #
    currently_sld = mdl.get_item("SLD1", parent=comp_handle, item_type="port")
    if currently_sld:
        # The terminal related to the current property hasn't been created yet
        modified_prop_values = dict(current_pass_prop_values)
        modified_prop_values[calling_prop_name] = old_value
        sld_info = get_sld_conversion_info(mdl, mask_handle, modified_prop_values)
        util.convert_to_multiline(mdl, mask_handle, sld_info)

    if new_prop_values.get("sld_mode") in (True, "True"):
        importlib.reload(util)
        sld_info = get_sld_conversion_info(mdl, mask_handle, current_pass_prop_values)
        util.convert_to_sld(mdl, mask_handle, sld_info)

    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    bus1 = mdl.get_item("SLD1_bus", parent=comp_handle)
    if bus1:
        bus1_size_prop = mdl.prop(bus1, "bus_size")
        mdl.set_property_value(bus1_size_prop, 4)
